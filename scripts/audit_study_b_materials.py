#!/usr/bin/env python
"""Offline manipulation-integrity audit for the Study B materials (SB-AUDIT).

Fully offline: no model API, no model SDK import, no network, no API key. Reads
the fixed stimulus file and checks that the 6 x 8 x 2 = 96 material grid is
complete and that each condition adds exactly its intended information unit.

Status per material is one of:
  - ``pass``          : deterministic checks all clear;
  - ``manual_review`` : a semantic question a keyword rule cannot settle, or a
                        symmetry threshold was tripped;
  - ``fail``          : a deterministic structural error (missing condition,
                        duplicate id, contradictory field, C4/C5 action wrong,
                        incomplete grid).

The audit never rewrites material text. Semantic uncertainty is flagged for a
human, not auto-fixed. Similarity is only a prompt for manual review.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import sys
from collections import Counter
from pathlib import Path

from public_json import dumps as public_dumps
from public_json import write as write_public_json

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STIMULI = (
    ROOT / "tasks" / "attribution_behavior" / "evaluations"
    / "pa_wu_r1_pilot" / "stimuli.jsonl"
)
AUDIT_CSV = ROOT / "research_packages" / "study_b" / "material_integrity_audit.csv"
SUMMARY_JSON = ROOT / "research_packages" / "study_b" / "material_integrity_summary.json"
REVIEW_MD = ROOT / "docs" / "reviews" / "study_b_material_integrity_review.md"
PAGE_SUMMARY_JSON = ROOT / "docs" / "pa-wu-r1-pilot" / "data" / "material_integrity_summary.json"

CONDITIONS = ["C0", "C1", "C2", "C3", "C4", "C5"]
DIRECTIONS = ["A", "B"]
EXPECTED_SCENARIOS = 8
EXPECTED_COUNT = len(CONDITIONS) * EXPECTED_SCENARIOS * len(DIRECTIONS)  # 96

# Deterministic structural markers (documented lexicon).
ALTERNATIVE_MARKER = "the available options were"
REASON_MARKER = "the stated reason was"
FEEDBACK_MARKER = "received this feedback"
KEPT_MARKER = "kept the original decision"
CHANGED_MARKER = "changed the original decision"
SECOND_DECISION_MARKER = "made a second decision"

SENTENCE_SPLIT = re.compile(r"[.!?]+")

# symmetry thresholds (trigger manual_review only, never fail)
CHAR_ABS_THRESHOLD = 30
CHAR_PCT_THRESHOLD = 0.15
SENTENCE_THRESHOLD = 1

# high-similarity threshold for cross-id duplicate prompts (manual_review)
SIMILARITY_THRESHOLD = 0.97


class AuditError(RuntimeError):
    """Raised when the stimulus source is missing or unreadable."""


def load_materials(path: Path) -> list[dict]:
    if not path.is_file():
        raise AuditError(f"stimulus file missing: {path}")
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _sentences(text: str) -> int:
    return len([s for s in SENTENCE_SPLIT.split(text or "") if s.strip()])


def _char_count(text: str) -> int:
    return len(re.sub(r"\s+", "", text or ""))


def _condition_structure_issues(mat: dict) -> tuple[list[str], list[str]]:
    """Return (fail_issues, review_issues) for a single material's condition."""
    cid = mat.get("condition_id")
    p1 = (mat.get("phase_1_text") or "").lower()
    p2 = (mat.get("phase_2_text") or "").lower()
    fb = (mat.get("feedback_text") or "").lower()
    fails: list[str] = []
    reviews: list[str] = []

    has_alt = ALTERNATIVE_MARKER in p1
    has_reason = REASON_MARKER in p1
    has_feedback = bool(fb.strip()) and FEEDBACK_MARKER in fb
    has_second = bool(p2.strip()) and SECOND_DECISION_MARKER in p2
    kept = KEPT_MARKER in p2
    changed = CHANGED_MARKER in p2

    if cid == "C0":
        if has_alt:
            fails.append("C0_has_alternatives")
        if has_reason:
            fails.append("C0_has_reason")
        if has_feedback:
            fails.append("C0_has_feedback")
        if has_second:
            fails.append("C0_has_second_decision")
    elif cid == "C1":
        if not has_alt:
            fails.append("C1_missing_alternatives")
        if has_reason:
            fails.append("C1_has_reason")
        if has_feedback:
            fails.append("C1_has_feedback")
        if has_second:
            fails.append("C1_has_second_decision")
    elif cid == "C2":
        if not has_reason:
            fails.append("C2_missing_reason")
        if has_feedback:
            fails.append("C2_has_feedback")
        if has_second:
            fails.append("C2_has_second_decision")
    elif cid == "C3":
        if not has_reason:
            fails.append("C3_missing_reason")
        if not has_feedback:
            fails.append("C3_missing_feedback")
        if has_second:
            fails.append("C3_has_second_decision")
    elif cid == "C4":
        if not has_reason:
            fails.append("C4_missing_reason")
        if not has_feedback:
            fails.append("C4_missing_feedback")
        if not has_second:
            fails.append("C4_missing_second_decision")
        if changed and not kept:
            fails.append("C4_changed_instead_of_kept")
        if not kept and not changed:
            reviews.append("C4_maintain_change_unclear")
    elif cid == "C5":
        if not has_reason:
            fails.append("C5_missing_reason")
        if not has_feedback:
            fails.append("C5_missing_feedback")
        if not has_second:
            fails.append("C5_missing_second_decision")
        if kept and not changed:
            fails.append("C5_kept_instead_of_changed")
        if not kept and not changed:
            reviews.append("C5_maintain_change_unclear")
    else:
        fails.append("unknown_condition_id")
    return fails, reviews


