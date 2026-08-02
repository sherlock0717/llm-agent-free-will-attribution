"""Static, file-level checks for the study-B (machine decision-process
attribution) showcase page.

These tests never start a real model and never make a network call. They only
read files under docs/pa-wu-r1-pilot/ and its showcase_data.json, enforcing the
seven-section architecture, the JS interaction contract, the analysis-interface
example data contract, local resource resolution, and the public-name rules.
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

OUTPUT_DATA = (
    REPO_ROOT
    / "tasks"
    / "attribution_behavior"
    / "evaluations"
    / "pa_wu_r1_pilot"
    / "outputs"
    / "showcase_data.json"
)
PILOT_DIR = (
    REPO_ROOT / "tasks" / "attribution_behavior" / "evaluations" / "pa_wu_r1_pilot"
)
DEMO_REPORT = PILOT_DIR / "reports" / "demo_report.md"
ANALYSIS_PLAN = PILOT_DIR / "analysis_plan.md"

HTML = INDEX.read_text(encoding="utf-8")
JS = APP.read_text(encoding="utf-8")
CSS = STYLES.read_text(encoding="utf-8")
SHOWCASE = json.loads(DATA.read_text(encoding="utf-8"))


def _reject_nonstandard_constant(value):
    raise ValueError(f"Non-standard JSON constant: {value}")


def _strict_load(path: Path):
    """Parse JSON while rejecting NaN / Infinity / -Infinity, which Python's
    default json.loads would otherwise accept."""
    return json.loads(path.read_text(encoding="utf-8"),
                      parse_constant=_reject_nonstandard_constant)


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
    for fig in FIGURES:
        deployed = (FIG_DIR / fig).read_bytes()
        generated = (OUTPUT_FIG_DIR / fig).read_bytes()
        assert deployed == generated, fig


# --- 2. section architecture (new reading order) ----------------------------

def test_lang_is_zh_cn():
    assert '<html lang="zh-CN">' in HTML


def test_title_is_chinese():
    title = re.search(r"<title>(.*?)</title>", HTML, re.S).group(1)
    assert re.search(r"[\u4e00-\u9fff]", title), title


def test_page_has_at_most_six_main_sections():
    indices = re.findall(r'<span class="section-index">(\d+)</span>', HTML)
    assert indices == [f"{i:02d}" for i in range(1, 7)], indices


def test_semantic_section_ids_present():
    for sid in ["example", "materialAudit", "measurement", "comparison", "demo", "methods"]:
        assert f'id="{sid}"' in HTML, sid
    # the standalone overview and progress sections were folded into the hero
    # and the analysis section.
    assert '<section id="overview"' not in HTML
    assert '<section id="progress"' not in HTML


def test_material_audit_section_follows_condition_tree():
    # the material integrity audit sits right after the six-condition example.
    assert HTML.index('id="example"') < HTML.index('id="materialAudit"')
    assert HTML.index('id="materialAudit"') < HTML.index('id="measurement"')
    audit = HTML.split('id="materialAudit"', 1)[1].split("</section>", 1)[0]
    assert "材料设计经过了哪些检查" in audit
    assert "这些检查解决什么问题" in audit
    assert "materialAuditSummary" in audit


def test_material_audit_summary_json_is_present_and_strict():
    path = PAGE / "data" / "material_integrity_summary.json"
    assert path.is_file()
    payload = _strict_load(path)
    assert payload["material_count"] == 96
    assert payload["expected_count"] == 96
    assert payload["complete_grid"] is True
    assert "structural_pass_count" in payload
    assert "structural_fail_count" in payload
    assert "direction_threshold_flags" in payload
    assert payload["semantic_review_status"] == "not_assessed"


def test_material_audit_js_loads_independently():
    assert "loadMaterialAudit" in JS
    assert "material_integrity_summary.json" in JS
    # audit load must not be chained into the demo load path.
    assert "load().catch(showLoadError)" in JS


def test_legacy_anchor_aliases_s1_to_s14_present():
    for i in range(1, 15):
        assert re.search(rf'id="s{i}"[^>]*class="anchor-alias"', HTML), f"s{i}"


def test_nav_matches_sections():
    nav = HTML.split('nav class="toc"', 1)[1].split("</nav>", 1)[0]
    hrefs = re.findall(r'<a href="#([^"]+)">([^<]+)</a>', nav)
    assert [h for h, _ in hrefs] == [
        "example", "materialAudit", "measurement", "comparison", "demo", "methods",
    ], hrefs
    for _, label in hrefs:
        assert re.search(r"[\u4e00-\u9fff]", label), label


def test_hero_has_inline_metrics_not_snapshot():
    hero = HTML.split('class="hero-lead"', 1)[1].split("</header>", 1)[0]
    assert "hero-metrics" in hero
    assert "hero-snapshot" not in HTML
    buttons = re.findall(r'<a class="btn', hero)
    assert len(buttons) <= 2, buttons


def test_five_figures_have_direct_src():
    for fig in FIGURES:
        assert re.search(rf'<img[^>]*src="assets/figures/{re.escape(fig)}"', HTML), fig


def test_hero_leads_from_research_a():
    hero = HTML.split('class="hero-lead"', 1)[1].split("</header>", 1)[0]
    assert "固定机器主体" in hero
    assert "备选方案" in hero and "反馈" in hero


def test_material_example_tree_present():
    example = HTML.split('id="example"', 1)[1].split("</section>", 1)[0]
    assert "example-tree" in example
    for label in ["只给出决定", "展示备选方案", "给出明确理由",
                  "收到反馈", "反馈后维持决定", "反馈后改变决定"]:
        assert label in example, label
    for code in ["C0", "C1", "C2", "C3", "C4", "C5"]:
        assert code in example, code


def test_four_main_dimensions_in_first_layer():
    measurement = HTML.split('id="measurement"', 1)[1].split("</section>", 1)[0]
    for phrase in ["独立形成决定", "围绕目标行动", "思考与意图", "影响决定与结果"]:
        assert phrase in measurement, phrase
    assert "dimension-grid" in measurement


def test_pa5_pa8_collapsed_by_default():
    details = re.search(r'<details class="tech-details" id="supplementaryDetails"[^>]*>', HTML)
    assert details, "supplementary measurement details missing"
    assert "open" not in details.group(0)
    measurement = HTML.split('id="measurement"', 1)[1].split("</section>", 1)[0]
    before_details = measurement.split('id="supplementaryDetails"', 1)[0]
    assert "PA5" not in before_details
    assert "PA8" not in before_details


def test_comparison_uses_natural_language_questions():
    comparison = HTML.split('id="comparison"', 1)[1].split("</section>", 1)[0]
    assert "comparison-list" in comparison
    assert "展示备选方案与只给出决定相比，评价怎样变化？" in comparison
    assert "在相同反馈下，维持决定与改变决定之间有什么差异？" in comparison
    for tag in ["P1", "P2", "P3", "P4", "P5", "P6"]:
        assert f'class="p-tag">{tag}<' in comparison, tag


def test_formal_model_formula_collapsed():
    details = re.search(r'<details class="tech-details" id="analysisPlanDetails"[^>]*>', HTML)
    assert details, "analysis plan details missing"
    assert "open" not in details.group(0)
    comparison = HTML.split('id="comparison"', 1)[1].split("</section>", 1)[0]
    before_details = comparison.split('id="analysisPlanDetails"', 1)[0]
    assert "construct_score" not in before_details
    assert "random intercept" not in before_details


def test_progress_section_folded_into_analysis():
    # the standalone progress chain section was removed; the analysis section
    # carries the material-to-result pipeline instead.
    assert '<section id="progress"' not in HTML
    demo = HTML.split('id="demo"', 1)[1].split("</section>", 1)[0]
    assert "analysis-pipeline" in demo
    assert "分析流程示例" in demo


def test_analysis_interface_example_naming():
    demo = HTML.split('id="demo"', 1)[1].split("</section>", 1)[0]
    assert "条件变化与预设比较" in demo
    assert "界面中的数值用于校验分析流程、统计表和图表结构" in demo


def test_precise_model_ids_not_in_public_page():
    assert "deepseek-v4-pro" not in HTML
    assert "gpt-5.6-terra" not in HTML


def test_public_name_is_study_b():
    assert "机器主体决策过程归因" in HTML
    assert "PA—Wu R1" not in HTML
    assert "PA-Wu R1" not in HTML


def test_no_development_labels_in_html():
    for label in ["流程演示", "V2", "旧版", "新版", "当前版", "legacy"]:
        assert label not in HTML, label


def test_no_current_entry_links_in_html_or_js():
    assert "CURRENT_STUDY_CARD" not in HTML and "CURRENT_STUDY_CARD" not in JS
    assert "CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES" not in HTML
    assert "CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES" not in JS


def test_return_to_overview_link_present():
    # the return-to-overview entry is rendered into the methods entry grid.
    assert 'href: "../"' in JS
    assert "返回项目总览" in JS


def test_every_image_has_chinese_alt():
    for match in re.finditer(r'<img[^>]*alt="([^"]*)"', HTML):
        assert re.search(r"[\u4e00-\u9fff]", match.group(1)), match.group(1)


# --- 3. JS contract ---------------------------------------------------------

def test_js_checks_response_ok():
    assert "response.ok" in JS


def test_js_has_chinese_error_and_retry():
    assert "分析界面示例数据未能载入" in JS
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
    for fn in ["renderDemoMetrics", "renderStatus", "renderEntries", "renderFitSummary"]:
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
    # the #demo section, not in overview/example/measurement/comparison/progress.
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


def test_full_analysis_interface_collapsed_by_default():
    stats = re.search(r'<details class="tech-details" id="demoStatsDetails"[^>]*>', HTML)
    assert stats, "full analysis interface details missing"
    assert "open" not in stats.group(0)
    # the five pipeline figures live inside this collapsed block.
    body = HTML.split('id="demoStatsDetails"', 1)[1]
    for fig in FIGURES:
        assert fig in body, fig


def test_full_analysis_interface_contains_tables_and_five_figures():
    # inside the collapsed analysis interface: a complete condition-mean table,
    # the P1–P6 planned-contrast table, and all five pipeline figures.
    body = HTML.split('id="demoStatsDetails"', 1)[1].split("</details>", 1)[0]
    assert 'id="appxCondTable"' in body
    assert "条件均值完整表" in body
    assert 'id="contrastTable"' in body
    assert "预设对比表" in body
    for fig in FIGURES:
        assert fig in body, fig


def test_five_figures_are_lazy_loaded_not_asserted_as_loaded():
    # static tests only confirm the lazy-load markup exists; they never claim the
    # images are actually decoded. Runtime naturalWidth is verified by the browser
    # acceptance report, not here.
    body = HTML.split('id="demoStatsDetails"', 1)[1].split("</details>", 1)[0]
    lazy = re.findall(r'<img[^>]*loading="lazy"[^>]*>', body)
    assert len(lazy) >= len(FIGURES)


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
    assert "0–1" in src or "0-1" in src


def test_render_report_writes_strict_json():
    src = RENDER_REPORT.read_text(encoding="utf-8")
    assert "allow_nan=False" in src
    assert "_json_safe" in src


# --- 9. strict JSON (no NaN / Infinity) -------------------------------------

def test_docs_json_is_strict():
    payload = _strict_load(DATA)
    assert isinstance(payload, dict)


def test_outputs_json_is_strict():
    assert OUTPUT_DATA.is_file()
    payload = _strict_load(OUTPUT_DATA)
    assert isinstance(payload, dict)


def test_no_nonstandard_json_constants_in_text():
    number_token = re.compile(r"(?<![\"\\w])(NaN|-?Infinity)(?![\"\\w])")
    for path in (DATA, OUTPUT_DATA):
        text = path.read_text(encoding="utf-8")
        without_strings = re.sub(r'"(?:[^"\\]|\\.)*"', '""', text)
        hits = number_token.findall(without_strings)
        assert hits == [], (path.name, hits)


def test_captured_warnings_are_str_or_none():
    for path in (DATA, OUTPUT_DATA):
        payload = _strict_load(path)
        for row in payload["model_adjusted_results"]["fit_summary"]:
            assert "captured_warnings" in row
            value = row["captured_warnings"]
            assert value is None or isinstance(value, str), (path.name, value)


def test_docs_and_outputs_json_identical():
    assert DATA.read_bytes() == OUTPUT_DATA.read_bytes()


# --- 10. load-failure resilience (static content) ---------------------------

def test_static_research_design_baked_into_html():
    # core research design must be readable without the demo JSON: it is present
    # as static markup, not only injected by DATA-dependent JS.
    for token in ["独立形成决定", "围绕目标行动", "思考与意图", "影响决定与结果",
                  "construct_score", "阶段一：决定信息", "阶段二：反馈后行为"]:
        assert token in HTML, token


def test_demo_error_panel_and_content_wrapper_present():
    assert 'id="demoError"' in HTML
    assert 'id="demoContent"' in HTML


def test_load_failure_keeps_design_and_shows_demo_error():
    handler = JS.split("function showLoadError(", 1)[1]
    assert "demoContent" in handler
    assert "demoError" in handler
    assert "data/showcase_data.json" in handler
    assert "查看技术错误" in handler
    assert "研究设计和分析计划仍可浏览" in handler


def test_static_render_initializes_once_before_load():
    load_fn = JS.split("async function load(", 1)[1].split("\n}", 1)[0]
    assert "renderStatic()" not in load_fn
    tail = JS.rsplit("renderStatic();", 1)[1]
    assert "load().catch(showLoadError);" in tail
    assert "load().catch(showLoadError)" in JS


def test_captured_warnings_null_shows_placeholder():
    assert "无记录" in JS
    warn_fn = JS.split("function warningText(", 1)[1].split("\n}", 1)[0]
    assert "无记录" in warn_fn


# --- 11. research-copy refinements ------------------------------------------

def test_html_free_of_time_and_comparative_negations():
    for token in ["研究A在早期探索", "而不是机器主体本身", "这些都不依赖真实模型输出"]:
        assert token not in HTML, token


def test_html_has_precise_p_value_definition():
    assert "在零假设成立时，获得当前检验统计量或更极端值的概率" in HTML


def test_render_report_docstring_free_of_stacked_negations():
    head = RENDER_REPORT.read_text(encoding="utf-8").split('"""', 2)[1]
    assert "MACHINE-ONLY R1" not in head
    assert "NO ai/human" not in head


