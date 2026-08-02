"""Offline tests for the Study B material-integrity audit (SB-AUDIT)."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
STIMULI = (
    ROOT / "tasks" / "attribution_behavior" / "evaluations"
    / "pa_wu_r1_pilot" / "stimuli.jsonl"
)
SUMMARY_JSON = ROOT / "research_packages" / "study_b" / "material_integrity_summary.json"
AUDIT_CSV = ROOT / "research_packages" / "study_b" / "material_integrity_audit.csv"
PAGE_JSON = ROOT / "docs" / "pa-wu-r1-pilot" / "data" / "material_integrity_summary.json"
STUDY_B_HTML = ROOT / "docs" / "pa-wu-r1-pilot" / "index.html"
STUDY_B_JS = ROOT / "docs" / "pa-wu-r1-pilot" / "app.js"


def _load_module():
    scripts_dir = ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    path = scripts_dir / "audit_study_b_materials.py"
    spec = importlib.util.spec_from_file_location("audit_study_b_materials", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["audit_study_b_materials"] = module
    spec.loader.exec_module(module)
    return module


mod = _load_module()


@pytest.fixture(scope="module")
def audited():
    materials = mod.load_materials(STIMULI)
    records, summary = mod.audit_materials(materials)
    return materials, records, summary


def test_source_module_is_offline():
    text = (ROOT / "scripts" / "audit_study_b_materials.py").read_text(encoding="utf-8")
    for banned in ["import openai", "import anthropic", "import requests", "import httpx",
                   "import socket", "urllib.request", "api_key", "API_KEY"]:
        assert banned not in text, banned


def test_grid_is_complete_6x8x2(audited):
    materials, _records, summary = audited
    assert len(materials) == 96
    assert summary["material_count"] == 96
    assert summary["expected_count"] == 96
    assert summary["complete_grid"] is True


def test_material_ids_unique(audited):
    materials, _records, _summary = audited
    ids = [m["material_id"] for m in materials]
    assert len(ids) == len(set(ids))


def test_every_scenario_direction_has_c0_to_c5(audited):
    materials, _records, _summary = audited
    grid = {}
    for m in materials:
        grid.setdefault((m["scenario_id"], m["direction_version"]), set()).add(m["condition_id"])
    assert len(grid) == 16
    for conds in grid.values():
        assert conds == {"C0", "C1", "C2", "C3", "C4", "C5"}


def test_status_values_are_limited(audited):
    _materials, records, _summary = audited
    for rec in records:
        assert rec["status"] in {"pass", "manual_review", "fail"}


# --- deterministic structure vs semantic review are separate ------------------

def test_structural_check_and_semantic_review_are_separate(audited):
    _materials, _records, summary = audited
    dsc = summary["deterministic_structure_check"]
    for field in ["expected_count", "actual_count", "complete_grid",
                  "duplicate_id_count", "structural_pass_count",
                  "structural_fail_count", "field_consistency",
                  "direction_threshold_flags"]:
        assert field in dsc, field
    assert "semantic_review" in summary
    # the summary must NOT collapse the two into a single pass count.
    assert "deterministic_pass_count" not in summary
    assert "manual_review_count" not in summary


def test_semantic_review_status_is_not_assessed(audited):
    _materials, _records, summary = audited
    sem = summary["semantic_review"]
    assert sem["status"] == "not_assessed"
    assert sem["assessed_material_count"] == 0


def test_zero_threshold_flags_do_not_imply_zero_semantic_review(audited):
    _materials, _records, summary = audited
    # even if direction_threshold_flags is 0, semantic review stays not_assessed.
    assert summary["semantic_review"]["status"] == "not_assessed"


def test_symmetry_thresholds_only_flag_review(audited):
    _materials, records, _summary = audited
    for rec in records:
        review = rec["review_issues"]
        if "symmetry" in review and not rec["fail_issues"]:
            assert rec["status"] == "manual_review"


def test_page_does_not_claim_complete_verification():
    html = STUDY_B_HTML.read_text(encoding="utf-8")
    js = STUDY_B_JS.read_text(encoding="utf-8")
    for banned in ["全部验证通过", "材料质量已验证", "0条需要人工复核",
                   "内容效度通过", "材料已验证完成"]:
        assert banned not in html, banned
        assert banned not in js, banned
    # the page speaks of a structural check, not a full verification.
    assert "确定性结构检查" in js


def test_page_summary_uses_structural_fields():
    payload = json.loads(PAGE_JSON.read_text(encoding="utf-8"))
    assert "structural_pass_count" in payload
    assert "structural_fail_count" in payload
    assert "direction_threshold_flags" in payload
    assert payload["semantic_review_status"] == "not_assessed"
    assert "deterministic_pass_count" not in payload
    assert "manual_review_count" not in payload


def test_audit_does_not_modify_input(audited):
    materials, _records, _summary = audited
    before = STIMULI.read_bytes()
    mod.audit_materials(materials)
    assert STIMULI.read_bytes() == before


def test_summary_json_is_strict(audited):
    _materials, _records, summary = audited
    text = mod.public_dumps(summary)
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


def test_audit_is_deterministic(audited):
    materials, records, summary = audited
    records2, summary2 = mod.audit_materials(materials)
    assert mod._csv_text(records) == mod._csv_text(records2)
    assert mod.public_dumps(summary) == mod.public_dumps(summary2)


def test_committed_summary_matches_current_audit(audited):
    _materials, _records, summary = audited
    assert SUMMARY_JSON.is_file()
    assert SUMMARY_JSON.read_text(encoding="utf-8") == mod.public_dumps(summary)


def test_committed_csv_matches_current_audit(audited):
    _materials, records, _summary = audited
    assert AUDIT_CSV.is_file()
    assert AUDIT_CSV.read_text(encoding="utf-8") == mod._csv_text(records)