def _id_consistency_issues(mat: dict) -> list[str]:
    """Check that material_id encodes the same condition/scenario/direction as
    the structured fields."""
    fails = []
    mid = mat.get("material_id") or ""
    parts = mid.split("__")
    # expected: C?__<scenario>__<A|B>__<identity>
    if len(parts) != 4:
        fails.append("material_id_format")
        return fails
    cid, scenario, direction, _identity = parts
    if cid != mat.get("condition_id"):
        fails.append("id_condition_mismatch")
    if scenario != mat.get("scenario_id"):
        fails.append("id_scenario_mismatch")
    if direction != mat.get("direction_version"):
        fails.append("id_direction_mismatch")
    if mat.get("direction_version") not in DIRECTIONS:
        fails.append("invalid_direction")
    if mat.get("condition_id") not in CONDITIONS:
        fails.append("invalid_condition")
    return fails


def _leakage_issues(mat: dict) -> list[str]:
    """C0-C5 labels or scenario/direction ids leaking into the visible body."""
    reviews = []
    body = mat.get("complete_stimulus_text") or ""
    for token in CONDITIONS:
        if re.search(rf"\b{token}\b", body):
            reviews.append(f"label_leak_{token}")
    if mat.get("scenario_id") and mat.get("scenario_id") in body:
        reviews.append("scenario_id_leak")
    return reviews


