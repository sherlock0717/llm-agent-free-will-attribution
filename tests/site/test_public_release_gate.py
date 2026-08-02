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
    for section_id in ["materials", "results", "robustness", "implications", "analysis", "repro"]:
        assert f'id="{section_id}"' in html
    assert "身份与决策过程" in html
    assert "DeepSeek" in html
    assert "python -m http.server 8000 --directory _site" in html


def test_research_a_results_lead_before_robustness_and_analysis():
    html = (STUDY_A / "index.html").read_text(encoding="utf-8")
    assert html.index('id="results"') < html.index('id="robustness"')
    assert html.index('id="robustness"') < html.index('id="analysis"')


def test_research_a_has_at_most_seven_main_sections():
    html = (STUDY_A / "index.html").read_text(encoding="utf-8")
    sections = re.findall(r'<section id="([^"]+)"', html)
    assert len(sections) <= 7, sections
    assert len(sections) == len(set(sections)), sections


def test_research_a_materials_example_leads_before_results():
    html = (STUDY_A / "index.html").read_text(encoding="utf-8")
    assert html.index('id="materials"') < html.index('id="results"')


def test_research_a_results_lead_before_analysis_and_repro():
    html = (STUDY_A / "index.html").read_text(encoding="utf-8")
    assert html.index('id="results"') < html.index('id="analysis"')
    assert html.index('id="results"') < html.index('id="repro"')


def test_research_a_three_fixed_findings_in_question_order():
    html = (STUDY_A / "index.html").read_text(encoding="utf-8")
    results = html.split('id="results"', 1)[1].split('id="robustness"', 1)[0]
    blocks = re.findall(r'<article class="finding-block">.*?<h3>(.*?)</h3>', results, re.S)
    assert len(blocks) == 3, blocks
    assert "过程" in blocks[0]
    assert "自由意志归因" in blocks[1]
    assert "场景" in blocks[2]


def test_research_a_first_layer_has_one_figure_per_finding():
    html = (STUDY_A / "index.html").read_text(encoding="utf-8")
    results = html.split('id="results"', 1)[1].split('id="robustness"', 1)[0]
    # every result figure sits inside a collapsed "查看完整数据" details block.
    outside_details = re.sub(r"<details.*?</details>", "", results, flags=re.S)
    assert "<img" not in outside_details


def test_research_a_hero_has_exactly_two_actions():
    html = (STUDY_A / "index.html").read_text(encoding="utf-8")
    hero = html.split('class="hero"', 1)[1].split("</header>", 1)[0]
    actions = hero.split('class="actions"', 1)[1].split("</div>", 1)[0]
    links = re.findall(r"<a\b", actions)
    assert len(links) == 2, actions
    assert 'href="#results"' in actions
    assert 'href="#materials"' in actions
    # the return-to-overview button is no longer inside the hero actions.
    assert 'href="../"' not in actions


def test_research_a_return_to_overview_still_reachable():
    html = (STUDY_A / "index.html").read_text(encoding="utf-8")
    nav = html.split('class="toc"', 1)[1].split("</nav>", 1)[0]
    assert 'href="../"' in nav
    assert "返回项目总览" in nav


def test_research_a_three_first_layer_chart_containers():
    html = (STUDY_A / "index.html").read_text(encoding="utf-8")
    for chart_id in ["processFindingChart", "identityFindingChart", "scenarioFindingChart"]:
        assert f'id="{chart_id}"' in html, chart_id


def test_research_a_first_layer_charts_are_outside_details():
    html = (STUDY_A / "index.html").read_text(encoding="utf-8")
    results = html.split('id="results"', 1)[1].split('id="robustness"', 1)[0]
    outside_details = re.sub(r"<details.*?</details>", "", results, flags=re.S)
    for chart_id in ["processFindingChart", "identityFindingChart", "scenarioFindingChart"]:
        assert f'id="{chart_id}"' in outside_details, chart_id


def test_research_a_finding_charts_have_role_and_aria_label():
    html = (STUDY_A / "index.html").read_text(encoding="utf-8")
    for chart_id in ["processFindingChart", "identityFindingChart", "scenarioFindingChart"]:
        tag = re.search(rf'<[^>]*id="{chart_id}"[^>]*>', html)
        assert tag, chart_id
        assert 'role="img"' in tag.group(0), chart_id
        assert "aria-label" in tag.group(0), chart_id


def test_research_a_finding_charts_use_native_rendering_only():
    for name in ("index.html", "app.js", "styles.css"):
        text = (STUDY_A / name).read_text(encoding="utf-8").lower()
        for lib in ["echarts", "chart.js", "chartjs", "d3.", "highcharts", "plotly"]:
            assert lib not in text, (name, lib)