# --- 12. reports + analysis-plan alignment ----------------------------------

def test_condition_meta_roles_match_contrast_sides():
    block = JS.split("const CONDITION_META", 1)[1].split("\n};", 1)[0]
    roles = dict(re.findall(r'(C\d):\s*\{[^}]*role:\s*"([^"]+)"', block))
    assert "P1、P2的参考条件" == roles["C0"]
    assert "P1的比较条件" == roles["C1"]
    assert "P2的比较条件" in roles["C2"] and "P3、P4、P5的参考条件" in roles["C2"]
    assert "P3的比较条件" == roles["C3"]
    assert "P4的比较条件" in roles["C4"] and "P6的参考条件" in roles["C4"]
    assert "P5、P6的比较条件" == roles["C5"]


def test_demo_report_public_naming_and_no_nan():
    text = DEMO_REPORT.read_text(encoding="utf-8")
    for bad in ["PA—Wu R1", "PA-Wu R1", "- **IN**: nan", "- **PA8**: nan"]:
        assert bad not in text, bad
    assert not re.search(r"\*\*\w+\*\*: *nan", text)
    assert text.splitlines()[0] == (
        "# Study B — Machine Decision-Process Attribution — Flow Demonstration Report"
    )


def test_render_report_warning_filter_uses_pd_notna():
    src = RENDER_REPORT.read_text(encoding="utf-8")
    assert "pd.notna(warning)" in src


def test_analysis_plan_effect_structure_consistent():
    text = ANALYSIS_PLAN.read_text(encoding="utf-8")
    assert "fixed **block**" in text or "fixed block" in text
    assert "random intercept" in text
    assert "scenario random effect" not in text


def test_five_figures_outputs_and_docs_byte_identical():
    for name in FIGURES:
        assert (FIG_DIR / name).read_bytes() == (OUTPUT_FIG_DIR / name).read_bytes(), name


def test_both_showcase_json_strict_and_identical():
    a = _strict_load(DATA)
    b = _strict_load(OUTPUT_DATA)
    assert a == b
    assert DATA.read_bytes() == OUTPUT_DATA.read_bytes()