def audit_materials(materials: list[dict]) -> tuple[list[dict], dict]:
    records = []
    id_counter = Counter(m.get("material_id") for m in materials)

    # grid completeness
    grid = {}
    for m in materials:
        key = (m.get("scenario_id"), m.get("direction_version"))
        grid.setdefault(key, set()).add(m.get("condition_id"))

    # direction symmetry: pair A/B within (condition, scenario)
    by_cond_scen: dict[tuple[str, str], dict[str, dict]] = {}
    for m in materials:
        by_cond_scen.setdefault(
            (m.get("condition_id"), m.get("scenario_id")), {}
        )[m.get("direction_version")] = m

    duplicate_pairs = []
    normalized = {m.get("material_id"): _normalize(m.get("complete_stimulus_text") or "")
                  for m in materials}
    ids_sorted = sorted(normalized)
    for i, a in enumerate(ids_sorted):
        for b in ids_sorted[i + 1:]:
            if normalized[a] == normalized[b]:
                duplicate_pairs.append((a, b, 1.0))
            else:
                ratio = difflib.SequenceMatcher(None, normalized[a], normalized[b]).ratio()
                if ratio >= SIMILARITY_THRESHOLD:
                    duplicate_pairs.append((a, b, round(ratio, 4)))
    high_similarity_ids = {a for a, _b, _r in duplicate_pairs} | {b for _a, b, _r in duplicate_pairs}
    exact_dup_ids = {a for a, _b, r in duplicate_pairs if r == 1.0} | {
        b for _a, b, r in duplicate_pairs if r == 1.0}

    symmetry_flags = 0
    for m in materials:
        fails: list[str] = []
        reviews: list[str] = []

        if id_counter[m.get("material_id")] > 1:
            fails.append("duplicate_material_id")
        fails += _id_consistency_issues(m)
        struct_fail, struct_review = _condition_structure_issues(m)
        fails += struct_fail
        reviews += struct_review
        reviews += _leakage_issues(m)
        if m.get("material_id") in exact_dup_ids:
            fails.append("duplicate_body_text")
        elif m.get("material_id") in high_similarity_ids:
            reviews.append("high_similarity_body")

        # direction symmetry vs the opposite direction in same condition+scenario
        pair = by_cond_scen.get((m.get("condition_id"), m.get("scenario_id")), {})
        other_dir = "B" if m.get("direction_version") == "A" else "A"
        other = pair.get(other_dir)
        if other is not None:
            sym = _symmetry_review(m, other)
            if sym:
                reviews.extend(sym)
                symmetry_flags += 1

        status = "fail" if fails else ("manual_review" if reviews else "pass")
        records.append({
            "material_id": m.get("material_id"),
            "condition_id": m.get("condition_id"),
            "scenario_id": m.get("scenario_id"),
            "direction_version": m.get("direction_version"),
            "char_count": _char_count(m.get("complete_stimulus_text")),
            "sentence_count": _sentences(m.get("complete_stimulus_text")),
            "status": status,
            "fail_issues": ";".join(sorted(fails)),
            "review_issues": ";".join(sorted(set(reviews))),
        })

    records.sort(key=lambda r: (r["condition_id"], r["scenario_id"], r["direction_version"]))

    complete_grid = all(
        set(conds) == set(CONDITIONS) for conds in grid.values()
    ) and len(grid) == EXPECTED_SCENARIOS * len(DIRECTIONS)

    issue_counter: Counter[str] = Counter()
    for rec in records:
        for token in rec["fail_issues"].split(";"):
            if token:
                issue_counter[token] += 1
        for token in rec["review_issues"].split(";"):
            if token:
                issue_counter[token] += 1

    structural_fail = sum(1 for r in records if r["status"] == "fail")
    structural_pass = sum(1 for r in records if r["status"] != "fail")
    field_consistency = not any("id_" in r["fail_issues"] or "material_id_format" in r["fail_issues"]
                                or "invalid_" in r["fail_issues"] for r in records)
    duplicate_id_count = sum(1 for r in records if "duplicate_material_id" in r["fail_issues"])

    summary = {
        "data_role": "study_b_material_integrity_audit",
        "material_count": len(materials),
        "expected_count": EXPECTED_COUNT,
        "complete_grid": bool(complete_grid),
        # Deterministic structural check: what code can settle without judgement.
        "deterministic_structure_check": {
            "expected_count": EXPECTED_COUNT,
            "actual_count": len(materials),
            "complete_grid": bool(complete_grid),
            "duplicate_id_count": duplicate_id_count,
            "structural_pass_count": structural_pass,
            "structural_fail_count": structural_fail,
            "field_consistency": bool(field_consistency),
            "direction_threshold_flags": symmetry_flags,
        },
        # Semantic review is a separate, human activity. A 0 threshold-flag count
        # does NOT mean no material needs semantic review; unless a human has
        # actually assessed all 96 materials, this stays not_assessed.
        "semantic_review": {
            "status": "not_assessed",
            "assessed_material_count": 0,
            "note": (
                "语义对称性、理由强度和反馈强度属于独立人工复核范围，本轮未纳入。"
                "阈值提示数量不等于语义复核项数量。"
            ),
        },
        "issue_type_counts": dict(sorted(issue_counter.items())),
        "direction_symmetry_summary": {
            "review_flag_count": symmetry_flags,
            "char_abs_threshold": CHAR_ABS_THRESHOLD,
            "char_pct_threshold": CHAR_PCT_THRESHOLD,
            "sentence_threshold": SENTENCE_THRESHOLD,
        },
        "duplicate_summary": {
            "exact_duplicate_count": len(exact_dup_ids),
            "high_similarity_pair_count": len(duplicate_pairs),
            "similarity_threshold": SIMILARITY_THRESHOLD,
        },
        "condition_delta_summary": _condition_delta_summary(by_cond_scen),
        "note": (
            "审计只标记问题，不修改材料正文。结构检查是确定性的；语义复核独立进行。"
            "相似度仅用于提示人工复核。"
        ),
    }
    return records, summary


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _symmetry_review(a: dict, b: dict) -> list[str]:
    reviews = []
    ca, cb = _char_count(a.get("complete_stimulus_text")), _char_count(b.get("complete_stimulus_text"))
    if abs(ca - cb) > max(CHAR_ABS_THRESHOLD, CHAR_PCT_THRESHOLD * max(ca, cb, 1)):
        reviews.append("symmetry_char_gap")
    sa, sb = _sentences(a.get("complete_stimulus_text")), _sentences(b.get("complete_stimulus_text"))
    if abs(sa - sb) > SENTENCE_THRESHOLD:
        reviews.append("symmetry_sentence_gap")
    # reason presence asymmetry
    ra = REASON_MARKER in (a.get("phase_1_text") or "").lower()
    rb = REASON_MARKER in (b.get("phase_1_text") or "").lower()
    if ra != rb:
        reviews.append("symmetry_reason_asymmetry")
    return reviews