def test_research_a_finding_charts_use_fixed_construct_choice():
    app = (STUDY_A / "app.js").read_text(encoding="utf-8")
    # the three first-layer charts pin a pre-registered construct/contrast and
    # never scan for the largest difference / smallest p / largest effect.
    assert 'PROCESS_FINDING_CONSTRUCT = "agency"' in app
    assert 'IDENTITY_FINDING_CONSTRUCT = "free_will_attribution"' in app
    assert 'SCENARIO_FINDING_CONSTRUCT = "agency"' in app
    assert 'SCENARIO_FINDING_CONTRAST = "A4"' in app
    # no effect-size ranking is used to choose which construct/contrast leads.
    # (Math.max for chart-axis scaling is allowed; argmax-style selection is not.)
    for token in ["largestDiff", "maxAbs", "argmax", "idxmax", ".sort((a, b) => b"]:
        assert token not in app, token


def test_research_a_no_internal_field_names_or_reading_guidance():
    html = (STUDY_A / "index.html").read_text(encoding="utf-8")
    for token in ["direction_consistency", "leave_one_scenario", "all_identities",
                  "raw字段", "V2", "阅读顺序", "如何使用本页", "建议从这里开始",
                  "本节帮助", "第一层", "第二层"]:
        assert token not in html, token


def test_research_a_technical_statistics_collapsed():
    html = (STUDY_A / "index.html").read_text(encoding="utf-8")
    assert '<details class="technical-details">' in html
    # the complete statistics table lives inside a collapsed technical block.
    repro = html.split('id="repro"', 1)[1]
    assert "查看完整统计表" in repro
    assert "查看分析方法" in repro
    assert "查看数据与代码" in repro


def test_research_a_public_copy_avoids_internal_process_wording():
    html = (STUDY_A / "index.html").read_text(encoding="utf-8")
    # 不能 / 不支持 / 不代表 are allowed: they carry necessary evidence-boundary
    # meaning. Only stalled-progress and internal-process wording is forbidden.
    for phrase in ["仍待", "尚未", "待验证", "仍在完善", "槽位", "流程演示", "阅读顺序", "如何使用本页"]:
        assert phrase not in html, phrase


def test_research_a_dynamic_groups_are_independent():
    app = (STUDY_A / "app.js").read_text(encoding="utf-8")
    assert "Promise.allSettled" in app
    assert "loadStoryGroup" in app
    assert "loadMeasurementGroup" in app
    assert "loadAnalysisGroup" in app
    assert "loadScenarioGroup" in app
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
        "research_a_scenario_summary.json",
        "research_a_robustness_summary.json",
    }
    for name in names:
        payload = json.loads((ROOT / "site" / "data" / name).read_text(encoding="utf-8"))
        assert isinstance(payload, dict)


SCENARIO_JSON = ROOT / "site" / "data" / "research_a_scenario_summary.json"


def test_research_a_scenario_public_json_is_strict_and_complete():
    check_public_json.validate_file(SCENARIO_JSON)
    payload = json.loads(SCENARIO_JSON.read_text(encoding="utf-8"))
    assert payload["record_count"] == 360
    assert payload["unit_count"] == 96
    assert payload["scenario_count"] == 8
    assert payload["identity_count"] == 2
    assert payload["condition_count"] == 6
    assert payload["analysis_version"] == "research_a_scenario_block"
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


def test_research_a_page_has_scenario_results_section():
    html = (STUDY_A / "index.html").read_text(encoding="utf-8")
    assert "V2" not in html
    for slot in ['id="scenarioResult"', 'id="scenarioConstructSelect"', 'id="scenarioIntro"']:
        assert slot in html, slot


def test_research_a_scenario_group_is_independent_and_recoverable():
    app = (STUDY_A / "app.js").read_text(encoding="utf-8")
    # scenario is a fourth independent group with its own retry path.
    assert re.search(r"GROUP_STATE\s*=\s*\{[^}]*\bscenario\b", app)
    assert "loadScenarioGroup" in app
    assert 'runGroup("scenario", loadScenarioGroup)' in app
    # scenario rendering shows direction consistency and both scenario ranges.
    assert "direction_consistency" in app
    assert "scenario_mean_min" in app
    assert "leave_one_scenario_mean_min" in app


def test_research_a_findings_are_not_ordered_by_largest_difference():
    app = (STUDY_A / "app.js").read_text(encoding="utf-8")
    # the old behaviour picked the strongest contrast to build the lead finding.
    assert "renderTakeawaysFromV2" not in app
    assert "renderTakeawaysFromScenario" in app


def test_study_card_uses_positive_extension_language():
    text = (ROOT / "docs" / "STUDY_CARD.md").read_text(encoding="utf-8")
    for phrase in ["无法逐请求还原", "不能逐请求复现", "已知方法问题", "后续研究需要优先处理"]:
        assert phrase not in text, phrase
    assert "当前稳健性报告" in text
