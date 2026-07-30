"""Release-gate checks for the combined public Pages artifact."""

from __future__ import annotations

import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
STUDY_A = ROOT / "docs" / "identity-process-attribution-baseline"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


assemble_pages = _load(ROOT / "scripts" / "assemble_pages.py", "assemble_pages_release_gate")
check_public_json = _load(ROOT / "scripts" / "check_public_json.py", "check_public_json_release_gate")
public_json = _load(ROOT / "scripts" / "public_json.py", "public_json_release_gate")


def test_research_a_public_page_has_complete_structure():
    html = (STUDY_A / "index.html").read_text(encoding="utf-8")
    for section_id in [
        "question",
        "design",
        "materials",
        "measurement",
        "data",
        "analysis",
        "results",
        "repro",
    ]:
        assert f'id="{section_id}"' in html
    assert "身份与决策过程归因基线" in html
    assert "DeepSeek API模型模拟问卷响应" in html
    assert "python -m http.server 8000 --directory _site" in html


def test_research_a_public_copy_uses_positive_status_language():
    html = (STUDY_A / "index.html").read_text(encoding="utf-8")
    for phrase in ["仍待", "尚未", "不能", "无法", "不支持", "不代表"]:
        assert phrase not in html, phrase


def test_research_a_dynamic_groups_are_independent():
    app = (STUDY_A / "app.js").read_text(encoding="utf-8")
    assert "Promise.allSettled" in app
    assert "loadStoryGroup" in app
    assert "loadMeasurementGroup" in app
    assert "loadAnalysisGroup" in app
    assert "errorPanel" in app
    assert "Promise.all([" not in app


def test_strict_json_checker_rejects_nan(tmp_path: Path):
    invalid = tmp_path / "invalid.json"
    invalid.write_text('{"value": NaN}', encoding="utf-8")
    with pytest.raises(check_public_json.PublicJsonError):
        check_public_json.validate_file(invalid)


def test_public_json_writer_normalizes_non_finite_values():
    text = public_json.dumps({"nan": math.nan, "pos": math.inf, "neg": -math.inf})
    assert "NaN" not in text and "Infinity" not in text
    assert json.loads(text) == {"nan": None, "neg": None, "pos": None}


def test_repository_public_json_is_browser_compatible():
    paths = list(check_public_json.DEFAULT_PATHS)
    files = check_public_json._iter_json_files(paths)
    assert files
    for path in files:
        check_public_json.validate_file(path)


def test_combined_pages_artifact_contains_all_routes(tmp_path: Path):
    output = tmp_path / "site"
    assemble_pages.assemble(output)
    required = [
        output / "index.html",
        output / "identity-process-attribution-baseline" / "index.html",
        output / "identity-process-attribution-baseline" / "app.js",
        output / "identity-process-attribution-baseline" / "styles.css",
        output / "machine-decision-process-attribution" / "index.html",
        output / "pa-wu-r1-pilot" / "index.html",
    ]
    assert all(path.is_file() for path in required)
    redirect = required[-1].read_text(encoding="utf-8")
    assert "../machine-decision-process-attribution/" in redirect


def test_research_a_page_uses_existing_root_data_contract():
    app = (STUDY_A / "app.js").read_text(encoding="utf-8")
    names = set(re.findall(r'fetchJson\("([^"]+\.json)"\)', app))
    assert names == {
        "showcase_story.json",
        "measurement_summary.json",
        "analysis_results.json",
        "research_a_v2_summary.json",
    }
    for name in names:
        payload = json.loads((ROOT / "site" / "data" / name).read_text(encoding="utf-8"))
        assert isinstance(payload, dict)


V2_JSON = ROOT / "site" / "data" / "research_a_v2_summary.json"


def test_research_a_v2_public_json_is_strict_and_complete():
    check_public_json.validate_file(V2_JSON)
    payload = json.loads(V2_JSON.read_text(encoding="utf-8"))
    assert payload["record_count"] == 360
    assert payload["unit_count"] == 96
    assert payload["scenario_count"] == 8
    assert payload["identity_count"] == 2
    assert payload["condition_count"] == 6
    assert len(payload["public_constructs"]) == 5
    assert len(payload["contrasts"]) == 4
    assert len(payload["public_contrast_summary"]) == 20
    for row in payload["public_contrast_summary"]:
        for field in [
            "mean_difference", "positive_count", "negative_count", "zero_count",
            "direction_consistency", "scenario_mean_min", "scenario_mean_max",
            "leave_one_scenario_mean_min", "leave_one_scenario_mean_max",
        ]:
            assert field in row, field


def test_research_a_page_has_v2_results_section():
    html = (STUDY_A / "index.html").read_text(encoding="utf-8")
    assert "场景级V2结果" in html
    for slot in ['id="v2Result"', 'id="v2ConstructSelect"', 'id="v2Intro"']:
        assert slot in html, slot


def test_research_a_v2_group_is_independent_and_recoverable():
    app = (STUDY_A / "app.js").read_text(encoding="utf-8")
    # v2 is a fourth independent group with its own retry path.
    assert re.search(r"GROUP_STATE\s*=\s*\{[^}]*\bv2\b", app)
    assert "loadV2Group" in app
    assert 'runGroup("v2", loadV2Group)' in app
    # v2 rendering shows direction consistency and both scenario ranges.
    assert "direction_consistency" in app
    assert "scenario_mean_min" in app
    assert "leave_one_scenario_mean_min" in app


def test_study_card_uses_positive_extension_language():
    text = (ROOT / "docs" / "STUDY_CARD.md").read_text(encoding="utf-8")
    for phrase in ["无法逐请求还原", "不能逐请求复现", "已知方法问题", "后续研究需要优先处理"]:
        assert phrase not in text, phrase
    assert "研究A扩展路线" in text