DELTA_PAIRS = [
    ("C0", "C1", "add_alternatives"),
    ("C0", "C2", "add_reason"),
    ("C2", "C3", "add_feedback"),
    ("C2", "C4", "add_feedback_and_maintain"),
    ("C2", "C5", "add_feedback_and_change"),
    ("C4", "C5", "maintain_vs_change"),
]


def _condition_delta_summary(by_cond_scen: dict[tuple[str, str], dict[str, dict]]) -> list[dict]:
    scenarios = sorted({scen for (_c, scen) in by_cond_scen})
    out = []
    for left, right, expected in DELTA_PAIRS:
        added_chars = []
        removed_chars = []
        for scen in scenarios:
            for direction in DIRECTIONS:
                lm = by_cond_scen.get((left, scen), {}).get(direction)
                rm = by_cond_scen.get((right, scen), {}).get(direction)
                if not lm or not rm:
                    continue
                lc = _char_count(lm.get("complete_stimulus_text"))
                rc = _char_count(rm.get("complete_stimulus_text"))
                delta = rc - lc
                if delta >= 0:
                    added_chars.append(delta)
                else:
                    removed_chars.append(-delta)
        out.append({
            "from_condition": left,
            "to_condition": right,
            "expected_added_information": expected,
            "mean_added_chars": round(sum(added_chars) / len(added_chars), 2) if added_chars else 0.0,
            "mean_removed_chars": round(sum(removed_chars) / len(removed_chars), 2) if removed_chars else 0.0,
            "needs_manual_review": bool(removed_chars),
        })
    return out


# ---------------------------------------------------------------------------
# Report + outputs
# ---------------------------------------------------------------------------


def build_review_md(summary: dict) -> str:
    dsc = summary["deterministic_structure_check"]
    sem = summary["semantic_review"]
    lines = [
        "# 研究B材料操纵完整性审计", "",
        f"- 数据角色：`{summary['data_role']}`",
        f"- 材料数量：{summary['material_count']} / 期望 {summary['expected_count']}",
        f"- 完整网格（6条件 × 8场景 × 2方向）：{'是' if summary['complete_grid'] else '否'}",
        "",
        "## 确定性结构检查", "",
        f"- 期望数量：{dsc['expected_count']}；实际数量：{dsc['actual_count']}",
        f"- 完整网格：{'是' if dsc['complete_grid'] else '否'}",
        f"- 重复ID数量：{dsc['duplicate_id_count']}",
        f"- 结构通过：{dsc['structural_pass_count']}；结构错误：{dsc['structural_fail_count']}",
        f"- 字段一致性：{'是' if dsc['field_consistency'] else '否'}",
        f"- 方向阈值提示：{dsc['direction_threshold_flags']}",
        "",
        "## 语义复核", "",
        f"- 状态：`{sem['status']}`（已复核材料数：{sem['assessed_material_count']}）",
        f"- {sem['note']}",
        "",
        "本审计完全离线，未调用模型，不修改材料正文。结构检查是确定性的；"
        "语义对称性、理由强度和反馈强度属于独立人工复核范围。方向阈值提示数量不等于语义复核项数量。",
        "",
        "## 问题类型计数", "",
    ]
    if summary["issue_type_counts"]:
        lines += ["| 问题类型 | 数量 |", "|---|---:|"]
        for key, value in summary["issue_type_counts"].items():
            lines.append(f"| {key} | {value} |")
    else:
        lines.append("无确定性结构问题标记。")
    lines += ["", "## 方向对称性（仅触发人工复核，不判错）", "",
              f"- 触发人工复核的方向对数：{summary['direction_symmetry_summary']['review_flag_count']}",
              f"- 阈值：字符差 > max({CHAR_ABS_THRESHOLD}, {int(CHAR_PCT_THRESHOLD*100)}%)，句子差 > {SENTENCE_THRESHOLD}",
              "", "## 重复与相似", "",
              f"- 完全重复正文：{summary['duplicate_summary']['exact_duplicate_count']}",
              f"- 高相似对（阈值 {SIMILARITY_THRESHOLD}）：{summary['duplicate_summary']['high_similarity_pair_count']}",
              "", "## 条件差异审计（新增信息）", "",
              "| 从 | 到 | 预期新增 | 平均新增字符 | 平均删除字符 | 需人工确认 |",
              "|---|---|---|---:|---:|---|"]
    for row in summary["condition_delta_summary"]:
        lines.append(
            f"| {row['from_condition']} | {row['to_condition']} | "
            f"{row['expected_added_information']} | {row['mean_added_chars']} | "
            f"{row['mean_removed_chars']} | {row['needs_manual_review']} |"
        )
    lines.append("")
    return "\n".join(lines)


