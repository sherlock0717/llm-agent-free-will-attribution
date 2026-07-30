#!/usr/bin/env python
"""Build Research A scenario-consistency summaries without changing historical outputs.

This is the canonical builder for the scenario-level analysis published on the
Research A page. It groups the existing DeepSeek responses into
``scenario × identity × process condition`` units and reports how each planned
contrast behaves across the eight scenarios.
"""

from __future__ import annotations

import argparse
import math
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from public_json import write as write_json

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "outputs" / "scale_scores.csv"
DEFAULT_OUTPUT = ROOT / "artifacts" / "research_a_scenario"
KEYS = ["scenario_id", "identity_label", "process_condition"]
CONSTRUCTS = [
    "factual_manipulation_check", "subjective_process_completeness", "agency",
    "free_will_attribution", "autonomy", "experience", "perceived_intelligence",
    "outcome_accountability", "moral_praise_blame", "process_accountability",
    "responsibility_total",
]
PUBLIC_CONSTRUCTS = [
    "subjective_process_completeness", "agency", "free_will_attribution",
    "perceived_intelligence", "responsibility_total",
]
CONTRASTS = [
    ("A1", "alternatives", "direct_choice", "候选方案线索"),
    ("A2", "reasons_concise", "direct_choice_long", "短理由结构与长背景文本"),
    ("A3", "reflection_feedback", "reasons", "反思反馈相对完整理由"),
    ("A4", "reflection_feedback", "direct_choice_long", "高结构过程与长文本直接选择"),
]


class AnalysisError(RuntimeError):
    pass


