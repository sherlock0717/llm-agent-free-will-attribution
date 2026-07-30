"""Tests for the Study B external offline result validation and import tools."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research_packages" / "study_b"
SCRIPTS = ROOT / "scripts"
EXAMPLE = PACKAGE / "external_result_example.jsonl"

NEW_OFFLINE_SCRIPTS = [
    "build_study_b_protocol_package.py",
    "validate_study_b_external_results.py",
    "import_study_b_external_results.py",
    "build_study_b_offline_demo.py",
]

FORBIDDEN_IMPORTS = [
    "import openai", "import anthropic", "import requests", "import httpx",
    "import aiohttp", "import urllib.request", "import socket",
    "from openai", "from anthropic", "from requests", "from httpx",
    "from aiohttp", "from urllib.request", "from urllib import request",
    "import urllib", "from socket",
]


def _load(name: str, filename: str):
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validate = _load("validate_study_b_external_results_test", "validate_study_b_external_results.py")
importer = _load("import_study_b_external_results_test", "import_study_b_external_results.py")


def _records():
    return [json.loads(line) for line in EXAMPLE.read_text(encoding="utf-8").splitlines() if line.strip()]


def _run_validate(records):
    schema = validate.load_schema()
    material_ids = validate.load_material_ids()
    return validate.validate_records(records, schema, material_ids)


# --- happy path -------------------------------------------------------------

def test_example_file_is_valid():
    report = _run_validate(_records())
    assert report["valid"] is True
    assert report["error_count"] == 0
    assert report["record_count"] == 2
    assert report["network_operations"] == "none"


def test_schema_required_fields_and_ranges():
    schema = validate.load_schema()
    assert set(schema["required_fields"]) == {
        "material_id", "judge_slot", "judge_model_id",
        "item_responses", "source_record_id", "source_file_hash",
    }
    assert len(schema["item_scale_ranges"]) == 27


# --- rejection cases --------------------------------------------------------

def _codes(report):
    return {error["code"] for error in report["errors"]}


def test_duplicate_key_rejected():
    records = _records()
    dup = copy.deepcopy(records[0])
    report = _run_validate([records[0], dup])
    assert not report["valid"]
    assert "duplicate_key" in _codes(report)


def test_unknown_item_rejected():
    records = _records()
    records[0]["item_responses"]["not_a_real_item"] = 3
    report = _run_validate([records[0]])
    assert "unknown_item" in _codes(report)


def test_missing_item_rejected():
    records = _records()
    records[0]["item_responses"].pop("wu_in1a")
    report = _run_validate([records[0]])
    assert "missing_item" in _codes(report)


def test_out_of_range_rejected():
    records = _records()
    records[0]["item_responses"]["wu_in1a"] = 9  # scale max is 7
    report = _run_validate([records[0]])
    assert "out_of_range" in _codes(report)


def test_nan_rejected():
    records = _records()
    records[0]["item_responses"]["wu_ms1"] = float("nan")
    report = _run_validate([records[0]])
    assert "non_finite_or_non_numeric" in _codes(report)


def test_infinity_rejected():
    records = _records()
    records[0]["item_responses"]["wu_ms1"] = float("inf")
    report = _run_validate([records[0]])
    assert "non_finite_or_non_numeric" in _codes(report)


def test_unknown_material_id_rejected():
    records = _records()
    records[0]["material_id"] = "C9__nope__A__machine"
    report = _run_validate([records[0]])
    assert "unknown_material_id" in _codes(report)


def test_bad_judge_slot_rejected():
    records = _records()
    records[0]["judge_slot"] = "judge_3"
    report = _run_validate([records[0]])
    assert "bad_judge_slot" in _codes(report)


def test_unknown_field_rejected():
    records = _records()
    records[0]["estimated_cost"] = 0.01
    report = _run_validate([records[0]])
    assert "unknown_field" in _codes(report)


def test_missing_required_field_rejected():
    records = _records()
    records[0].pop("source_file_hash")
    report = _run_validate([records[0]])
    assert "missing_field" in _codes(report)


# --- import tool behaviour --------------------------------------------------

def test_validate_only_writes_nothing(tmp_path):
    out = tmp_path / "should_not_exist"
    rc = importer.main([
        "--input", str(EXAMPLE),
        "--output", str(out),
        "--validate-only",
    ])
    assert rc == 0
    assert not out.exists()


def test_dry_run_writes_nothing(tmp_path):
    out = tmp_path / "dry"
    rc = importer.main(["--input", str(EXAMPLE), "--output", str(out), "--dry-run"])
    assert rc == 0
    assert not out.exists()


def test_import_creates_directory_and_artifacts(tmp_path):
    out = tmp_path / "import_one"
    rc = importer.main(["--input", str(EXAMPLE), "--output", str(out)])
    assert rc == 0
    assert (out / "manifest.json").is_file()
    assert (out / "validation_report.json").is_file()
    assert (out / "standardized_records.jsonl").is_file()
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["network_operations"] == "none"
    assert manifest["record_count"] == 2


def test_import_refuses_to_overwrite(tmp_path):
    out = tmp_path / "import_twice"
    assert importer.main(["--input", str(EXAMPLE), "--output", str(out)]) == 0
    second = importer.main(["--input", str(EXAMPLE), "--output", str(out)])
    assert second == 3


def test_input_file_is_not_modified(tmp_path):
    before = EXAMPLE.read_bytes()
    importer.main(["--input", str(EXAMPLE), "--output", str(tmp_path / "ro"), "--validate-only"])
    assert EXAMPLE.read_bytes() == before


# --- static offline gate ----------------------------------------------------

def test_new_offline_scripts_have_no_network_imports():
    for filename in NEW_OFFLINE_SCRIPTS:
        text = (SCRIPTS / filename).read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_IMPORTS:
            assert forbidden not in text, (filename, forbidden)


def test_new_offline_scripts_have_no_api_key_reads():
    for filename in NEW_OFFLINE_SCRIPTS:
        text = (SCRIPTS / filename).read_text(encoding="utf-8")
        for forbidden in ["os.environ", "getenv", "API_KEY", "OPENAI_API_KEY",
                          "ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY"]:
            assert forbidden not in text, (filename, forbidden)


def test_new_offline_scripts_do_not_import_model_sdk():
    for filename in NEW_OFFLINE_SCRIPTS:
        text = (SCRIPTS / filename).read_text(encoding="utf-8")
        for forbidden in ["freewill_attribution.model", "import openai", "ollama"]:
            assert forbidden not in text, (filename, forbidden)
