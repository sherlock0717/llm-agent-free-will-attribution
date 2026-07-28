"""Static, file-level checks for the study-B (machine decision-process
attribution) showcase page.

These tests never start a real model and never make a network call. They only
read files under docs/pa-wu-r1-pilot/ and its showcase_data.json, enforcing the
seven-section architecture, the JS interaction contract, the synthetic-demo data
contract, local resource resolution, and the public-name rules.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PAGE = REPO_ROOT / "docs" / "pa-wu-r1-pilot"
INDEX = PAGE / "index.html"
APP = PAGE / "app.js"
STYLES = PAGE / "styles.css"
DATA = PAGE / "data" / "showcase_data.json"
FIG_DIR = PAGE / "assets" / "figures"
OUTPUT_FIG_DIR = (
    REPO_ROOT
    / "tasks"
    / "attribution_behavior"
    / "evaluations"
    / "pa_wu_r1_pilot"
    / "outputs"
    / "figures"
)
RENDER_REPORT = (
    REPO_ROOT
    / "tasks"
    / "attribution_behavior"
    / "evaluations"
    / "pa_wu_r1_pilot"
    / "scripts"
    / "render_report.py"
)

FIGURES = [
    "fig1_condition_construct_means.png",
    "fig2_model_adjusted_contrasts.png",
    "fig3_model_profiles.png",
    "fig4_scenario_construct_heatmap.png",
    "fig5_contrast_forest.png",
]

HTML = INDEX.read_text(encoding="utf-8")
JS = APP.read_text(encoding="utf-8")
CSS = STYLES.read_text(encoding="utf-8")
SHOWCASE = json.loads(DATA.read_text(encoding="utf-8"))


# --- 1. required files ------------------------------------------------------

def test_required_files_exist():
    assert INDEX.is_file()
    assert APP.is_file()
    assert STYLES.is_file()
    assert DATA.is_file()
    for fig in FIGURES:
        assert (FIG_DIR / fig).is_file(), fig
        assert (OUTPUT_FIG_DIR / fig).is_file(), fig


def test_deployed_figures_match_generated_outputs():
    # keep the analysis product (outputs/figures) and the published product
    # (docs/.../assets/figures) byte-identical so they never diverge again.
    for fig in FIGURES:
        deployed = (FIG_DIR / fig).read_bytes()
        generated = (OUTPUT_FIG_DIR / fig).read_bytes()
        assert deployed == generated, fig


# --- 2. seven-section architecture ------------------------------------------

def test_lang_is_zh_cn():
    assert '<html lang="zh-CN">' in HTML


def test_title_is_chinese():
    title = re.search(r"<title>(.*?)</title>", HTML, re.S).group(1)
    assert re.search(r"[\u4e00-\u9fff]", title), title


def test_page_has_seven_sections_numbered_01_to_07():
    indices = re.findall(r'<span class="section-index">(\d+)</span>', HTML)
    assert indices == [f"{i:02d}" for i in range(1, 8)], indices


def test_semantic_section_ids_present():
    for sid in ["overview", "constructs", "design", "materials",
                "analysis", "demo", "status"]:
        assert f'id="{sid}"' in HTML, sid


def test_legacy_anchor_aliases_s1_to_s14_present():
    for i in range(1, 15):
        assert re.search(rf'id="s{i}"[^>]*class="anchor-alias"', HTML), f"s{i}"


def test_nav_has_seven_entries_matching_sections():
    nav = HTML.split('nav class="toc"', 1)[1].split("</nav>", 1)[0]
    hrefs = re.findall(r'<a href="#([^"]+)">([^<]+)</a>', nav)
    assert [h for h, _ in hrefs] == [
        "overview", "constructs", "design", "materials",
        "analysis", "demo", "status",
    ], hrefs
    for _, label in hrefs:
        assert re.search(r"[\u4e00-\u9fff]", label), label


def test_five_figures_have_direct_src():
    for fig in FIGURES:
        assert re.search(rf'<img[^>]*src="assets/figures/{re.escape(fig)}"', HTML), fig


def test_process_demo_declaration_chinese():
    assert "流程演示数据" in HTML


def test_public_name_is_study_b():
    assert "机器主体决策过程归因评测" in HTML
    assert "PA—Wu R1" not in HTML
    assert "PA-Wu R1" not in HTML


def test_return_to_overview_link_present():
    assert 'href="../"' in HTML
    assert "返回项目总览" in HTML


def test_no_old_section_names():
    for bad in ["方法边界", "真实数据替换流程", "旧图表", "材料示例"]:
        assert bad not in HTML, bad


def test_no_current_r1_wording():
    assert "当前R1" not in HTML
    assert "当前R1" not in JS


def test_every_image_has_chinese_alt():
    for match in re.finditer(r'<img[^>]*alt="([^"]*)"', HTML):
        assert re.search(r"[\u4e00-\u9fff]", match.group(1)), match.group(1)


# --- 3. JS contract ---------------------------------------------------------

def test_js_checks_response_ok():
    assert "response.ok" in JS


def test_js_has_chinese_error_and_retry():
    assert "数据加载失败" in JS
    assert "重新加载" in JS
    assert "showLoadError" in JS


def test_scenario_meta_has_eight_entries():
    block = JS.split("const SCENARIO_META", 1)[1].split("};", 1)[0]
    keys = re.findall(r"s\d_[a-z_]+:", block)
    assert len(keys) == 8, keys


def test_condition_meta_has_six_entries():
    block = JS.split("const CONDITION_META", 1)[1].split("};", 1)[0]
    keys = re.findall(r"\bC[0-5]:\s*\{", block)
    assert len(keys) == 6, keys


def test_construct_meta_has_six_entries():
    block = JS.split("const CONSTRUCT_META", 1)[1].split("};", 1)[0]
    for key in ["IN", "GO", "MSI", "IC", "PA5", "PA8"]:
        assert re.search(rf"\b{key}:\s*\{{", block), key


def test_js_does_not_use_json_stringify_for_display():
    assert "JSON.stringify" not in JS


def test_direction_labels_are_pure_chinese():
    assert "场景方案一" in JS
    assert "场景方案二" in JS


def test_esc_closes_lightbox():
    assert "Escape" in JS


def test_no_boundary_translations_constant():
    assert "BOUNDARY_TRANSLATIONS" not in JS


def test_no_removed_render_functions():
    for fn in ["renderJudgeConfig", "renderMaterialExamples", "renderBoundaries"]:
        assert fn not in JS, fn


def test_merged_and_new_render_functions_present():
    for fn in ["renderJudgeSummary", "renderDemoMetrics", "renderStatus"]:
        assert fn in JS, fn


def test_no_judge_config_or_material_examples_containers():
    assert "judgeConfigCards" not in HTML
    assert "materialExamples" not in HTML


def test_contrast_cards_use_comparison_and_reading():
    block = JS.split("const CONTRAST_CARDS", 1)[1].split("\n];", 1)[0]
    assert "comparison:" in block
    assert "reading:" in block
    assert "allow:" not in block
    assert "forbid:" not in block


def test_status_notes_constant_present():
    assert "STATUS_NOTES" in JS


# --- 4. data contract -------------------------------------------------------

def test_data_status_is_synthetic_demo():
    assert SHOWCASE["data_status"] == "synthetic_demo"


def test_material_and_response_counts():
    q = SHOWCASE["quality_summary"]
    assert q["n_materials"] == 96
    assert q["n_responses"] == 192


def test_scenarios_count_is_eight():
    assert len(SHOWCASE["scenarios"]) == 8


def test_per_condition_scenario_direction_balance():
    balance = SHOWCASE["material_balance"]
    assert all(v == 16 for v in balance["per_condition"].values())
    assert all(v == 12 for v in balance["per_scenario"].values())
    assert balance["per_direction"]["A"] == 48
    assert balance["per_direction"]["B"] == 48


def test_figure_paths_are_five():
    assert len(SHOWCASE["figure_paths"]) == 5


def test_model_contrasts_have_stat_fields():
    contrasts = SHOWCASE["model_adjusted_results"]["contrasts"]
    assert len(contrasts) == 36
    for row in contrasts:
        for field in ["standard_error", "ci95_low", "ci95_high",
                      "p_value", "p_value_holm"]:
            assert field in row, field


# --- 5. resource references -------------------------------------------------

def test_local_html_src_files_exist():
    for src in re.findall(r'src="([^"]+)"', HTML):
        if src.startswith(("http://", "https://", "//")):
            continue
        assert (PAGE / src).is_file(), src


def test_css_and_js_paths_resolve():
    for href in re.findall(r'<link[^>]*href="([^"]+)"', HTML):
        if not href.startswith(("http", "//")):
            assert (PAGE / href).is_file(), href
    scripts = re.findall(r'<script[^>]*src="([^"]+)"', HTML)
    assert scripts
    for src in scripts:
        assert (PAGE / src).is_file(), src


def test_png_signatures_valid():
    for fig in FIGURES:
        assert (FIG_DIR / fig).read_bytes()[:8] == b"\x89PNG\r\n\x1a\n", fig


def test_no_external_cdn_assets():
    for src in re.findall(r'src="([^"]+)"', HTML):
        assert not src.startswith(("http://", "https://", "//")), src
    for href in re.findall(r'<link[^>]*href="([^"]+)"', HTML):
        assert not href.startswith(("http://", "https://", "//")), href
    assert "@import" not in CSS
    assert "http" not in CSS


# --- 6. demo concentration + collapsed technical tables ---------------------

def test_synthetic_stats_only_in_demo_section():
    # the p-value / CI contrast table and the SVG profile chart must live inside
    # the #demo section, not in overview/constructs/design/materials/analysis.
    demo = HTML.split('id="demo"', 1)[1].split("</section>", 1)[0]
    assert 'id="contrastTable"' in demo
    assert 'id="conditionProfileChart"' in demo
    before_demo = HTML.split('id="demo"', 1)[0]
    assert 'id="contrastTable"' not in before_demo
    assert 'id="conditionProfileChart"' not in before_demo


def test_demo_statistics_table_collapsed_by_default():
    stats = re.search(r'<details class="tech-details" id="demoStatsDetails"[^>]*>', HTML)
    assert stats, "demo stats details missing"
    assert "open" not in stats.group(0)


def test_pipeline_figures_collapsed_by_default():
    figs = re.search(r'<details class="tech-details" id="pipelineFigures"[^>]*>', HTML)
    assert figs, "pipeline figures details missing"
    assert "open" not in figs.group(0)


def test_demo_marks_present():
    assert 'class="demo-mark"' in HTML


def test_condition_profile_chart_present_native_svg():
    assert 'id="conditionProfileChart"' in HTML
    assert "<svg" in HTML
    for lib in ["echarts", "chart.js", "chartjs", "d3.", "react", "vue"]:
        assert lib not in HTML.lower()
        assert lib not in JS.lower()


def test_construct_selector_drives_chart_update():
    assert "renderConditionProfile" in JS
    view = JS.split("function renderConstructView(", 1)[1].split("\n}", 1)[0]
    assert "renderConditionProfile(" in view


# --- 7. contrast diffs + English source material ----------------------------

def test_contrast_card_diffs_match_analysis_plan():
    block = JS.split("const CONTRAST_CARDS", 1)[1].split("\n];", 1)[0]
    found = dict(re.findall(r'id:\s*"(P[1-6])",\s*diff:\s*"([^"]+)"', block))
    assert found == {
        "P1": "C1−C0",
        "P2": "C2−C0",
        "P3": "C3−C2",
        "P4": "C4−C2",
        "P5": "C5−C2",
        "P6": "C5−C4",
    }, found


def test_english_source_material_preserved_in_js():
    assert '"the machine" refers to the AI system described above.' in JS


# --- 8. scale-safe figures / render_report ----------------------------------

def test_render_report_has_native_scale_bounds():
    src = RENDER_REPORT.read_text(encoding="utf-8")
    assert "NATIVE_SCALE_BOUNDS" in src


def test_render_report_uses_theoretical_0_1_mapping_for_heatmap():
    src = RENDER_REPORT.read_text(encoding="utf-8")
    # fig4 heatmap maps native scores to a theoretical 0–1 in-scale position
    assert "0–1" in src or "0-1" in src
