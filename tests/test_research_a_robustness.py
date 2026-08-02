"""Offline tests for the Research A robustness analysis (RA-ROBUST)."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCORES = ROOT / "outputs" / "scale_scores.csv"
PUBLIC_JSON = ROOT / "site" / "data" / "research_a_robustness_summary.json"
SITE_JS = ROOT / "site" / "assets" / "js" / "site.js"
FLOAT_ABS_TOLERANCE = 1e-12
FLOAT_REL_TOLERANCE = 1e-12


def _load_module():
    scripts_dir = ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    path = scripts_dir / "analyze_research_a_robustness.py"
    spec = importlib.util.spec_from_file_location("analyze_research_a_robustness", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["analyze_research_a_robustness"] = module
    spec.loader.exec_module(module)
    return module


mod = _load_module()


@pytest.fixture(scope="module")
def payload():
    data = mod.load_scores(SCORES)
    units = mod.build_units(data)
    return mod.build_payload(data, units), data, units


def _assert_same_structure_and_numbers(actual, expected, path: str = "$"):
    """Compare JSON-like values exactly except for negligible float tails.

    Linear algebra libraries can differ at roughly 1e-14 across operating
    systems. Keys, list lengths, strings, booleans and integers remain exact;
    only finite floating-point values receive a tightly bounded tolerance.
    """
    if isinstance(expected, dict):
        assert isinstance(actual, dict), path
        assert actual.keys() == expected.keys(), path
        for key in expected:
            _assert_same_structure_and_numbers(actual[key], expected[key], f"{path}.{key}")
        return
    if isinstance(expected, list):
        assert isinstance(actual, list), path
        assert len(actual) == len(expected), path
        for index, (actual_item, expected_item) in enumerate(zip(actual, expected, strict=True)):
            _assert_same_structure_and_numbers(actual_item, expected_item, f"{path}[{index}]")
        return
    if isinstance(expected, float) or isinstance(actual, float):
        assert isinstance(actual, (int, float)) and not isinstance(actual, bool), path
        assert isinstance(expected, (int, float)) and not isinstance(expected, bool), path
        assert math.isfinite(float(actual)) and math.isfinite(float(expected)), path
        assert float(actual) == pytest.approx(
            float(expected),
            rel=FLOAT_REL_TOLERANCE,
            abs=FLOAT_ABS_TOLERANCE,
        ), path
        return
    assert actual == expected, path


def test_source_module_never_imports_model_sdk():
    text = (ROOT / "scripts" / "analyze_research_a_robustness.py").read_text(encoding="utf-8")
    for banned in ["import openai", "import anthropic", "import requests", "import httpx",
                   "import socket", "api_key", "API_KEY"]:
        assert banned not in text, banned


def test_original_records_are_read_only_and_count_360(payload):
    _payload, data, _units = payload
    assert len(data) == 360
    assert data["participant_id"].is_unique


def test_aggregate_unit_count_is_96(payload):
    p, _data, units = payload
    assert len(units) == 96
    assert p["aggregate_unit_count"] == 96
    assert p["source_record_count"] == 360


def test_fixed_contrasts_unchanged(payload):
    p, _data, _units = payload
    ids = [(c["id"], c["left_condition"], c["right_condition"]) for c in p["fixed_contrasts"]]
    assert ids == [
        ("A1", "alternatives", "direct_choice"),
        ("A2", "reasons_concise", "direct_choice_long"),
        ("A3", "reflection_feedback", "reasons"),
        ("A4", "reflection_feedback", "direct_choice_long"),
    ]


# --- process finding: fixed process-condition contrast, 16 units --------------

def test_process_finding_uses_fixed_process_contrast(payload):
    p, _data, _units = payload
    proc = p["public_findings"]["process_information"]
    assert proc["comparison_type"] == "process_condition_contrast"
    assert proc["construct"] == "agency"
    assert proc["contrast_id"] == "A4"
    assert proc["left_condition"] == "reflection_feedback"
    assert proc["right_condition"] == "direct_choice_long"


def test_process_finding_uses_16_scenario_identity_units(payload):
    p, _data, _units = payload
    proc = p["public_findings"]["process_information"]
    assert proc["unit_definition"] == "scenario_id × identity_label"
    assert proc["total_unit_count"] == 16
    assert proc["positive_count"] + proc["negative_count"] + proc["zero_count"] == 16


# --- identity finding: human - AI, 48 units -----------------------------------

def test_identity_finding_uses_human_minus_ai(payload):
    p, _data, _units = payload
    ident = p["public_findings"]["identity_label"]
    assert ident["comparison_type"] == "identity_difference_human_minus_ai"
    assert ident["construct"] == "free_will_attribution"
    assert ident["identity_high"] == "人类决策者"
    assert ident["identity_low"] == "AI 决策者"


def test_identity_finding_uses_48_scenario_condition_units(payload):
    p, _data, _units = payload
    ident = p["public_findings"]["identity_label"]
    assert ident["unit_definition"] == "scenario_id × process_condition"
    assert ident["total_unit_count"] == 48
    assert ident["positive_count"] + ident["negative_count"] + ident["zero_count"] == 48


def test_process_and_identity_findings_do_not_share_a4_evidence(payload):
    p, _data, _units = payload
    proc = p["public_findings"]["process_information"]
    ident = p["public_findings"]["identity_label"]
    # the identity finding must NOT be an A4 process contrast.
    assert ident.get("contrast_id") is None
    assert proc["contrast_id"] == "A4"
    assert proc["comparison_type"] != ident["comparison_type"]


def test_scenario_dependence_is_not_a_third_treatment_effect(payload):
    p, _data, _units = payload
    scen = p["public_findings"]["scenario_dependence"]
    # it summarises process + identity ranges, not a new contrast.
    for field in ["process_effect_range", "identity_effect_range",
                  "process_leave_one_same_sign", "identity_leave_one_same_sign",
                  "largest_process_influence", "largest_identity_influence",
                  "interpretation"]:
        assert field in scen, field
    assert "contrast_id" not in scen
    assert "full_effect" not in scen


def test_data_role_and_no_cross_model_fields(payload):
    p, _data, _units = payload
    assert p["data_role"] == "research_a_existing_data_robustness"
    text = json.dumps(p, ensure_ascii=False)
    for banned in ["formal_cross_model_result", "new_model_response",
                   "validated_construct", "causal_effect"]:
        assert banned not in text, banned


def test_status_labels_are_descriptive_not_evidence_grades(payload):
    p, _data, _units = payload
    allowed = {"多数场景方向一致", "方向一致但幅度存在场景差异",
               "结果对个别场景敏感", "当前数据未呈现清晰方向"}
    for key in ("process_information", "identity_label"):
        assert p["public_findings"][key]["status_label"] in allowed
    text = json.dumps(p, ensure_ascii=False)
    for banned in ["强证据", "高可信度", "已验证", "已证明", "稳健结论", "构念有效", "跨场景较稳定"]:
        assert banned not in text, banned


def test_analysis_is_deterministic(payload):
    p, data, units = payload
    again = mod.build_payload(data, units)
    assert json.dumps(p, sort_keys=True) == json.dumps(again, sort_keys=True)


def test_public_json_is_strict_no_nan_or_inf(payload):
    p, _data, _units = payload
    text = mod.public_dumps(p)
    assert "NaN" not in text and "Infinity" not in text
    parsed = json.loads(text)

    def walk(value):
        if isinstance(value, float):
            assert math.isfinite(value)
        elif isinstance(value, dict):
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(parsed)


def test_leave_one_scenario_covers_eight_scenarios(payload):
    p, _data, _units = payload
    for row in p["scenario_influence"]:
        assert row["scenario_count"] == 8
        assert len(row["scenario_influence"]) == 8
    # both public findings also carry 8-scenario leave-one influence.
    assert len(p["public_findings"]["process_information"]["scenario_influence"]) == 8
    assert len(p["public_findings"]["identity_label"]["scenario_influence"]) == 8


def test_text_metrics_are_reproducible(payload):
    p, _data, _units = payload
    lexicons = p["text_structure_metrics"]["lexicons"]
    assert lexicons["alternative_markers"]
    assert lexicons["reason_connectives"]
    per_condition = p["text_structure_metrics"]["per_condition"]
    assert len(per_condition) == 6


def test_findings_not_selected_by_largest_difference():
    text = (ROOT / "scripts" / "analyze_research_a_robustness.py").read_text(encoding="utf-8")
    # findings/constructs are pinned constants, not argmax over effect size.
    assert 'PROCESS_FINDING_CONSTRUCT = "agency"' in text
    assert 'IDENTITY_FINDING_CONSTRUCT = "free_will_attribution"' in text
    for banned in ["argmax", "idxmax", "sort_values(", "max(effect"]:
        assert banned not in text, banned


def test_homepage_numbers_come_from_correct_fields():
    js = SITE_JS.read_text(encoding="utf-8")
    # process number from process_information.direction_majority_count/total_unit_count
    assert "public_findings" in js
    assert "process_information" in js
    assert "identity_label" in js
    assert "direction_majority_count" in js
    assert "total_unit_count" in js
    # scenario number is a scenario-sensitivity number, NOT the length percentage.
    assert "process_effect_range" in js
    assert "absolute_shrink_ratio" not in js


def test_numeric_comparison_tolerates_only_platform_tail_noise():
    _assert_same_structure_and_numbers({"value": 1.0 + 5e-14}, {"value": 1.0})
    with pytest.raises(AssertionError):
        _assert_same_structure_and_numbers({"value": 1.0 + 1e-8}, {"value": 1.0})


def test_committed_public_json_matches_current_analysis(payload):
    p, _data, _units = payload
    assert PUBLIC_JSON.is_file()
    committed = json.loads(PUBLIC_JSON.read_text(encoding="utf-8"))
    _assert_same_structure_and_numbers(p, committed)