def load_scores(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise AnalysisError(f"source file missing: {path}")
    data = pd.read_csv(path)
    missing = [c for c in [*KEYS, *CONSTRUCTS] if c not in data.columns]
    if missing:
        raise AnalysisError("source data missing columns: " + ", ".join(missing))
    return data


def build_units(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for key, group in data.groupby(KEYS, dropna=False, sort=True):
        row = dict(zip(KEYS, key, strict=True))
        row["generation_count"] = len(group)
        for construct in CONSTRUCTS:
            values = pd.to_numeric(group[construct], errors="coerce").dropna()
            row[f"{construct}_mean"] = values.mean()
            row[f"{construct}_sd"] = values.std(ddof=1) if len(values) > 1 else math.nan
            row[f"{construct}_n"] = len(values)
        rows.append(row)
    units = pd.DataFrame(rows)
    expected = data.scenario_id.nunique() * data.identity_label.nunique() * data.process_condition.nunique()
    if len(units) != expected:
        raise AnalysisError(f"unit grid incomplete: expected {expected}, found {len(units)}")
    return units


def build_conditions(units: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for key, group in units.groupby(["identity_label", "process_condition"], sort=True):
        row = {"identity_label": key[0], "process_condition": key[1], "scenario_unit_count": group.scenario_id.nunique()}
        for construct in CONSTRUCTS:
            values = group[f"{construct}_mean"].dropna()
            row[f"{construct}_mean"] = values.mean()
            row[f"{construct}_scenario_sd"] = values.std(ddof=1) if len(values) > 1 else math.nan
        rows.append(row)
    return pd.DataFrame(rows)


def build_differences(units: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for construct in CONSTRUCTS:
        pivot = units.pivot(index=["scenario_id", "identity_label"], columns="process_condition", values=f"{construct}_mean")
        for cid, left, right, label in CONTRASTS:
            if left not in pivot or right not in pivot:
                raise AnalysisError(f"contrast {cid} missing source condition")
            for (scenario, identity), diff in (pivot[left] - pivot[right]).items():
                rows.append({"construct": construct, "contrast_id": cid, "contrast_label": label, "left_condition": left, "right_condition": right, "scenario_id": scenario, "identity_label": identity, "difference": diff})
    return pd.DataFrame(rows)


def summarize_group(group: pd.DataFrame, scope: str, identity: str | None) -> dict:
    values = group.difference.dropna()
    positive = int((values > 1e-12).sum())
    negative = int((values < -1e-12).sum())
    zero = len(values) - positive - negative
    nonzero = positive + negative
    loo = []
    for scenario in group.scenario_id.unique():
        retained = group.loc[group.scenario_id != scenario, "difference"].dropna()
        if len(retained):
            loo.append(retained.mean())
    scenario_means = group.groupby("scenario_id").difference.mean()
    first = group.iloc[0]
    return {
        "construct": first.construct, "contrast_id": first.contrast_id,
        "contrast_label": first.contrast_label, "scope": scope,
        "identity_label": identity, "matched_unit_count": len(values),
        "scenario_count": group.scenario_id.nunique(), "mean_difference": values.mean(),
        "median_difference": values.median(), "min_difference": values.min(),
        "max_difference": values.max(), "positive_count": positive,
        "negative_count": negative, "zero_count": zero,
        "direction_consistency": max(positive, negative) / nonzero if nonzero else 1.0,
        "scenario_mean_min": scenario_means.min(), "scenario_mean_max": scenario_means.max(),
        "leave_one_scenario_mean_min": min(loo) if loo else math.nan,
        "leave_one_scenario_mean_max": max(loo) if loo else math.nan,
    }


def build_contrasts(differences: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, group in differences.groupby(["construct", "contrast_id"], sort=False):
        rows.append(summarize_group(group, "all_identities", None))
        for identity, part in group.groupby("identity_label", sort=True):
            rows.append(summarize_group(part, "identity", str(identity)))
    return pd.DataFrame(rows)


def build_report(data: pd.DataFrame, units: pd.DataFrame, contrasts: pd.DataFrame) -> str:
    public = contrasts[(contrasts.construct.isin(PUBLIC_CONSTRUCTS)) & (contrasts.scope == "all_identities")]
    lines = [
        "# 研究A场景一致性分析：场景区组结果", "", "## 数据组成", "",
        f"- API模型模拟问卷响应：{len(data)}条", f"- 场景：{data.scenario_id.nunique()}",
        f"- 身份标签：{data.identity_label.nunique()}", f"- 过程条件：{data.process_condition.nunique()}",
        f"- 场景×身份×过程条件单元：{len(units)}", "", "## 主要比较", "",
        "| 构念 | 对比 | 平均差异 | 正向 | 负向 | 方向一致率 | 场景均值范围 | 留一场景范围 |",
        "|---|---|---:|---:|---:|---:|---|---|",
    ]
    for _, row in public.iterrows():
        lines.append(
            f"| {row.construct} | {row.contrast_id} | {row.mean_difference:.3f} | "
            f"{row.positive_count} | {row.negative_count} | {row.direction_consistency:.3f} | "
            f"[{row.scenario_mean_min:.3f}, {row.scenario_mean_max:.3f}] | "
            f"[{row.leave_one_scenario_mean_min:.3f}, {row.leave_one_scenario_mean_max:.3f}] |"
        )
    return "\n".join(lines) + "\n"


def build_public_payload(data: pd.DataFrame, units: pd.DataFrame,
                         contrasts: pd.DataFrame) -> dict:
    """Assemble the public summary object shared by the artifact JSON and the
    site/data JSON. ``generated_at`` is intentionally omitted so the published
    file is deterministic and does not create timestamp noise on each run."""
    public = contrasts[(contrasts.construct.isin(PUBLIC_CONSTRUCTS))
                       & (contrasts.scope == "all_identities")]
    return {
        "schema_version": 1,
        "study_id": "identity_process_attribution_baseline",
        "analysis_version": "research_a_scenario_block",
        "data_label_zh": "DeepSeek API模型模拟问卷响应",
        "analysis_unit": "scenario_id × identity_label × process_condition",
        "record_count": len(data),
        "unit_count": len(units),
        "scenario_count": data.scenario_id.nunique(),
        "identity_count": data.identity_label.nunique(),
        "condition_count": data.process_condition.nunique(),
        "public_constructs": PUBLIC_CONSTRUCTS,
        "contrasts": [{"id": cid, "label": label} for cid, _, _, label in CONTRASTS],
        "public_contrast_summary": public.to_dict(orient="records"),
    }


def run(input_path: Path, output: Path, public_json: Path | None = None) -> None:
    data = load_scores(input_path)
    units = build_units(data)
    conditions = build_conditions(units)
    differences = build_differences(units)
    contrasts = build_contrasts(differences)
    output.mkdir(parents=True, exist_ok=True)
    units.to_csv(output / "unit_summary.csv", index=False)
    conditions.to_csv(output / "condition_summary.csv", index=False)
    differences.to_csv(output / "contrast_unit_differences.csv", index=False)
    contrasts.to_csv(output / "contrast_summary.csv", index=False)
    payload = build_public_payload(data, units, contrasts)
    # artifact JSON keeps a run timestamp; the published site JSON stays stable.
    artifact_payload = {**payload,
                        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    write_json(output / "research_a_scenario_summary.json", artifact_payload)
    (output / "research_a_scenario_report.md").write_text(build_report(data, units, contrasts),
                                                          encoding="utf-8")
    if public_json is not None:
        public_json.parent.mkdir(parents=True, exist_ok=True)
        write_json(public_json, payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Research A scenario-consistency outputs.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--public-json", default=None,
                        help="also write a deterministic strict-JSON summary for the public site")
    args = parser.parse_args(argv)
    public_json = Path(args.public_json).resolve() if args.public_json else None
    try:
        run(Path(args.input).resolve(), Path(args.output).resolve(), public_json)
    except AnalysisError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
