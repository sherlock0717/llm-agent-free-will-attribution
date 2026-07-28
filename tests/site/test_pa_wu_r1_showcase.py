"""Static, file-level checks for the Chinese PA-Wu R1 pilot showcase page.

These tests never start a real model and never make a network call. They only
read files under docs/pa-wu-r1-pilot/ and its showcase_data.json, enforcing:
the Chinese page contract, the JS interaction contract, the synthetic-demo data
contract, local resource resolution, and the forbidden-claim rules.
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
        assert (FIG_DIR / fig).is_file(), fig          # deployed (docs) figure
        assert (OUTPUT_FIG_DIR / fig).is_file(), fig    # generated (outputs) figure


def test_deployed_figures_match_generated_outputs():
    # keep the analysis product (outputs/figures) and the published product
    # (docs/.../assets/figures) byte-identical so they never diverge again.
    for fig in FIGURES:
        deployed = (FIG_DIR / fig).read_bytes()
        generated = (OUTPUT_FIG_DIR / fig).read_bytes()
        assert deployed == generated, fig


# --- 2. page contract -------------------------------------------------------

def test_lang_is_zh_cn():
    assert '<html lang="zh-CN">' in HTML


def test_title_is_chinese():
    title = re.search(r"<title>(.*?)</title>", HTML, re.S).group(1)
    assert re.search(r"[\u4e00-\u9fff]", title), title


def test_s4_section_present():
    assert 'id="s4"' in HTML


def test_section_indices_01_to_14_continuous():
    indices = re.findall(r'<span class="section-index">(\d+)</span>', HTML)
    assert indices == [f"{i:02d}" for i in range(1, 15)], indices


def test_five_figures_have_direct_src():
    for fig in FIGURES:
        assert re.search(rf'<img[^>]*src="assets/figures/{re.escape(fig)}"', HTML), fig


def test_fig5_is_referenced():
    assert "fig5_contrast_forest.png" in HTML


def test_process_demo_declaration_chinese():
    assert "流程演示数据" in HTML


def test_how_to_use_present():
    assert "如何使用本页" in HTML


def test_five_chinese_nav_entries():
    nav = HTML.split('nav class="toc"', 1)[1].split("</nav>", 1)[0]
    labels = re.findall(r'<a href="#s\d+">([^<]+)</a>', nav)
    assert len(labels) == 5, labels
    for label in labels:
        assert re.search(r"[\u4e00-\u9fff]", label), label


def test_every_image_has_chinese_alt():
    for match in re.finditer(r'<img[^>]*alt="([^"]*)"', HTML):
        assert re.search(r"[\u4e00-\u9fff]", match.group(1)), match.group(1)


def test_every_figure_has_how_to_read_caption():
    # each of the five figures sits in a <figure> whose caption starts 怎么看
    assert HTML.count("怎么看") >= 5


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
    # the direction dropdown must not surface long English decision text by default
    assert "场景方案一" in JS
    assert "场景方案二" in JS


def test_esc_closes_lightbox():
    assert "Escape" in JS


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


# --- 6. forbidden claims / hygiene -----------------------------------------

def test_public_name_is_study_b():
    assert "机器主体决策过程归因评测" in HTML
    assert "PA—Wu R1" not in HTML
    assert "PA-Wu R1" not in HTML


def test_return_to_overview_link_present():
    assert 'href="../"' in HTML
    assert "返回LLM行动者归因评测总览" in HTML


def test_process_demo_status_banner():
    assert "流程演示状态" in HTML
    assert "真实双模型运行完成后" in HTML


def test_english_source_material_preserved_in_js():
    # the referent bridge (actual English administration text) must remain
    assert '"the machine" refers to the AI system described above.' in JS


def test_pilot_page_has_no_illustrative_id():
    assert "illustrative id" not in HTML
    assert "illustrative id" not in JS
    assert "illustrative id" not in DATA.read_text(encoding="utf-8")


def test_pilot_page_states_configuration_and_unevaluated_status():
    blob = HTML + JS
    assert "配置已确定" in blob or "配置" in HTML
    assert "实证表现未评估" in blob
    assert ("不代表其实际评分行为" in blob) or ("不代表该模型的实际评分行为" in blob)


def test_no_external_cdn_assets():
    for src in re.findall(r'src="([^"]+)"', HTML):
        assert not src.startswith(("http://", "https://", "//")), src
    for href in re.findall(r'<link[^>]*href="([^"]+)"', HTML):
        assert not href.startswith(("http://", "https://", "//")), href
    assert "@import" not in CSS
    assert "http" not in CSS


# --- 7. PR B: analysis-presentation redesign (#s7 / #s8 / #s9) --------------

def test_s7_title_is_analysis_framework():
    s7 = HTML.split('id="s7"', 1)[1].split("</section>", 1)[0]
    assert "分析框架与结果呈现方式" in s7


def test_condition_profile_chart_present():
    assert 'id="conditionProfileChart"' in HTML
    # native inline SVG, no external chart library
    assert "<svg" in HTML
    for lib in ["echarts", "chart.js", "chartjs", "d3.", "react", "vue"]:
        assert lib not in HTML.lower()
        assert lib not in JS.lower()


def test_construct_selector_drives_chart_update():
    # the #s7 selector handler must refresh the SVG chart, not only the table
    assert "renderConditionProfile" in JS
    view = JS.split("function renderConstructView(", 1)[1].split("\n}", 1)[0]
    assert "renderConditionProfile(" in view


def test_synthetic_pipeline_appendix_collapsed_by_default():
    assert 'id="syntheticPipelineAppendix"' in HTML
    appx = re.search(r'<details id="syntheticPipelineAppendix"[^>]*>', HTML)
    assert appx, "appendix details tag missing"
    # a <details> without the `open` attribute is collapsed by default
    assert "open" not in appx.group(0)


def test_s8_main_area_has_no_pvalue_table():
    # the P1—P6 main area shows comparison cards; the p-value / CI table lives
    # only inside the collapsed technical appendix.
    s8 = HTML.split('id="s8"', 1)[1].split("</section>", 1)[0]
    main = s8.split('id="syntheticPipelineAppendix"', 1)[0]
    assert 'id="contrastCards"' in main
    assert 'id="contrastTable"' not in main
    assert "Holm校正p值" not in main


def test_s9_main_area_has_no_model_mean_ranking():
    s9 = HTML.split('id="s9"', 1)[1].split("</section>", 1)[0]
    assert 'id="judgeConfigCards"' in s9
    assert 'id="judgeDiffTable"' not in s9
    assert "不用于模型能力排名" in s9


def test_s9_states_empirical_performance_unevaluated():
    # #s9 model cards render an explicit "实证表现 / 未评估" configuration status
    assert "实证表现" in JS
    assert "renderJudgeConfig" in JS
    config = JS.split("function renderJudgeConfig(", 1)[1].split("\n}", 1)[0]
    assert "未评估" in config


def test_contrast_card_diffs_match_analysis_plan():
    # the reader-facing P1—P6 condition-diffs must match the pre-registered
    # analysis_plan.md contrasts exactly (P2/P4/P5 reference C0/C2, not C1/C3).
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
