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
ROOT_SECTIONS = ["overview", "program", "studies", "evidence", "methods", "future", "entries"]
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
    assert re.search(r"<h1>\s*LLM行动者归因评测\s*</h1>", html)
    for section_id in ROOT_SECTIONS:
        assert f'id="{section_id}"' in html
    for removed in ["research-a-detail", "historical-data", "mock-validation", "real-provider"]:
        assert f'id="{removed}"' not in html


def test_root_page_links_to_independent_studies(html: str):
    assert 'href="identity-process-attribution-baseline/"' in html
    assert 'href="machine-decision-process-attribution/"' in html
    assert "进入研究A页面" in html
    assert "进入研究B页面" in html


def test_root_navigation_matches_overview_sections(html: str):
    nav = html.split('id="site-nav-list"', 1)[1].split("</nav>", 1)[0]
    hrefs = re.findall(r'href="#([^"]+)"', nav)
    assert hrefs == ROOT_SECTIONS


def test_root_page_uses_positive_public_status_language(html: str):
    for phrase in ["仍待", "尚未", "不能", "无法", "不支持", "不代表", "待验证", "仍在完善"]:
        assert phrase not in html, phrase


def test_root_preview_command_uses_assembled_site(html: str):
    assert "python scripts/assemble_pages.py --output _site" in html
    assert "python -m http.server 8000 --directory _site" in html
    assert "--directory site" not in html


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
    assert "身份与决策过程归因基线" in (STUDY_A / "index.html").read_text(encoding="utf-8")
    assert "机器主体决策过程归因评测" in (STUDY_B / "index.html").read_text(encoding="utf-8")
    assert "identity-process-attribution-baseline" in INDEX.read_text(encoding="utf-8")
    assert "machine-decision-process-attribution" in INDEX.read_text(encoding="utf-8")


def test_no_old_public_repo_slug_in_pages():
    old_slug = "llm-agent-free-will-attribution"
    for page in PUBLIC_PAGES:
        assert old_slug not in page.read_text(encoding="utf-8"), page


def test_public_pages_have_no_inline_handlers():
    for page in PUBLIC_PAGES:
        content = page.read_text(encoding="utf-8")
        assert re.search(r"\son[a-z]+\s*=", content) is None, page
