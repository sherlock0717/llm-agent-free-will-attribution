"""Static checks for the project overview and assembled research pages."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
INDEX = SITE / "index.html"
CSS = SITE / "assets" / "css" / "site.css"
JS = SITE / "assets" / "js" / "site.js"
DATA = SITE / "data"
STUDY_A = ROOT / "docs" / "identity-process-attribution-baseline"
STUDY_B = ROOT / "docs" / "pa-wu-r1-pilot"

ROOT_JSON = [
    "site_summary.json",
    "showcase_story.json",
    "measurement_summary.json",
    "analysis_results.json",
    "historical_results.json",
    "engineering_status.json",
    "evidence_matrix.json",
    "reproducibility_summary.json",
]
ROOT_SECTIONS = ["overview", "findings", "studies", "build", "implications", "methods"]
ROOT_H1 = "语言模型如何理解一个行动者的决定"
RESULTS_DOC = ROOT / "docs" / "RESULTS_AND_PRACTICAL_IMPLICATIONS.md"
PUBLIC_PAGES = [INDEX, STUDY_A / "index.html", STUDY_B / "index.html"]


@pytest.fixture(scope="module")
def html() -> str:
    return INDEX.read_text(encoding="utf-8")


def test_public_sources_exist():
    paths = [
        INDEX,
        CSS,
        JS,
        STUDY_A / "index.html",
        STUDY_A / "app.js",
        STUDY_A / "styles.css",
        STUDY_B / "index.html",
        STUDY_B / "app.js",
        STUDY_B / "styles.css",
        RESULTS_DOC,
    ]
    for path in paths:
        assert path.is_file(), path
    for name in ROOT_JSON:
        assert (DATA / name).is_file(), name


def test_root_page_is_project_overview(html: str):
    assert "<title>LLM行动者归因评测</title>" in html
    assert ROOT_H1 in html
    for section_id in ROOT_SECTIONS:
        assert f'id="{section_id}"' in html
    removed = ["research-a-detail", "historical-data", "mock-validation", "real-provider", "future", "entries", "evidence"]
    for section_id in removed:
        assert f'id="{section_id}"' not in html


def test_root_page_has_ordered_portfolio_sections(html: str):
    sections = re.findall(r'<section id="([^"]+)"', html)
    assert sections == ROOT_SECTIONS, sections
    assert len(sections) == len(set(sections)), "duplicate section id"


def test_root_hero_links_directly_to_both_studies(html: str):
    hero = html.split('id="overview"', 1)[1].split("</section>", 1)[0]
    buttons = re.findall(r'<a class="btn', hero)
    assert len(buttons) == 2
    assert 'href="identity-process-attribution-baseline/"' in hero
    assert 'href="machine-decision-process-attribution/"' in hero
    assert "进入研究A" in hero
    assert "进入研究B" in hero


def test_root_hero_uses_plain_research_question(html: str):
    hero = html.split('id="overview"', 1)[1].split("</section>", 1)[0]
    assert ROOT_H1 in hero
    for phrase in [
        "在研究A中，仅改变身份和过程写法",
        "当前结果来自研究A",
        "本页不把研究B",
        "项目关注的核心不是",
    ]:
        assert phrase not in hero, phrase


def test_root_hero_has_two_linked_research_cards(html: str):
    hero = html.split('id="overview"', 1)[1].split("</section>", 1)[0]
    assert 'aria-label="两项研究入口"' in hero
    assert "360次模型评分、主要结果与场景分析" in hero
    assert "96条材料、评价维度与分析方案" in hero


def test_root_section_order_is_findings_then_studies_then_questions(html: str):
    assert html.index('id="findings"') < html.index('id="studies"')
    assert html.index('id="studies"') < html.index('id="build"')
    assert html.index('id="build"') < html.index('id="implications"')
    assert html.index('id="implications"') < html.index('id="methods"')


def test_root_findings_has_three_finding_blocks(html: str):
    findings = html.split('id="findings"', 1)[1].split("</section>", 1)[0]
    assert len(re.findall(r'<article class="finding-block">', findings)) == 3


def test_root_studies_have_explicit_page_entries(html: str):
    studies = html.split('id="studies"', 1)[1].split("</section>", 1)[0]
    for phrase in [
        "身份与决策过程归因",
        "机器主体决策过程归因",
        "进入研究A结果页",
        "进入研究B设计页",
    ]:
        assert phrase in studies
    assert 'href="identity-process-attribution-baseline/"' in studies
    assert 'href="machine-decision-process-attribution/"' in studies


def test_root_questions_cover_measurement_agent_and_product(html: str):
    implications = html.split('id="implications"', 1)[1].split("</section>", 1)[0]
    for phrase in [
        "测量的究竟是哪一层",
        "Agent是否真正改变了后续行为",
        "产品如何影响用户判断",
    ]:
        assert phrase in implications
    assert "训练数据与质检" not in implications
    assert "这些结果对实际评测意味着什么" not in implications


def test_root_has_no_support_not_support_section(html: str):
    for phrase in [
        "证据支持什么，也不支持什么",
        "当前结果支持的是",
        "当前结果不支持",
        "证据边界",
    ]:
        assert phrase not in html, phrase


def test_root_page_has_no_internal_reading_guidance(html: str):
    for phrase in [
        "先看懂问题",
        "阅读顺序",
        "如何使用本页",
        "信息架构",
        "当前范围覆盖",
        "已形成完整链路",
        "槽位",
        "judge_slot",
        "流程演示",
        "正式模型评分即将开始",
    ]:
        assert phrase not in html, phrase


def test_root_navigation_matches_overview_sections(html: str):
    nav = html.split('id="site-nav-list"', 1)[1].split("</nav>", 1)[0]
    hrefs = re.findall(r'href="#([^"]+)"', nav)
    assert hrefs == ROOT_SECTIONS[1:], hrefs


def test_root_page_has_no_research_a_result_statistics_hardcoded(html: str):
    for token in ["12.189", "0.2699", "4.308", "5.200", "1296.23"]:
        assert token not in html


def test_root_javascript_has_static_fallback_and_single_data_dependency():
    script = JS.read_text(encoding="utf-8")
    assert 'fetch("data/showcase_story.json"' in script
    assert "renderStory" in script
    assert "项目总览使用页面内置说明" in script
    assert "Promise.all" not in script
    for old_renderer in ["renderConditionProfile", "renderMediation", "renderMockQuality", "renderReadiness"]:
        assert old_renderer not in script


def test_root_styles_are_responsive_and_local():
    css = CSS.read_text(encoding="utf-8")
    assert "@media (max-width: 760px)" in css
    assert "@media (max-width: 420px)" in css
    assert ".bridge-node:hover" in css
    assert "http://" not in css and "https://" not in css


def test_root_local_links_resolve_before_assembly(html: str):
    ids = set(re.findall(r'id="([^"]+)"', html))
    assembled_routes = {
        "identity-process-attribution-baseline/": STUDY_A / "index.html",
        "machine-decision-process-attribution/": STUDY_B / "index.html",
    }
    for href in re.findall(r'href="([^"]+)"', html):
        if href.startswith(("https://", "http://", "mailto:")):
            continue
        if href.startswith("#"):
            assert href[1:] in ids, href
            continue
        if href in assembled_routes:
            assert assembled_routes[href].is_file(), href
            continue
        assert (SITE / href).exists(), href


def test_public_page_assets_are_local():
    for page in PUBLIC_PAGES:
        content = page.read_text(encoding="utf-8")
        for src in re.findall(r'<script[^>]+src="([^"]+)"', content):
            assert not src.startswith(("http://", "https://", "//")), (page, src)
        for href in re.findall(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"', content):
            assert not href.startswith(("http://", "https://", "//")), (page, href)


def test_root_json_is_valid_utf8_without_bom():
    for name in ROOT_JSON:
        path = DATA / name
        assert not path.read_bytes().startswith(b"\xef\xbb\xbf"), name
        assert isinstance(json.loads(path.read_text(encoding="utf-8")), dict)


def test_public_names_and_routes_are_consistent():
    assert "身份与决策过程" in (STUDY_A / "index.html").read_text(encoding="utf-8")
    assert "机器主体决策过程归因" in (STUDY_B / "index.html").read_text(encoding="utf-8")
    assert "identity-process-attribution-baseline" in INDEX.read_text(encoding="utf-8")
    assert "machine-decision-process-attribution" in INDEX.read_text(encoding="utf-8")


def test_public_pages_have_no_development_labels():
    for page in PUBLIC_PAGES:
        content = page.read_text(encoding="utf-8")
        for label in ["V2", "旧版", "新版", "当前版", "legacy", "流程演示", "PA—Wu", "PA-Wu"]:
            assert label not in content, (page.name, label)


def test_public_pages_have_no_internal_slot_wording():
    for page in PUBLIC_PAGES:
        content = page.read_text(encoding="utf-8")
        for label in ["槽位", "评判槽位", "双评判槽位", "judge_slot", "judge slot", "评分槽"]:
            assert label not in content, (page.name, label)


def test_no_old_public_repo_slug_in_pages():
    old_slug = "llm-agent-free-will-attribution"
    for page in PUBLIC_PAGES:
        assert old_slug not in page.read_text(encoding="utf-8"), page


def test_public_pages_have_no_inline_handlers():
    for page in PUBLIC_PAGES:
        content = page.read_text(encoding="utf-8")
        assert re.search(r"\son[a-z]+\s*=", content) is None, page


def test_root_findings_numbers_come_from_robustness_json():
    script = JS.read_text(encoding="utf-8")
    assert "loadFindingMetrics" in script
    assert "research_a_robustness_summary.json" in script
    assert "data-finding-metric" in script
    assert 'fetch("data/showcase_story.json"' in script
    assert "Promise.all" not in script


def test_root_findings_use_correct_public_findings_sources():
    script = JS.read_text(encoding="utf-8")
    for token in [
        "public_findings",
        "process_information",
        "identity_label",
        "full_effect",
        "overall_identity_difference",
        "process_effect_range",
    ]:
        assert token in script
    assert "absolute_shrink_ratio" not in script


def test_root_identity_finding_is_scoped_to_free_will():
    html = INDEX.read_text(encoding="utf-8")
    script = JS.read_text(encoding="utf-8")
    findings = html.split('id="findings"', 1)[1].split("</section>", 1)[0]
    assert "人类标签" in findings and "自由意志归因" in findings
    assert "过程条件身份配对" in script
    assert "这一结果聚焦自由意志归因维度" in script
    assert "A4" not in script.split("identity_label", 1)[1].split("scenario_dependence", 1)[0]
    assert "独立实验" not in html and "独立样本" not in html


def test_root_process_finding_uses_json_denominator():
    script = JS.read_text(encoding="utf-8")
    assert len(script.split("proc.full_effect", 1)) == 2
    assert "1.263" not in script
    assert "16/16" not in script


def test_length_section_avoids_misleading_wording():
    paths = [
        INDEX,
        STUDY_A / "index.html",
        STUDY_A / "app.js",
        ROOT / "docs" / "research_a_robustness_report.md",
        RESULTS_DOC,
        ROOT / "README.md",
        ROOT / "docs" / "RESEARCH_PROGRAM.md",
    ]
    banned = [
        "控制长度后效果更强",
        "排除文本长度影响",
        "排除长度影响",
        "调整后更稳健",
        "中度共线性",
        "长度不是混杂因素",
        "已排除长度混杂",
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for phrase in banned:
            assert phrase not in text, (path.name, phrase)


def test_direction_count_described_as_descriptive_statistic():
    text = (STUDY_A / "index.html").read_text(encoding="utf-8")
    assert "描述性统计" in text
    assert "不等同于独立样本数量或统计显著性" in text


def test_root_has_results_document_entry(html: str):
    assert "RESULTS_AND_PRACTICAL_IMPLICATIONS.md" in html
    assert RESULTS_DOC.is_file()


def test_study_a_has_robustness_section():
    study_html = (STUDY_A / "index.html").read_text(encoding="utf-8")
    assert 'id="robustness"' in study_html
    assert "这些变化有多稳定" in study_html
    assert 'id="evidenceStatusTable"' in study_html
    assert "稳健性与限制" in study_html


def test_study_a_robustness_conclusions_come_from_json():
    app = (STUDY_A / "app.js").read_text(encoding="utf-8")
    assert "research_a_robustness_summary.json" in app
    assert "loadRobustnessGroup" in app
    assert "renderRobustnessModules" in app
    payload = json.loads((DATA / "research_a_robustness_summary.json").read_text(encoding="utf-8"))
    assert payload["data_role"] == "research_a_existing_data_robustness"


def test_study_b_has_material_audit_section():
    study_html = (STUDY_B / "index.html").read_text(encoding="utf-8")
    assert 'id="materialAudit"' in study_html
    assert "材料设计经过了哪些检查" in study_html
    stats = re.search(r'<details class="tech-details" id="demoStatsDetails"[^>]*>', study_html)
    assert stats and "open" not in stats.group(0)


def test_study_b_has_no_formal_primary_result_section():
    study_html = (STUDY_B / "index.html").read_text(encoding="utf-8")
    assert '<section id="results"' not in study_html
    for phrase in ["主要正式结果", "正式模型评分即将开始", "正式结果已产出"]:
        assert phrase not in study_html, phrase


def test_static_site_no_reading_flow_or_slot_wording_anywhere():
    for page in PUBLIC_PAGES:
        content = page.read_text(encoding="utf-8")
        for phrase in ["先看", "阅读顺序", "如何使用本页", "槽位"]:
            assert phrase not in content, (page.name, phrase)
