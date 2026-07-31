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
ROOT_SECTIONS = ["overview", "program", "studies", "evidence", "methods"]
PUBLIC_PAGES = [INDEX, STUDY_A / "index.html", STUDY_B / "index.html"]


@pytest.fixture(scope="module")
def html() -> str:
    return INDEX.read_text(encoding="utf-8")


def test_public_sources_exist():
    for path in [INDEX, CSS, JS, STUDY_A / "index.html", STUDY_A / "app.js", STUDY_A / "styles.css", STUDY_B / "index.html", STUDY_B / "app.js", STUDY_B / "styles.css"]:
        assert path.is_file(), path
    for name in ROOT_JSON:
        assert (DATA / name).is_file(), name


def test_root_page_is_project_overview(html: str):
    assert "<title>LLM行动者归因评测</title>" in html
    assert re.search(r"<h1>同一个决定，为什么写法一变，模型评价也会变？</h1>", html)
    for section_id in ROOT_SECTIONS:
        assert f'id="{section_id}"' in html
    for removed in ["research-a-detail", "historical-data", "mock-validation", "real-provider", "future", "entries"]:
        assert f'id="{removed}"' not in html


def test_root_page_has_at_most_five_main_sections(html: str):
    sections = re.findall(r'<section id="([^"]+)"', html)
    assert len(sections) <= 5, sections
    assert sections == ROOT_SECTIONS


def test_root_hero_has_at_most_two_buttons(html: str):
    hero = html.split('id="overview"', 1)[1].split("</section>", 1)[0]
    buttons = re.findall(r'<a class="btn', hero)
    assert len(buttons) <= 2, buttons


def test_root_hero_has_no_number_snapshot(html: str):
    hero = html.split('id="overview"', 1)[1].split("</section>", 1)[0]
    assert "项目现在包含什么" not in hero
    assert "fact-grid" not in hero
    assert "research-bridge" in hero


def test_root_page_leads_with_a_concrete_question(html: str):
    hero = html.split('id="overview"', 1)[1].split("</section>", 1)[0]
    assert "同一个决定，为什么写法一变" in hero
    program = html.split('id="program"', 1)[1].split("</section>", 1)[0]
    assert "路线" in program or "配送" in program
    assert "story-flow" in program
    studies = html.split('id="studies"', 1)[1].split("</section>", 1)[0]
    assert "研究A比较" in studies and "拆" in studies


def test_root_evidence_uses_finding_blocks_not_table(html: str):
    evidence = html.split('id="evidence"', 1)[1].split("</section>", 1)[0]
    assert "finding-block" in evidence
    assert "<table" not in evidence


def test_root_page_has_no_internal_reading_guidance(html: str):
    for phrase in [
        "先看懂问题", "再看例子", "阅读顺序", "如何使用本页", "建议从这里开始",
        "第一次访问", "信息架构", "叙事主线", "渐进式披露", "本节帮助", "本页按照",
        "读者应该先看", "首次访问者", "第一层", "第二层", "第三层",
    ]:
        assert phrase not in html, phrase


def test_root_page_links_to_independent_studies(html: str):
    assert 'href="identity-process-attribution-baseline/"' in html
    assert 'href="machine-decision-process-attribution/"' in html
    assert "查看研究A结果" in html
    assert "查看研究B设计" in html


def test_root_navigation_matches_overview_sections(html: str):
    nav = html.split('id="site-nav-list"', 1)[1].split("</nav>", 1)[0]
    hrefs = re.findall(r'href="#([^"]+)"', nav)
    assert hrefs == ROOT_SECTIONS


def test_root_page_uses_positive_public_status_language(html: str):
    for phrase in ["仍待", "尚未", "不能", "无法", "不支持", "不代表", "待验证", "仍在完善"]:
        assert phrase not in html, phrase


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
