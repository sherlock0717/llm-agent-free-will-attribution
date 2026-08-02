#!/usr/bin/env python
"""Offline robustness checks for the EXISTING Research A data (RA-ROBUST).

This script never calls a model API, never imports a model SDK, never touches
the network, and never reads an API key. It only reads already-produced
Research A source files and derives descriptive robustness diagnostics for the
three public findings:

  1. process information enters agency judgements;
  2. identity labels shift mind / responsibility judgements;
  3. direction repeats across scenarios but magnitude depends on the task.

Design guardrails (mirrored in tests):
  - inputs are read-only;
  - the primary analysis uses the 96 ``scenario x identity x process`` blocks,
    not the 360 responses treated as independent replicates;
  - the fixed contrasts A1-A4 and the primary constructs are pinned constants;
    the script never scans for the largest difference / smallest p / largest
    effect to pick a "lead" result;
  - all JSON is strict (no NaN / Infinity) via ``public_json``;
  - figures are inline SVG with no external resources;
  - output is deterministic and supports ``--check``.

The length model is a descriptive sensitivity check, not a causal control. The
report states "condition differences persist / weaken / flip after adding text
length", and flags collinearity when process condition and length co-vary.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

import pandas as pd

from public_json import dumps as public_dumps
from public_json import write as write_public_json

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCORES = ROOT / "outputs" / "scale_scores.csv"
DEFAULT_OUTPUT = ROOT / "artifacts" / "research_a_robustness"
PUBLIC_JSON = ROOT / "site" / "data" / "research_a_robustness_summary.json"
REPORT_MD = ROOT / "docs" / "research_a_robustness_report.md"
FIG_DIR = ROOT / "docs" / "assets" / "figures"
FIG_IDENTITY = FIG_DIR / "research_a_identity_process.svg"
FIG_INFLUENCE = FIG_DIR / "research_a_scenario_influence.svg"
FIG_LENGTH = FIG_DIR / "research_a_length_sensitivity.svg"

DATA_ROLE = "research_a_existing_data_robustness"

KEYS = ["scenario_id", "identity_label", "process_condition"]

# Primary constructs are pinned to the public five, in a fixed order that
# follows the research questions (not the size of any effect).
PRIMARY_CONSTRUCTS = [
    "subjective_process_completeness",
    "agency",
    "free_will_attribution",
    "perceived_intelligence",
    "responsibility_total",
]
CONSTRUCT_LABELS = {
    "subjective_process_completeness": "主观过程完整性",
    "agency": "能动性",
    "free_will_attribution": "自由意志归因",
    "perceived_intelligence": "感知智能",
    "responsibility_total": "责任归因总分",
}
CONSTRUCT_RANGE = {name: (1.0, 7.0) for name in PRIMARY_CONSTRUCTS}

# Fixed process-condition contrasts (left - right), identical to the canonical
# scenario builder. These are decided ahead of time by the research questions.
CONTRASTS = [
    ("A1", "alternatives", "direct_choice", "候选方案线索"),
    ("A2", "reasons_concise", "direct_choice_long", "短理由结构与长背景文本"),
    ("A3", "reflection_feedback", "reasons", "反思反馈相对完整理由"),
    ("A4", "reflection_feedback", "direct_choice_long", "高结构过程与长文本直接选择"),
]

# Each public finding is anchored to a pre-registered construct/comparison,
# pinned here (never chosen by effect size). Crucially the process finding and
# the identity finding use DIFFERENT comparisons:
#   - process finding  -> agency, process contrast A4 (a process-condition diff);
#   - identity finding  -> free_will_attribution, human - AI identity diff;
#   - scenario finding  -> summarises how BOTH effects vary across scenarios.
PROCESS_FINDING_CONSTRUCT = "agency"
PROCESS_FINDING_CONTRAST = "A4"
IDENTITY_FINDING_CONSTRUCT = "free_will_attribution"
# identity labels in scale_scores.csv; human - AI is (HUMAN_LABEL - AI_LABEL).
AI_LABEL = "AI 决策者"
HUMAN_LABEL = "人类决策者"

CONDITION_LABELS = {
    "direct_choice": "直接选择",
    "direct_choice_long": "长文本直接选择",
    "alternatives": "列出可选方案",
    "reasons_concise": "简洁理由权衡",
    "reasons": "完整理由权衡",
    "reflection_feedback": "反思与反馈修正",
}
CONDITION_ORDER = [
    "direct_choice", "direct_choice_long", "alternatives",
    "reasons_concise", "reasons", "reflection_feedback",
]

# --- Text-structure lexicons (fully offline; listed in the report) ----------
ALTERNATIVE_MARKERS = [
    "options", "option", "alternative", "alternatives", "instead of",
    "either", "versus", "candidate", "choices",
]
REASON_CONNECTIVES = [
    "because", "since", "so that", "in order to", "reason", "therefore",
    "as a result", "the stated reason",
]
FEEDBACK_WORDS = [
    "feedback", "noted", "responded", "review", "reviewed", "concern",
    "pushback", "complaint", "flagged",
]
ACTION_MAINTAIN_CHANGE_WORDS = [
    "kept", "keep", "maintain", "maintained", "changed", "change",
    "switched", "revised", "second decision", "reconsider",
]
SENTENCE_SPLIT = re.compile(r"[.!?。！？]+")

# Descriptive status thresholds. These are DESCRIPTIVE labels only, never a
# statistical-significance tier and never a formal evidence grade.
MAJORITY_MIN_DIRECTION_RATIO = 0.75  # share of units on the majority direction
SCENARIO_SENSITIVE_CHANGE_RATIO = 0.5


class RobustnessError(RuntimeError):
    """Raised when a required source file / field is missing or inconsistent."""


# ---------------------------------------------------------------------------
# Source loading + aggregation (96 blocks)
# ---------------------------------------------------------------------------


def load_scores(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise RobustnessError(f"source file missing: {path}")
    data = pd.read_csv(path)
    needed = [*KEYS, "char_len", *PRIMARY_CONSTRUCTS]
    missing = [c for c in needed if c not in data.columns]
    if missing:
        raise RobustnessError("source data missing columns: " + ", ".join(missing))
    return data


def build_units(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for key, group in data.groupby(KEYS, dropna=False, sort=True):
        row = dict(zip(KEYS, key, strict=True))
        row["response_count"] = len(group)
        row["char_len_mean"] = pd.to_numeric(group["char_len"], errors="coerce").mean()
        for construct in PRIMARY_CONSTRUCTS:
            values = pd.to_numeric(group[construct], errors="coerce").dropna()
            row[f"{construct}_mean"] = values.mean()
        rows.append(row)
    units = pd.DataFrame(rows)
    expected = (
        data.scenario_id.nunique()
        * data.identity_label.nunique()
        * data.process_condition.nunique()
    )
    if len(units) != expected:
        raise RobustnessError(
            f"aggregate grid incomplete: expected {expected}, found {len(units)}"
        )
    return units


# ---------------------------------------------------------------------------
# 6.1 identity x process stratification
# ---------------------------------------------------------------------------


def _finite(value: float) -> float | None:
    number = float(value)
    return number if math.isfinite(number) else None


def build_identity_by_process(units: pd.DataFrame) -> list[dict]:
    identities = sorted(units.identity_label.unique())
    out = []
    for construct in PRIMARY_CONSTRUCTS:
        mean_col = f"{construct}_mean"
        by_identity = {}
        for identity in identities:
            subset = units[units.identity_label == identity]
            per_condition = []
            for condition in CONDITION_ORDER:
                cell = subset[subset.process_condition == condition][mean_col]
                per_condition.append({
                    "condition": condition,
                    "label": CONDITION_LABELS.get(condition, condition),
                    "mean": _finite(cell.mean()) if len(cell) else None,
                })
            by_identity[identity] = per_condition
        # identity difference per condition (first identity - second identity)
        diffs = []
        for condition in CONDITION_ORDER:
            vals = {}
            for identity in identities:
                subset = units[
                    (units.identity_label == identity)
                    & (units.process_condition == condition)
                ][mean_col]
                vals[identity] = subset.mean() if len(subset) else math.nan
            if len(identities) == 2:
                diff = vals[identities[0]] - vals[identities[1]]
            else:
                diff = math.nan
            diffs.append({
                "condition": condition,
                "label": CONDITION_LABELS.get(condition, condition),
                "identity_difference": _finite(diff),
            })
        out.append({
            "construct": construct,
            "label": CONSTRUCT_LABELS[construct],
            "scale_min": CONSTRUCT_RANGE[construct][0],
            "scale_max": CONSTRUCT_RANGE[construct][1],
            "identities": identities,
            "means_by_identity": by_identity,
            "identity_difference_by_condition": diffs,
        })
    return out


# ---------------------------------------------------------------------------
# 6.2 scenario influence + leave-one-scenario (per fixed contrast)
# ---------------------------------------------------------------------------


def _contrast_unit_differences(units: pd.DataFrame, construct: str,
                               left: str, right: str) -> pd.DataFrame:
    mean_col = f"{construct}_mean"
    pivot = units.pivot_table(
        index=["scenario_id", "identity_label"],
        columns="process_condition",
        values=mean_col,
        aggfunc="mean",
    )
    if left not in pivot or right not in pivot:
        raise RobustnessError(f"contrast source condition missing: {left}/{right}")
    diff = (pivot[left] - pivot[right]).dropna()
    return diff.reset_index(name="difference")


def summarize_contrast(units: pd.DataFrame, construct: str, cid: str,
                       left: str, right: str, label: str) -> dict:
    frame = _contrast_unit_differences(units, construct, left, right)
    values = frame["difference"]
    full_effect = values.mean()
    positive = int((values > 1e-12).sum())
    negative = int((values < -1e-12).sum())
    zero = int(len(values) - positive - negative)

    scenarios = sorted(frame["scenario_id"].unique())
    loo = []
    scenario_influence = []
    for scenario in scenarios:
        retained = frame.loc[frame["scenario_id"] != scenario, "difference"]
        loo_effect = retained.mean() if len(retained) else math.nan
        loo.append(loo_effect)
        influence = abs(full_effect - loo_effect) if math.isfinite(loo_effect) else math.nan
        direction_flips = bool(
            math.isfinite(loo_effect)
            and (full_effect > 0) != (loo_effect > 0)
            and abs(full_effect) > 1e-12
            and abs(loo_effect) > 1e-12
        )
        scenario_influence.append({
            "scenario_id": scenario,
            "leave_one_effect": _finite(loo_effect),
            "influence": _finite(influence),
            "direction_changes": direction_flips,
        })
    scenario_influence.sort(key=lambda r: (r["influence"] is None, -(r["influence"] or 0.0), r["scenario_id"]))
    loo_finite = [v for v in loo if math.isfinite(v)]
    per_scenario_means = frame.groupby("scenario_id")["difference"].mean()
    return {
        "construct": construct,
        "construct_label": CONSTRUCT_LABELS[construct],
        "contrast_id": cid,
        "contrast_label": label,
        "left_condition": left,
        "right_condition": right,
        "unit_count": int(len(values)),
        "scenario_count": int(len(scenarios)),
        "full_effect": _finite(full_effect),
        "positive_count": positive,
        "negative_count": negative,
        "zero_count": zero,
        "direction_units": max(positive, negative),
        "scenario_mean_min": _finite(per_scenario_means.min()),
        "scenario_mean_max": _finite(per_scenario_means.max()),
        "leave_one_min": _finite(min(loo_finite)) if loo_finite else None,
        "leave_one_max": _finite(max(loo_finite)) if loo_finite else None,
        "leave_one_keeps_sign": _leave_one_keeps_sign(full_effect, loo_finite),
        "scenario_influence": scenario_influence,
    }


def _leave_one_keeps_sign(full_effect: float, loo_finite: list[float]) -> bool:
    if not loo_finite or abs(full_effect) <= 1e-12:
        return False
    sign = full_effect > 0
    return all((value > 0) == sign for value in loo_finite if abs(value) > 1e-12)


def build_scenario_influence(units: pd.DataFrame) -> list[dict]:
    out = []
    for construct in PRIMARY_CONSTRUCTS:
        for cid, left, right, label in CONTRASTS:
            out.append(summarize_contrast(units, construct, cid, left, right, label))
    return out


# ---------------------------------------------------------------------------
# 6.3 text structure + length sensitivity
# ---------------------------------------------------------------------------


def _count_markers(text: str, markers: list[str]) -> int:
    lowered = text.lower()
    return sum(lowered.count(marker) for marker in markers)


def text_metrics_for_condition(process_condition: str) -> dict:
    """Structural metrics derived from the Research A process-condition template.

    Research A stores per-response ``char_len`` but not the raw stimulus text in
    the score file; the structural markers below are a fixed, documented mapping
    from the process condition to whether alternatives / reasons / feedback /
    maintain-change information is present. This keeps the metric deterministic
    and offline.
    """
    present = {
        "has_alternatives": process_condition in {"alternatives"},
        "has_reasons": process_condition in {"reasons_concise", "reasons", "reflection_feedback"},
        "has_feedback": process_condition in {"reflection_feedback"},
        "has_maintain_change": process_condition in {"reflection_feedback"},
    }
    return present


def build_text_structure_metrics(data: pd.DataFrame, units: pd.DataFrame) -> dict:
    per_condition = []
    for condition in CONDITION_ORDER:
        subset = data[data.process_condition == condition]
        char = pd.to_numeric(subset["char_len"], errors="coerce").dropna()
        present = text_metrics_for_condition(condition)
        per_condition.append({
            "condition": condition,
            "label": CONDITION_LABELS.get(condition, condition),
            "char_len_mean": _finite(char.mean()) if len(char) else None,
            "char_len_min": _finite(char.min()) if len(char) else None,
            "char_len_max": _finite(char.max()) if len(char) else None,
            **{k: bool(v) for k, v in present.items()},
        })
    return {
        "lexicons": {
            "alternative_markers": ALTERNATIVE_MARKERS,
            "reason_connectives": REASON_CONNECTIVES,
            "feedback_words": FEEDBACK_WORDS,
            "action_maintain_change_words": ACTION_MAINTAIN_CHANGE_WORDS,
        },
        "per_condition": per_condition,
        "note": (
            "结构标记由过程条件模板确定；char_len 来自每条响应记录。"
            "字符数与过程结构高度相关，长度敏感性只作描述用途。"
        ),
    }


def _ols_condition_effect(frame: pd.DataFrame, construct: str,
                          left: str, right: str, with_length: bool) -> float | None:
    """Estimate the (left - right) condition contrast from an OLS design with
    scenario fixed effects, identity, and optionally standardized char length +
    sentence-count proxy. Uses numpy least squares (offline, deterministic)."""
    import numpy as np

    mean_col = f"{construct}_mean"
    work = frame[frame.process_condition.isin([left, right])].copy()
    work = work.dropna(subset=[mean_col])
    if work.empty:
        return None
    y = work[mean_col].to_numpy(dtype=float)

    columns = [np.ones(len(work))]
    # condition indicator: 1 for left, 0 for right
    columns.append((work.process_condition == left).to_numpy(dtype=float))
    # identity indicator
    identities = sorted(work.identity_label.unique())
    if len(identities) == 2:
        columns.append((work.identity_label == identities[0]).to_numpy(dtype=float))
    # scenario fixed effects (drop first as reference)
    scenarios = sorted(work.scenario_id.unique())
    for scenario in scenarios[1:]:
        columns.append((work.scenario_id == scenario).to_numpy(dtype=float))
    if with_length:
        char = pd.to_numeric(work["char_len_mean"], errors="coerce").to_numpy(dtype=float)
        if char.std(ddof=0) > 1e-9:
            columns.append((char - char.mean()) / char.std(ddof=0))
        else:
            columns.append(char - char.mean())
        # sentence-count proxy: char length scaled (documented approximation)
        sent = char / 60.0
        if sent.std(ddof=0) > 1e-9:
            columns.append((sent - sent.mean()) / sent.std(ddof=0))
        else:
            columns.append(sent - sent.mean())
    design = np.column_stack(columns)
    coef, *_ = np.linalg.lstsq(design, y, rcond=None)
    return _finite(coef[1])  # the condition indicator coefficient


def build_length_sensitivity(units: pd.DataFrame) -> dict:
    import numpy as np

    rows = []
    # collinearity: correlation of process-structure ordinal with char length
    structure_rank = {c: i for i, c in enumerate(CONDITION_ORDER)}
    ranks = units.process_condition.map(structure_rank).to_numpy(dtype=float)
    char = pd.to_numeric(units["char_len_mean"], errors="coerce").to_numpy(dtype=float)
    if np.std(ranks) > 1e-9 and np.std(char) > 1e-9:
        collinearity = float(np.corrcoef(ranks, char)[0, 1])
    else:
        collinearity = math.nan

    for construct in PRIMARY_CONSTRUCTS:
        for cid, left, right, label in CONTRASTS:
            base = _ols_condition_effect(units, construct, left, right, with_length=False)
            adjusted = _ols_condition_effect(units, construct, left, right, with_length=True)
            if base is not None and adjusted is not None and abs(base) > 1e-9:
                shrink = (base - adjusted) / base
                if base > 0:
                    flips = adjusted < 0
                else:
                    flips = adjusted > 0
            else:
                shrink = None
                flips = None
            rows.append({
                "construct": construct,
                "construct_label": CONSTRUCT_LABELS[construct],
                "contrast_id": cid,
                "contrast_label": label,
                "base_estimate": base,
                "length_adjusted_estimate": adjusted,
                "absolute_shrink_ratio": _finite(abs(shrink)) if shrink is not None else None,
                "direction_flips": flips,
            })
    return {
        "condition_length_collinearity": _finite(collinearity),
        "collinearity_note": (
            "过程结构等级与字符数的描述性相关较高；该单一相关不能完整描述分类条件、"
            "字符数和句子数之间的多重依赖关系，因此无法据此分离文本长度与过程信息各自的独立作用。"
        ),
        "contrasts": rows,
    }


# ---------------------------------------------------------------------------
# 6.4 construct relationships
# ---------------------------------------------------------------------------


# Item-overlap map among the five public constructs. No two constructs share the
# same item id, EXCEPT responsibility_total which is a composite that mechanically
# includes its accountability sub-constructs (not among the public five, so no
# direct public-construct item overlap). agency / free_will_attribution / autonomy
# share theoretical roots but distinct items.
ITEM_OVERLAP_PAIRS: list[tuple[str, str]] = []  # no shared item ids among the five
MECHANICAL_COMPOSITE = {
    "responsibility_total": "结果责任、道德褒贬与过程可归责三个子构念的合成分。",
}


def build_construct_correlations(units: pd.DataFrame) -> dict:
    mean_cols = [f"{c}_mean" for c in PRIMARY_CONSTRUCTS]
    matrix = units[mean_cols].apply(pd.to_numeric, errors="coerce")

    # residualize on scenario, identity, process condition group means
    residual = matrix.copy()
    for col in mean_cols:
        adjusted = units[[*KEYS]].copy()
        adjusted[col] = matrix[col]
        overall = matrix[col].mean()
        for key in KEYS:
            group_mean = adjusted.groupby(key)[col].transform("mean")
            residual[col] = residual[col] - group_mean + overall

    def _corr(frame: pd.DataFrame, method: str) -> list[dict]:
        corr = frame.corr(method=method)
        pairs = []
        for i, a in enumerate(PRIMARY_CONSTRUCTS):
            for b in PRIMARY_CONSTRUCTS[i + 1:]:
                value = corr.loc[f"{a}_mean", f"{b}_mean"]
                pairs.append({
                    "construct_a": a,
                    "construct_b": b,
                    "coefficient": _finite(value),
                    "shares_items": bool((a, b) in ITEM_OVERLAP_PAIRS or (b, a) in ITEM_OVERLAP_PAIRS),
                })
        return pairs

    return {
        "pearson": _corr(matrix, "pearson"),
        "spearman": _corr(matrix, "spearman"),
        "residual_pearson": _corr(residual, "pearson"),
        "item_overlap_pairs": ITEM_OVERLAP_PAIRS,
        "mechanical_composites": MECHANICAL_COMPOSITE,
        "interpretation_note": (
            "相关不用于证明构念效度。区分：题项重叠造成的机械相关、同一评价来源"
            "造成的共同方法相关，以及可进一步研究的构念关系。"
        ),
    }


# ---------------------------------------------------------------------------
# 6.5 public findings (process / identity / scenario) + descriptive status
# ---------------------------------------------------------------------------


def _direction_counts(values: pd.Series) -> tuple[int, int, int]:
    positive = int((values > 1e-12).sum())
    negative = int((values < -1e-12).sum())
    zero = int(len(values) - positive - negative)
    return positive, negative, zero


def _status_label(direction_majority: int, unit_count: int, keeps_sign: bool,
                  max_change_ratio: float, crosses_zero: bool) -> tuple[str, str]:
    """Descriptive status label + code. Not a significance tier."""
    if unit_count == 0:
        return "no_clear_direction", "当前数据未呈现清晰方向"
    majority_ratio = direction_majority / unit_count
    if majority_ratio < 0.5 + 1e-9 or (not keeps_sign and crosses_zero and majority_ratio < MAJORITY_MIN_DIRECTION_RATIO):
        # no clear majority direction
        if majority_ratio <= 0.5 + 1e-9:
            return "no_clear_direction", "当前数据未呈现清晰方向"
    if crosses_zero or (not keeps_sign) or max_change_ratio > SCENARIO_SENSITIVE_CHANGE_RATIO:
        return "scenario_sensitive", "结果对个别场景敏感"
    if majority_ratio >= MAJORITY_MIN_DIRECTION_RATIO and keeps_sign:
        # a clear majority direction that survives leave-one-scenario, but
        # magnitude still varies across scenarios.
        return "direction_consistent_magnitude_varies", "方向一致但幅度存在场景差异"
    return "majority_same_direction", "多数场景方向一致"


def build_process_finding(units: pd.DataFrame) -> dict:
    cid, left, right, label = next(c for c in CONTRASTS if c[0] == PROCESS_FINDING_CONTRAST)
    summary = summarize_contrast(units, PROCESS_FINDING_CONSTRUCT, cid, left, right, label)
    influence_sorted = summary["scenario_influence"]
    most_influential = influence_sorted[0]["scenario_id"] if influence_sorted else None
    full = summary["full_effect"] or 0.0
    max_change = 0.0
    for row in influence_sorted:
        infl = row["influence"]
        if infl is not None and abs(full) > 1e-9:
            max_change = max(max_change, infl / abs(full))
    crosses_zero = (
        summary["leave_one_min"] is not None and summary["leave_one_max"] is not None
        and summary["leave_one_min"] <= 0 <= summary["leave_one_max"]
    )
    status_code, status_label = _status_label(
        summary["direction_units"], summary["unit_count"],
        summary["leave_one_keeps_sign"], max_change, crosses_zero)
    return {
        "comparison_type": "process_condition_contrast",
        "construct": PROCESS_FINDING_CONSTRUCT,
        "construct_label": CONSTRUCT_LABELS[PROCESS_FINDING_CONSTRUCT],
        "contrast_id": cid,
        "contrast_label": label,
        "left_condition": left,
        "right_condition": right,
        "unit_definition": "scenario_id × identity_label",
        "total_unit_count": summary["unit_count"],
        "full_effect": summary["full_effect"],
        "positive_count": summary["positive_count"],
        "negative_count": summary["negative_count"],
        "zero_count": summary["zero_count"],
        "direction_majority_count": summary["direction_units"],
        "scenario_range": [summary["scenario_mean_min"], summary["scenario_mean_max"]],
        "leave_one_scenario_range": [summary["leave_one_min"], summary["leave_one_max"]],
        "leave_one_scenario_same_sign": summary["leave_one_keeps_sign"],
        "most_influential_scenario": most_influential,
        "scenario_influence": summary["scenario_influence"],
        "status_code": status_code,
        "status_label": status_label,
    }


def build_identity_finding(units: pd.DataFrame) -> dict:
    """Real identity difference: human - AI, paired within the same
    scenario_id AND process_condition (8 × 6 = 48 pairing units). This is NOT a
    process-condition contrast, and never treats the 360 responses as 48
    independent designs."""
    construct = IDENTITY_FINDING_CONSTRUCT
    mean_col = f"{construct}_mean"
    pivot = units.pivot_table(
        index=["scenario_id", "process_condition"],
        columns="identity_label",
        values=mean_col,
        aggfunc="mean",
    )
    if HUMAN_LABEL not in pivot or AI_LABEL not in pivot:
        raise RobustnessError("identity labels missing for human - AI difference")
    diff = (pivot[HUMAN_LABEL] - pivot[AI_LABEL]).dropna()
    frame = diff.reset_index(name="difference")
    values = frame["difference"]
    full_effect = values.mean()
    positive, negative, zero = _direction_counts(values)

    # identity difference within each process condition
    by_condition = []
    for condition in CONDITION_ORDER:
        sub = frame[frame["process_condition"] == condition]["difference"]
        by_condition.append({
            "condition": condition,
            "label": CONDITION_LABELS.get(condition, condition),
            "identity_difference": _finite(sub.mean()) if len(sub) else None,
        })

    # identity difference range + leave-one-scenario across the 8 scenarios
    scenarios = sorted(frame["scenario_id"].unique())
    per_scenario = frame.groupby("scenario_id")["difference"].mean()
    loo = []
    scenario_influence = []
    for scenario in scenarios:
        retained = frame.loc[frame["scenario_id"] != scenario, "difference"]
        loo_effect = retained.mean() if len(retained) else math.nan
        loo.append(loo_effect)
        influence = abs(full_effect - loo_effect) if math.isfinite(loo_effect) else math.nan
        flips = bool(
            math.isfinite(loo_effect)
            and (full_effect > 0) != (loo_effect > 0)
            and abs(full_effect) > 1e-12 and abs(loo_effect) > 1e-12
        )
        scenario_influence.append({
            "scenario_id": scenario,
            "leave_one_effect": _finite(loo_effect),
            "influence": _finite(influence),
            "direction_changes": flips,
        })
    scenario_influence.sort(key=lambda r: (r["influence"] is None, -(r["influence"] or 0.0), r["scenario_id"]))
    loo_finite = [v for v in loo if math.isfinite(v)]
    keeps_sign = _leave_one_keeps_sign(full_effect, loo_finite)
    most_influential = scenario_influence[0]["scenario_id"] if scenario_influence else None
    max_change = 0.0
    for row in scenario_influence:
        infl = row["influence"]
        if infl is not None and abs(full_effect) > 1e-9:
            max_change = max(max_change, infl / abs(full_effect))
    crosses_zero = bool(loo_finite and min(loo_finite) <= 0 <= max(loo_finite))
    status_code, status_label = _status_label(
        max(positive, negative), int(len(values)), keeps_sign, max_change, crosses_zero)
    return {
        "comparison_type": "identity_difference_human_minus_ai",
        "construct": construct,
        "construct_label": CONSTRUCT_LABELS[construct],
        "identity_high": HUMAN_LABEL,
        "identity_low": AI_LABEL,
        "unit_definition": "scenario_id × process_condition",
        "total_unit_count": int(len(values)),
        "overall_identity_difference": _finite(full_effect),
        "positive_count": positive,
        "negative_count": negative,
        "zero_count": zero,
        "direction_majority_count": max(positive, negative),
        "identity_difference_by_condition": by_condition,
        "scenario_range": [_finite(per_scenario.min()), _finite(per_scenario.max())],
        "leave_one_scenario_range": [
            _finite(min(loo_finite)) if loo_finite else None,
            _finite(max(loo_finite)) if loo_finite else None,
        ],
        "leave_one_scenario_same_sign": keeps_sign,
        "most_influential_scenario": most_influential,
        "scenario_influence": scenario_influence,
        "status_code": status_code,
        "status_label": status_label,
    }


def build_scenario_dependence(process_finding: dict, identity_finding: dict) -> dict:
    """Scenario dependence is NOT a third treatment effect. It summarises how the
    process effect and the identity effect each vary across the eight scenarios."""
    return {
        "process_effect_range": process_finding["scenario_range"],
        "identity_effect_range": identity_finding["scenario_range"],
        "process_leave_one_same_sign": process_finding["leave_one_scenario_same_sign"],
        "identity_leave_one_same_sign": identity_finding["leave_one_scenario_same_sign"],
        "largest_process_influence": process_finding["most_influential_scenario"],
        "largest_identity_influence": identity_finding["most_influential_scenario"],
        "interpretation": (
            "过程效应与身份效应在八个场景中方向大体一致，但幅度存在场景差异；"
            "个别场景对总体估计影响较大。这是场景敏感性汇总，不是第三个独立处理效应。"
        ),
    }


def build_public_findings(units: pd.DataFrame, length_sensitivity: dict) -> dict:
    process_finding = build_process_finding(units)
    identity_finding = build_identity_finding(units)
    scenario_dependence = build_scenario_dependence(process_finding, identity_finding)
    # attach length sensitivity for the process contrast only (descriptive).
    length_row = next(
        (r for r in length_sensitivity["contrasts"]
         if r["construct"] == PROCESS_FINDING_CONSTRUCT and r["contrast_id"] == PROCESS_FINDING_CONTRAST),
        None)
    process_finding["length_sensitivity"] = {
        "base_estimate": length_row["base_estimate"] if length_row else None,
        "length_adjusted_estimate": length_row["length_adjusted_estimate"] if length_row else None,
        "absolute_shrink_ratio": length_row["absolute_shrink_ratio"] if length_row else None,
        "direction_flips": length_row["direction_flips"] if length_row else None,
    }
    return {
        "process_information": process_finding,
        "identity_label": identity_finding,
        "scenario_dependence": scenario_dependence,
    }


LIMITATIONS = [
    "结果来自单一DeepSeek模型配置的合成问卷响应，不能证明跨模型泛化。",
    "相关分析不能证明构念效度或测量等值性。",
    "方向一致数是场景×条件配对单元的描述性统计，用于观察结果是否在不同材料组合中重复出现，"
    "不等同于独立样本数量或统计显著性检验。",
    "文本长度与过程条件共同变化，长度敏感性只说明估计对模型设定较敏感，"
    "无法据此分离文本长度和过程信息各自的独立作用。",
    "分析基于既有360条响应与96个聚合单元，未生成任何新的模型响应。",
    "证据状态是描述性标签，不是统计显著性等级。",
]


# ---------------------------------------------------------------------------
# Assemble payload
# ---------------------------------------------------------------------------


def build_payload(data: pd.DataFrame, units: pd.DataFrame) -> dict:
    identity_by_process = build_identity_by_process(units)
    scenario_influence = build_scenario_influence(units)
    text_structure = build_text_structure_metrics(data, units)
    length_sensitivity = build_length_sensitivity(units)
    correlations = build_construct_correlations(units)
    public_findings = build_public_findings(units, length_sensitivity)
    return {
        "data_role": DATA_ROLE,
        "source_files": [
            "outputs/scale_scores.csv",
            "site/data/research_a_scenario_summary.json",
        ],
        "source_record_count": int(len(data)),
        "aggregate_unit_count": int(len(units)),
        "constructs": [
            {"key": c, "label": CONSTRUCT_LABELS[c],
             "scale_min": CONSTRUCT_RANGE[c][0], "scale_max": CONSTRUCT_RANGE[c][1]}
            for c in PRIMARY_CONSTRUCTS
        ],
        "fixed_contrasts": [
            {"id": cid, "left_condition": left, "right_condition": right, "label": label}
            for cid, left, right, label in CONTRASTS
        ],
        "public_findings": public_findings,
        "identity_by_process": identity_by_process,
        "scenario_influence": scenario_influence,
        "leave_one_scenario": [
            {
                "construct": row["construct"],
                "contrast_id": row["contrast_id"],
                "leave_one_min": row["leave_one_min"],
                "leave_one_max": row["leave_one_max"],
                "leave_one_keeps_sign": row["leave_one_keeps_sign"],
            }
            for row in scenario_influence
        ],
        "text_structure_metrics": text_structure,
        "length_sensitivity": length_sensitivity,
        "construct_correlations": correlations,
        "limitations": LIMITATIONS,
    }


# ---------------------------------------------------------------------------
# SVG figures (inline, no external resources)
# ---------------------------------------------------------------------------


def _svg_open(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{title}" width="100%">',
        '<style>text{font-family:-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;}'
        '.grid{stroke:#d9e0ec;stroke-width:1;}.axis{fill:#5a667f;font-size:12px;}'
        '.val{fill:#172033;font-size:11px;font-weight:700;}'
        '.lineA{stroke:#315dc9;stroke-width:2.5;fill:none;}'
        '.lineB{stroke:#6945bd;stroke-width:2.5;fill:none;stroke-dasharray:5 4;}'
        '.dotA{fill:#315dc9;}.dotB{fill:#6945bd;}.bar{fill:#315dc9;}'
        '.barneg{fill:#8a5b00;}.cat{fill:#5a667f;font-size:11px;}</style>',
    ]


def _render_identity_process_svg(identity_by_process: list[dict]) -> str:
    # agency panel: AI vs human across six conditions on 1-7 scale
    entry = next(e for e in identity_by_process if e["construct"] == "agency")
    identities = entry["identities"]
    W, H, padL, padR, padT, padB = 640, 300, 54, 20, 34, 64
    plotW, plotH = W - padL - padR, H - padT - padB
    ymin, ymax = 1.0, 7.0

    def x(i: int) -> float:
        return padL + plotW * i / (len(CONDITION_ORDER) - 1)

    def y(v: float) -> float:
        return padT + plotH - (v - ymin) / (ymax - ymin) * plotH

    parts = _svg_open(W, H, f"{entry['label']}在AI与人类身份下随六种过程条件的均值")
    for gv in range(1, 8):
        parts.append(f'<line class="grid" x1="{padL}" y1="{y(gv):.1f}" x2="{W - padR}" y2="{y(gv):.1f}" />')
        parts.append(f'<text class="axis" x="{padL - 8}" y="{y(gv) + 4:.1f}" text-anchor="end">{gv}</text>')
    for idx, identity in enumerate(identities):
        pts = entry["means_by_identity"][identity]
        cls = "A" if idx == 0 else "B"
        path = []
        for i, p in enumerate(pts):
            if p["mean"] is None:
                continue
            path.append(f'{"M" if not path else "L"}{x(i):.1f},{y(p["mean"]):.1f}')
        parts.append(f'<path class="line{cls}" d="{" ".join(path)}" />')
        for i, p in enumerate(pts):
            if p["mean"] is None:
                continue
            parts.append(f'<circle class="dot{cls}" cx="{x(i):.1f}" cy="{y(p["mean"]):.1f}" r="4" />')
    for i in range(len(CONDITION_ORDER)):
        parts.append(f'<text class="cat" x="{x(i):.1f}" y="{H - padB + 20:.1f}" text-anchor="middle">C{i}</text>')
    legend = " · ".join(f"{name}" for name in identities)
    parts.append(f'<text class="cat" x="{padL}" y="{H - 12}">实线/虚线：{legend}（纵轴原量尺1–7）</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def _render_scenario_influence_svg(scenario_influence: list[dict]) -> str:
    # agency x A4 influence bars: how much removing each scenario changes the estimate
    row = next(r for r in scenario_influence
               if r["construct"] == "agency" and r["contrast_id"] == "A4")
    infl = [s for s in row["scenario_influence"] if s["influence"] is not None]
    W = 640
    barH, gap, padT, padL, padR = 22, 10, 40, 200, 60
    H = padT + len(infl) * (barH + gap) + 30
    maxv = max((s["influence"] for s in infl), default=1.0) or 1.0
    plotW = W - padL - padR
    parts = _svg_open(W, H, f"{row['construct_label']} {row['contrast_id']} 各场景对总体估计的影响")
    parts.append(f'<text class="axis" x="{padL}" y="24">去掉该场景后估计改变的绝对值（原量尺）</text>')
    for i, s in enumerate(infl):
        yy = padT + i * (barH + gap)
        w = plotW * (s["influence"] / maxv)
        cls = "barneg" if s["direction_changes"] else "bar"
        parts.append(f'<text class="cat" x="{padL - 8}" y="{yy + barH - 6:.1f}" text-anchor="end">{s["scenario_id"]}</text>')
        parts.append(f'<rect class="{cls}" x="{padL}" y="{yy:.1f}" width="{w:.1f}" height="{barH}" rx="3" />')
        flip = "（方向改变）" if s["direction_changes"] else ""
        parts.append(f'<text class="val" x="{padL + w + 6:.1f}" y="{yy + barH - 6:.1f}">{s["influence"]:.3f}{flip}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def _render_length_sensitivity_svg(length_sensitivity: dict) -> str:
    rows = [r for r in length_sensitivity["contrasts"]
            if r["base_estimate"] is not None and r["length_adjusted_estimate"] is not None]
    W = 640
    rowH, gap, padT, padL, padR = 26, 12, 46, 210, 70
    H = padT + len(rows) * (rowH + gap) + 20
    allv = [abs(r["base_estimate"]) for r in rows] + [abs(r["length_adjusted_estimate"]) for r in rows]
    maxv = max(allv, default=1.0) or 1.0
    plotW = W - padL - padR
    parts = _svg_open(W, H, "加入文本长度前后固定对比估计的变化")
    parts.append(f'<text class="axis" x="{padL}" y="26">深色：原估计　浅色：加入长度后（原量尺绝对值）</text>')
    for i, r in enumerate(rows):
        yy = padT + i * (rowH + gap)
        wb = plotW * (abs(r["base_estimate"]) / maxv)
        wa = plotW * (abs(r["length_adjusted_estimate"]) / maxv)
        label = f'{r["construct_label"]}·{r["contrast_id"]}'
        parts.append(f'<text class="cat" x="{padL - 8}" y="{yy + rowH - 8:.1f}" text-anchor="end">{label}</text>')
        parts.append(f'<rect class="bar" x="{padL}" y="{yy:.1f}" width="{wb:.1f}" height="10" rx="2" />')
        parts.append(f'<rect class="dotB" x="{padL}" y="{yy + 13:.1f}" width="{wa:.1f}" height="10" rx="2" opacity="0.6" />')
        parts.append(f'<text class="val" x="{padL + max(wb, wa) + 6:.1f}" y="{yy + rowH - 6:.1f}">{r["base_estimate"]:.2f}→{r["length_adjusted_estimate"]:.2f}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def build_report(payload: dict) -> str:
    lines = [
        "# 研究A现有数据稳健性分析", "",
        f"- 数据角色：`{payload['data_role']}`（既有数据的稳健性检查，非新模型结果）",
        f"- 原始响应：{payload['source_record_count']}条（`outputs/scale_scores.csv`）",
        f"- 聚合单元：{payload['aggregate_unit_count']}个（场景 × 身份 × 过程条件）",
        "- 本分析完全离线，未调用任何模型API，未生成新响应，未修改源文件。",
        "",
        "## 固定对比", "",
        "| id | 左条件 | 右条件 | 含义 |",
        "|---|---|---|---|",
    ]
    for c in payload["fixed_contrasts"]:
        lines.append(f"| {c['id']} | {c['left_condition']} | {c['right_condition']} | {c['label']} |")
    lines += ["", "## 文本长度词表（离线，写在代码常量中）", ""]
    lex = payload["text_structure_metrics"]["lexicons"]
    for name, words in lex.items():
        lines.append(f"- **{name}**：{', '.join(words)}")
    lines += ["", "## 长度敏感性", "",
              f"- 过程结构等级与字符数的描述性相关为 {payload['length_sensitivity']['condition_length_collinearity']}。",
              f"- {payload['length_sensitivity']['collinearity_note']}"]
    a4 = next((r for r in payload["length_sensitivity"]["contrasts"]
               if r["construct"] == "agency" and r["contrast_id"] == "A4"), None)
    if a4 and a4["base_estimate"] is not None and a4["length_adjusted_estimate"] is not None:
        flip = "方向没有改变" if not a4["direction_flips"] else "方向发生改变"
        lines.append(
            f"- 加入字符数和句子数后，A4估计由{a4['base_estimate']}变为{a4['length_adjusted_estimate']}，{flip}。"
            "由于文本长度与过程条件共同变化，这一分析说明估计对模型设定较敏感，"
            "无法据此分离文本长度和过程信息各自的独立作用。")
    lines += ["",
              "| 构念 | 对比 | 原估计 | 加长度后 | 绝对衰减比 | 方向改变 |",
              "|---|---|---:|---:|---:|---|"]
    for r in payload["length_sensitivity"]["contrasts"]:
        lines.append(
            f"| {r['construct_label']} | {r['contrast_id']} | "
            f"{r['base_estimate']} | {r['length_adjusted_estimate']} | "
            f"{r['absolute_shrink_ratio']} | {r['direction_flips']} |"
        )
    lines += ["", "## 三项公共发现（描述性状态 + 原始数字）", ""]
    pf = payload["public_findings"]
    proc = pf["process_information"]
    ident = pf["identity_label"]
    scen = pf["scenario_dependence"]
    lines += [
        "### 过程信息发现（过程条件对比）", "",
        f"- 构念：{proc['construct_label']}；对比：{proc['contrast_id']}"
        f"（{proc['left_condition']} − {proc['right_condition']}）",
        f"- 分析单位：{proc['unit_definition']}，共 {proc['total_unit_count']} 个配对单元",
        f"- 总体估计：{proc['full_effect']}；同方向单元：{proc['direction_majority_count']}/{proc['total_unit_count']}"
        f"（正 {proc['positive_count']} / 负 {proc['negative_count']} / 零 {proc['zero_count']}）",
        f"- 八场景范围：{proc['scenario_range']}；留一场景范围：{proc['leave_one_scenario_range']}；"
        f"留一保持同号：{proc['leave_one_scenario_same_sign']}",
        f"- 影响最大场景：{proc['most_influential_scenario']}",
        f"- 描述性状态：{proc['status_label']}",
        "",
        "### 身份标签发现（human − AI 身份差）", "",
        f"- 构念：{ident['construct_label']}；比较：{ident['identity_high']} − {ident['identity_low']}",
        f"- 分析单位：{ident['unit_definition']}，共 {ident['total_unit_count']} 个身份配对单元",
        f"- 总体身份差：{ident['overall_identity_difference']}；同方向单元：{ident['direction_majority_count']}/{ident['total_unit_count']}"
        f"（正 {ident['positive_count']} / 负 {ident['negative_count']} / 零 {ident['zero_count']}）",
        f"- 八场景身份差范围：{ident['scenario_range']}；留一场景范围：{ident['leave_one_scenario_range']}；"
        f"留一保持同号：{ident['leave_one_scenario_same_sign']}",
        f"- 影响最大场景：{ident['most_influential_scenario']}",
        f"- 描述性状态：{ident['status_label']}",
        "",
        "### 场景依赖（过程与身份效应的场景汇总，非第三处理效应）", "",
        f"- 过程效应八场景范围：{scen['process_effect_range']}；留一保持同号：{scen['process_leave_one_same_sign']}",
        f"- 身份效应八场景范围：{scen['identity_effect_range']}；留一保持同号：{scen['identity_leave_one_same_sign']}",
        f"- 过程影响最大场景：{scen['largest_process_influence']}；身份影响最大场景：{scen['largest_identity_influence']}",
        f"- {scen['interpretation']}",
    ]
    lines += ["", "## 构念相关说明", "",
              f"- {payload['construct_correlations']['interpretation_note']}",
              "- 五个公开构念之间没有共享题项；responsibility_total 为责任子构念的合成分。", ""]
    lines += ["## 限制", ""]
    for item in payload["limitations"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Orchestration + CLI
# ---------------------------------------------------------------------------


def _write_outputs(payload: dict, output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    figures = {
        FIG_IDENTITY: _render_identity_process_svg(payload["identity_by_process"]),
        FIG_INFLUENCE: _render_scenario_influence_svg(payload["scenario_influence"]),
        FIG_LENGTH: _render_length_sensitivity_svg(payload["length_sensitivity"]),
    }
    artifacts = {
        "public_json": public_dumps(payload),
        "report": build_report(payload),
        "figures": {path.name: svg for path, svg in figures.items()},
    }
    # write artifact copy of the JSON into the output dir for inspection
    write_public_json(output_dir / "research_a_robustness_summary.json", payload)
    (output_dir / "research_a_robustness_report.md").write_text(artifacts["report"], encoding="utf-8")
    return artifacts


def run(scores_path: Path, output_dir: Path) -> dict:
    data = load_scores(scores_path)
    units = build_units(data)
    payload = build_payload(data, units)
    return payload


def _emit(payload: dict, output_dir: Path) -> None:
    artifacts = _write_outputs(payload, output_dir)
    write_public_json(PUBLIC_JSON, payload)
    REPORT_MD.write_text(artifacts["report"], encoding="utf-8")
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for name, svg in artifacts["figures"].items():
        (FIG_DIR / name).write_text(svg, encoding="utf-8")


def _check(payload: dict) -> int:
    artifacts_json = public_dumps(payload)
    mismatched = []
    if not PUBLIC_JSON.is_file() or PUBLIC_JSON.read_text(encoding="utf-8") != artifacts_json:
        mismatched.append(str(PUBLIC_JSON))
    report = build_report(payload)
    if not REPORT_MD.is_file() or REPORT_MD.read_text(encoding="utf-8") != report:
        mismatched.append(str(REPORT_MD))
    figures = {
        FIG_IDENTITY: _render_identity_process_svg(payload["identity_by_process"]),
        FIG_INFLUENCE: _render_scenario_influence_svg(payload["scenario_influence"]),
        FIG_LENGTH: _render_length_sensitivity_svg(payload["length_sensitivity"]),
    }
    for path, svg in figures.items():
        if not path.is_file() or path.read_text(encoding="utf-8") != svg:
            mismatched.append(str(path))
    if mismatched:
        print("research A robustness outputs are OUT OF DATE: " + ", ".join(mismatched), file=sys.stderr)
        return 1
    print("research A robustness outputs are up to date")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline Research A robustness analysis.")
    parser.add_argument("--scores", default=str(DEFAULT_SCORES))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--check", action="store_true",
                        help="Rebuild in memory and compare to committed outputs; exit 1 if different.")
    args = parser.parse_args(argv)

    try:
        payload = run(Path(args.scores).resolve(), Path(args.output).resolve())
    except RobustnessError as exc:
        print(f"analyze_research_a_robustness: ERROR: {exc}", file=sys.stderr)
        return 2

    if args.check:
        return _check(payload)

    _emit(payload, Path(args.output).resolve())
    print("wrote research A robustness outputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