def _page_summary(summary: dict) -> dict:
    """Compact summary consumed by the Study B page (browser-safe)."""
    dsc = summary["deterministic_structure_check"]
    return {
        "data_role": summary["data_role"],
        "material_count": summary["material_count"],
        "expected_count": summary["expected_count"],
        "complete_grid": summary["complete_grid"],
        "structural_pass_count": dsc["structural_pass_count"],
        "structural_fail_count": dsc["structural_fail_count"],
        "direction_threshold_flags": dsc["direction_threshold_flags"],
        "semantic_review_status": summary["semantic_review"]["status"],
        "top_issue_types": [
            {"issue": key, "count": value}
            for key, value in list(summary["issue_type_counts"].items())[:5]
        ],
    }


def _csv_text(records: list[dict]) -> str:
    from io import StringIO

    buffer = StringIO()
    fieldnames = [
        "material_id", "condition_id", "scenario_id", "direction_version",
        "char_count", "sentence_count", "status", "fail_issues", "review_issues",
    ]
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for rec in records:
        writer.writerow(rec)
    return buffer.getvalue()


def _emit(records: list[dict], summary: dict) -> None:
    AUDIT_CSV.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_CSV.write_text(_csv_text(records), encoding="utf-8")
    write_public_json(SUMMARY_JSON, summary)
    REVIEW_MD.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_MD.write_text(build_review_md(summary), encoding="utf-8")
    write_public_json(PAGE_SUMMARY_JSON, _page_summary(summary))


def _check(records: list[dict], summary: dict) -> int:
    mismatched = []
    if not AUDIT_CSV.is_file() or AUDIT_CSV.read_text(encoding="utf-8") != _csv_text(records):
        mismatched.append(str(AUDIT_CSV))
    if not SUMMARY_JSON.is_file() or SUMMARY_JSON.read_text(encoding="utf-8") != public_dumps(summary):
        mismatched.append(str(SUMMARY_JSON))
    if not REVIEW_MD.is_file() or REVIEW_MD.read_text(encoding="utf-8") != build_review_md(summary):
        mismatched.append(str(REVIEW_MD))
    if not PAGE_SUMMARY_JSON.is_file() or PAGE_SUMMARY_JSON.read_text(encoding="utf-8") != public_dumps(_page_summary(summary)):
        mismatched.append(str(PAGE_SUMMARY_JSON))
    if mismatched:
        print("study B material audit outputs are OUT OF DATE: " + ", ".join(mismatched), file=sys.stderr)
        return 1
    print("study B material audit outputs are up to date")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline Study B material integrity audit.")
    parser.add_argument("--stimuli", default=str(DEFAULT_STIMULI))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    try:
        materials = load_materials(Path(args.stimuli).resolve())
        records, summary = audit_materials(materials)
    except AuditError as exc:
        print(f"audit_study_b_materials: ERROR: {exc}", file=sys.stderr)
        return 2

    if args.check:
        return _check(records, summary)

    _emit(records, summary)
    dsc = summary["deterministic_structure_check"]
    print(
        f"wrote study B material audit: {summary['material_count']} materials, "
        f"structural pass {dsc['structural_pass_count']} / fail {dsc['structural_fail_count']}, "
        f"direction threshold flags {dsc['direction_threshold_flags']}, "
        f"semantic_review={summary['semantic_review']['status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
