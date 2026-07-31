"""Tests for the Study B offline protocol package."""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research_packages" / "study_b"
SCRIPTS = ROOT / "scripts"


def _load(module_name: str, filename: str):
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(module_name, SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = _load("build_study_b_protocol_package_test", "build_study_b_protocol_package.py")


def _reject_constant(value):
    raise ValueError(f"non-standard constant: {value}")


def _strict_load(path: Path):
    text = path.read_text(encoding="utf-8")
    assert not text.startswith("\ufeff"), f"BOM in {path}"
    return json.loads(text, parse_constant=_reject_constant)


def _read_csv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


# --- protocol manifest ------------------------------------------------------

def test_protocol_manifest_fields_present():
    text = (PACKAGE / "protocol_manifest.yaml").read_text(encoding="utf-8")
    for field in [
        "program_name:", "study_name:", "source_commit:", "protocol_date:",
        "protocol_scope:", "material_count:", "condition_count:", "scenario_count:",
        "direction_count:", "construct_ids:", "supplementary_score_ids:",
        "contrast_ids:", "analysis_formula:", "material_source_paths:",
        "item_source_paths:", "scoring_spec_paths:", "analysis_plan_paths:",
        "example_data_paths:", "public_page_paths:",
    ]:
        assert field in text, field


def test_protocol_manifest_scope_and_commit():
    text = (PACKAGE / "protocol_manifest.yaml").read_text(encoding="utf-8")
    assert "protocol_scope: offline_protocol_and_import" in text
    assert "source_commit: 9cb4aae1e3010f90b2a9c34ae87111b5e373de59" in text
    assert "material_count: 96" in text
    assert "condition_count: 6" in text
    assert "scenario_count: 8" in text
    assert "direction_count: 2" in text


def test_protocol_manifest_model_ids_metadata_only():
    text = (PACKAGE / "protocol_manifest.yaml").read_text(encoding="utf-8")
    assert "protocol_metadata_only: true" in text
    assert "deepseek-v4-pro" in text and "gpt-5.6-terra" in text


def test_protocol_manifest_has_no_online_fields():
    text = (PACKAGE / "protocol_manifest.yaml").read_text(encoding="utf-8")
    # Forbidden as YAML keys/values, not as descriptive prose in the header.
    for key in ["api_url:", "api_key:", "token_budget:", "cost:", "concurrency:",
                "timeout:", "retry:", "http://", "https://api"]:
        assert key not in text, key


# --- material matrix --------------------------------------------------------

def test_material_matrix_has_96_rows():
    rows = _read_csv(PACKAGE / "material_matrix.csv")
    assert len(rows) == 96


def test_material_matrix_ids_unique():
    rows = _read_csv(PACKAGE / "material_matrix.csv")
    ids = [row["material_id"] for row in rows]
    assert len(set(ids)) == 96


def test_material_matrix_covers_full_grid():
    rows = _read_csv(PACKAGE / "material_matrix.csv")
    assert {row["condition_id"] for row in rows} == {"C0", "C1", "C2", "C3", "C4", "C5"}
    assert len({row["scenario_id"] for row in rows}) == 8
    assert {row["direction_version"] for row in rows} == {"A", "B"}


def test_material_matrix_columns():
    rows = _read_csv(PACKAGE / "material_matrix.csv")
    assert set(rows[0]) == set(builder.MATERIAL_MATRIX_COLUMNS)


# --- scoring template -------------------------------------------------------

def test_scoring_template_has_192_rows():
    rows = _read_csv(PACKAGE / "scoring_matrix_template.csv")
    assert len(rows) == 192


def test_scoring_template_two_slots_per_material():
    rows = _read_csv(PACKAGE / "scoring_matrix_template.csv")
    per_material: dict[str, set[str]] = {}
    for row in rows:
        per_material.setdefault(row["material_id"], set()).add(row["judge_slot"])
    assert len(per_material) == 96
    assert all(slots == {"judge_1", "judge_2"} for slots in per_material.values())


def test_scoring_template_defaults():
    rows = _read_csv(PACKAGE / "scoring_matrix_template.csv")
    for row in rows:
        assert row["response_source"] == "external_offline_file"
        assert row["validation_status"] == "awaiting_input"
        assert row["parse_status"] == "not_started"
        assert row["item_score_status"] == "not_started"


def test_scoring_template_has_no_scores_or_costs():
    text = (PACKAGE / "scoring_matrix_template.csv").read_text(encoding="utf-8").lower()
    for forbidden in ["response_text", "item_score,", "construct_score", "token", "cost",
                      "request_id"]:
        assert forbidden not in text, forbidden


# --- asset hashes -----------------------------------------------------------

def test_asset_hashes_strict_and_stable():
    payload = _strict_load(PACKAGE / "asset_hashes.json")
    assert payload["hash_algorithm"] == "sha256"
    assert payload["material_count"] == 96
    assert payload["file_count"] == len(payload["files"])
    assert len(payload["material_content_sha256"]) == 96
    # regenerating asset hashes yields identical content (determinism).
    regenerated = json.loads(builder.build_asset_hashes())
    assert regenerated == payload


def test_all_package_json_is_strict():
    for path in PACKAGE.rglob("*.json"):
        payload = _strict_load(path)
        # ensure no non-finite floats slipped in
        stack = [payload]
        while stack:
            item = stack.pop()
            if isinstance(item, float):
                assert math.isfinite(item)
            elif isinstance(item, dict):
                stack.extend(item.values())
            elif isinstance(item, list):
                stack.extend(item)


# --- determinism ------------------------------------------------------------

def test_build_check_reports_up_to_date():
    assert builder.check_artefacts(PACKAGE) == []


def test_artefacts_are_deterministic():
    first = builder.artefacts()
    second = builder.artefacts()
    assert first == second
