"""Execution checks for the Research A V2 scenario-block analysis."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "build_research_a_v2.py"
SOURCE = ROOT / "outputs" / "scale_scores.csv"


def _load_module():
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    spec = importlib.util.spec_from_file_location("build_research_a_v2_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v2 = _load_module()


def test_v2_core_unit_grid_is_complete():
    scores = v2.load_scores(SOURCE)
    units = v2.build_units(scores)
    assert len(scores) == 360
    assert len(units) == 96
    assert units["scenario_id"].nunique() == 8
    assert units["identity_label"].nunique() == 2
    assert units["process_condition"].nunique() == 6
    assert units["generation_count"].min() >= 3
    assert units["generation_count"].max() <= 4


def test_v2_contrast_summary_contains_public_constructs():
    scores = v2.load_scores(SOURCE)
    units = v2.build_units(scores)
    differences = v2.build_differences(units)
    summary = v2.build_contrasts(differences)
    public = summary[
        (summary["scope"] == "all_identities")
        & (summary["construct"].isin(v2.PUBLIC_CONSTRUCTS))
    ]
    assert len(public) == len(v2.PUBLIC_CONSTRUCTS) * len(v2.CONTRASTS)
    assert set(public["matched_unit_count"]) == {16}
    assert set(public["scenario_count"]) == {8}
    assert public["direction_consistency"].between(0.5, 1.0).all()


def test_v2_run_writes_independent_outputs(tmp_path: Path):
    output = tmp_path / "research-a-v2"
    v2.run(SOURCE, output)
    expected = {
        "unit_summary.csv",
        "condition_summary.csv",
        "contrast_unit_differences.csv",
        "contrast_summary.csv",
        "research_a_v2_summary.json",
        "research_a_v2_report.md",
    }
    assert {path.name for path in output.iterdir()} == expected
    assert len(pd.read_csv(output / "unit_summary.csv")) == 96
    payload = json.loads((output / "research_a_v2_summary.json").read_text(encoding="utf-8"))
    assert payload["record_count"] == 360
    assert payload["unit_count"] == 96
    assert payload["analysis_unit"] == "scenario_id × identity_label × process_condition"
    assert len(payload["public_contrast_summary"]) == 20


def test_v2_source_and_historical_outputs_are_read_only(tmp_path: Path):
    before = SOURCE.read_bytes()
    v2.run(SOURCE, tmp_path / "out")
    assert SOURCE.read_bytes() == before
