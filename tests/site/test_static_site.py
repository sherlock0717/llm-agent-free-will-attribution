"""Static checks for the public showcase page (SHOWCASE-RELEASE-001).

No network calls; only reads files under site/. These enforce the frozen public
naming, the continuous section structure, and the public-content rules
(no internal task codes, no target-audience wording, no old repo name, no
hardcoded statistics, four-state provenance).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import struct
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SITE = REPO_ROOT / "site"
INDEX = SITE / "index.html"
CSS = SITE / "assets" / "css" / "site.css"
JS = SITE / "assets" / "js" / "site.js"
DATA = SITE / "data"
FIGURES = SITE / "assets" / "figures"

# Relative links that are NOT served from site/ directly, but assembled into the
# deployed Pages tree by .github/workflows/pages.yml:
#   site/                 -> _site/
#   docs/pa-wu-r1-pilot/  -> _site/pa-wu-r1-pilot/
# For these routes the test verifies the real assembled source exists (the
# pilot's index.html), rather than requiring a copy inside site/. This is an
# explicit per-route mapping, not a wildcard exemption.
DEPLOYED_ROUTE_SOURCES = {
    "pa-wu-r1-pilot/": (
        REPO_ROOT / "docs" / "pa-wu-r1-pilot" / "index.html"
    ),
}

HTML = INDEX.read_text(encoding="utf-8")
JS_SRC = JS.read_text(encoding="utf-8")
CSS_SRC = CSS.read_text(encoding="utf-8")

JSON_FILES = [
    "site_summary.json",
    "showcase_story.json",
    "measurement_summary.json",
    "analysis_results.json",
    "historical_results.json",
    "engineering_status.json",
    "evidence_matrix.json",
    "reproducibility_summary.json",
]

SECTION_IDS = [
    "overview", "research-question", "design-measurement", "research-sources",
    "historical-data", "analysis", "results-summary", "evaluation-core",
    "mock-validation", "real-provider", "reproducibility", "future-work",
]

SELECTED_FIGURES = [
    "mean_agency.png",
    "mean_free_will_attribution.png",
    "mean_subjective_process_completeness.png",
]

MAIN_TITLE = "LLM机器主体归因评测"
SUBTITLE = "PA—Wu R1仅机器主体研究"
NEW_SLUG = "llm-attribution-behavior-evaluation"
OLD_SLUG = "llm-agent-free-will-attribution"

# The public README title is now unified to the current machine-only research.
README_TITLE = "LLM机器主体归因评测"

# nav entries that must NOT sit in the first-level navigation any more (they
# belong to the legacy archive and moved under 方法与复现 / 历史归档).
FORBIDDEN_TOP_NAV = ["模拟运行验证", "真实模型接入", "评测核心"]


# --- files / structure -----------------------------------------------------

def test_core_files_exist():
    assert INDEX.is_file() and CSS.is_file() and JS.is_file()
    assert (SITE / "README.md").is_file()
    for name in JSON_FILES:
        assert (DATA / name).is_file(), name
    for fig in SELECTED_FIGURES:
        assert (FIGURES / fig).is_file(), fig


def test_json_files_are_valid():
    for name in JSON_FILES:
        json.loads((DATA / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", JSON_FILES)
def test_json_utf8_no_bom(name):
    assert not (DATA / name).read_bytes().startswith(b"\xef\xbb\xbf"), name


def test_index_contains_all_sections():
    for sid in SECTION_IDS:
        assert f'id="{sid}"' in HTML, sid


# --- (14) frozen public naming ---------------------------------------------

def test_main_title_exact():
    assert re.search(r"<h1>\s*LLM机器主体归因评测\s*</h1>", HTML)


def test_subtitle_exact():
    assert '<p class="subtitle">PA—Wu R1仅机器主体研究</p>' in HTML


def test_html_title_correct():
    assert "<title>LLM机器主体归因评测｜PA—Wu R1研究</title>" in HTML


def test_positioning_is_current_machine_only_research():
    # the page now leads with the current PA-Wu R1 machine-only research
    assert "PA—Wu R1" in HTML
    assert "机器主体" in HTML
    # and no longer positions itself as a test-evaluation benchmark up front
    assert "测试型评测基准" not in HTML


# --- (14) no version numbers / old names -----------------------------------

def test_no_public_version_numbers():
    for bad in ["v0.3", "v1.0", "Version History", "版本路线图", "0.2.0.dev0"]:
        assert bad not in HTML, bad


def test_no_old_public_titles():
    for bad in ["大语言模型自由意志归因研究原型",
                "大语言模型 Agent 决策结构",
                "LLM Free-Will Attribution"]:
        assert bad not in HTML, bad


def test_no_old_repo_slug_anywhere():
    assert OLD_SLUG not in HTML


def test_github_links_use_new_slug():
    hrefs = re.findall(r'href="(https://github\.com/[^"]+)"', HTML)
    assert hrefs, "expected at least one GitHub link"
    for h in hrefs:
        assert NEW_SLUG in h, h
        assert OLD_SLUG not in h, h


# --- (14) no internal dev language / task codes ----------------------------

def test_no_internal_task_codes_in_html():
    for bad in ["Phase ", "Phase1", "Track S", "FND-", "SITE-", "RES-",
                "RUN-", "BMK-", "FAST-", "RBC-", "backlog"]:
        assert bad not in HTML, bad


def test_no_target_audience_wording():
    for bad in ["求职", "招聘者", "作品集", "面向 AI 数据评测岗位",
                "面向后训练岗位", "为了投递", "方便面试"]:
        assert bad not in HTML, bad


def test_no_forbidden_english_headings():
    for bad in ["Historical Baseline", "Mock Validation", "Provider Readiness",
                "Evidence Matrix", "Roadmap", "Pipeline", "Benchmark Status",
                "Engineering Core"]:
        assert bad not in HTML, bad


# --- (14) no hardcoded statistics ------------------------------------------

def test_no_hardcoded_statistics_in_html():
    for bad in ["360", "12.19", "0.2699", "4.308", "5.200", "34 个题项",
                "F = ", "p < ."]:
        assert bad not in HTML, bad


# --- (14) markup hygiene ---------------------------------------------------

def test_no_inline_event_handlers():
    assert re.search(r"\son[a-z]+\s*=", HTML) is None


def test_no_cdn_or_remote_assets_in_head_tags():
    # Scripts must be local; only meta rel=canonical/og may be absolute URLs.
    for m in re.finditer(r'<script[^>]*\ssrc="([^"]+)"', HTML):
        assert not m.group(1).startswith(("http://", "https://", "//")), m.group(1)
    for m in re.finditer(r'<link[^>]*\srel="stylesheet"[^>]*\shref="([^"]+)"', HTML):
        assert not m.group(1).startswith(("http://", "https://", "//")), m.group(1)


def test_js_has_no_third_party_imports():
    # No remote assets or ES-module URL imports. The SVG namespace URI is not a
    # network dependency and is allowed.
    assert "https://" not in JS_SRC
    assert 'fetch("http' not in JS_SRC
    assert "://cdn" not in JS_SRC.lower()
    assert re.search(r'\bfrom\s+["\']https?://', JS_SRC) is None
    assert re.search(r'\bimport\s+.*\bfrom\b', JS_SRC) is None


# --- (14) anchors, local resources -----------------------------------------

def test_all_local_hrefs_resolve():
    ids = set(re.findall(r'id="([^"]+)"', HTML))
    for href in re.findall(r'href="([^"]+)"', HTML):
        if href.startswith(("http://", "https://", "mailto:")):
            continue
        if href.startswith("#"):
            assert href[1:] in ids, "missing anchor target: " + href
            continue
        # deployed-at-assembly route (optionally with a #fragment into that page)
        route = href.split("#", 1)[0]
        if route in DEPLOYED_ROUTE_SOURCES:
            assert DEPLOYED_ROUTE_SOURCES[route].is_file(), href
            continue
        assert (SITE / href).exists(), "broken local href: " + href


def test_nav_anchors_are_valid_sections():
    nav = HTML.split('id="site-nav-list"', 1)[1].split("</nav>", 1)[0]
    for href in re.findall(r'href="#([^"]+)"', nav):
        assert f'id="{href}"' in HTML, href


def test_top_nav_excludes_legacy_engineering_entries():
    nav = HTML.split('id="site-nav-list"', 1)[1].split("</nav>", 1)[0]
    for bad in FORBIDDEN_TOP_NAV:
        assert bad not in nav, bad


def test_top_nav_leads_with_current_research():
    nav = HTML.split('id="site-nav-list"', 1)[1].split("</nav>", 1)[0]
    labels = re.findall(r'<a href="#[^"]+">([^<]+)</a>', nav)
    assert labels and labels[0] == "当前研究"
    assert "历史归档" in labels


def test_current_study_card_exists_and_is_current():
    card = (REPO_ROOT / "docs" / "CURRENT_STUDY_CARD.md").read_text(encoding="utf-8")
    assert card.startswith("# 当前研究：PA—Wu R1机器主体归因评测")
    assert "仅机器主体" in card
    # no unsupported validity claims
    for bad in ["专家确认", "专家验证", "内容效度成立"]:
        assert bad not in card, bad


def test_legacy_study_card_marked_as_archive():
    card = (REPO_ROOT / "docs" / "STUDY_CARD.md").read_text(encoding="utf-8")
    assert card.startswith("# 早期探索性研究归档说明")
    assert "不代表当前主研究设计" in card
    assert "CURRENT_STUDY_CARD.md" in card


def test_site_has_legacy_archive_boundary():
    assert 'id="legacy-archive"' in HTML
    assert "早期探索性研究归档" in HTML
    # legacy section headings carry an 早期/历史 qualifier
    assert "早期研究问题" in HTML


def test_legacy_research_files_still_present():
    # nothing historical is deleted
    for path in [
        "docs/STUDY_CARD.md",
        "docs/research_and_measurement_sources.md",
        "site/data/showcase_story.json",
        "site/data/historical_results.json",
    ]:
        assert (REPO_ROOT / path).is_file(), path


# --- (14) chart slots / JS wiring ------------------------------------------

def test_every_javascript_slot_exists_in_html():
    defined = set(re.findall(r'data-slot="([^"]+)"', HTML))
    used = set(re.findall(r'(?:slotEl|requireSlot|setSlot)\("([^"]+)"', JS_SRC))
    missing = used - defined
    assert not missing, "JS references missing slots: " + ", ".join(sorted(missing))


def test_core_chart_slots_present():
    for name in ["hero-corefacts", "process-cards", "design-matrix",
                 "scenario-cards", "research-source-cards", "research-references",
                 "condition-profile", "identity-effect",
                 "planned-contrasts", "controlled-regression", "mediation-path",
                 "figures", "mock-quality", "eval-steps", "artifact-table",
                 "readiness-flow", "benchmark-flow"]:
        assert f'data-slot="{name}"' in HTML, name


def test_render_pipeline_and_diagnostics_present():
    for call in ["renderConditionProfile(", "renderFigures(", "renderMediation(",
                 "renderReadiness(", "renderMockQuality(", "renderProcessConditions(",
                 "renderScenarios(", "renderResearchSources(", "renderEvalSteps(",
                 "renderBenchmarkRoadmap("]:
        assert call in JS_SRC, call
    assert 'renderComplete = "true"' in JS_SRC
    assert 'renderComplete = "false"' in JS_SRC
    assert "writeLayoutDiagnostics" in JS_SRC
    assert "diagnostics=1" in JS_SRC


# --- (14) provider readiness only in one section ---------------------------

def test_provider_readiness_single_section():
    assert HTML.count('id="real-provider"') == 1
    # the offline-validated statement is rendered from JSON, once, into one slot
    assert HTML.count('data-slot="readiness-statement"') == 1
    assert HTML.count('data-slot="readiness-flow"') == 1


def test_no_fabricated_real_metrics_in_html():
    for bad in ["0 ms", "$0", "0 token", "0.0 美元", "0ms"]:
        assert bad not in HTML, bad


# --- (11 / 14) real readiness metrics stay null in data --------------------

def test_real_provider_actual_metrics_are_null():
    eng = json.loads((DATA / "engineering_status.json").read_text(encoding="utf-8"))
    rr = eng["real_provider_readiness"]
    for key in ["actual_token_usage", "actual_cost_usd", "actual_latency_ms",
                "actual_completion_rate", "actual_parse_success_rate"]:
        assert rr[key] is None, key
    assert rr["smoke_status"] == "not_run"
    assert rr["pilot_status"] == "not_run"
    assert rr["network_calls_made"] == 0


# --- (20) provenance four-state consistency --------------------------------

def test_provenance_four_states_consistent():
    ev = json.loads((DATA / "evidence_matrix.json").read_text(encoding="utf-8"))
    pc = ev["provenance_completeness"]
    dims = pc["dimensions"]
    states = {d["verification_status"] for d in dims}
    assert states == {"repository_verified", "author_attested", "reconstructed", "unknown"}
    total = (pc["repository_verified_count"] + pc["author_attested_count"]
             + pc["reconstructed_count"] + pc["unknown_count"])
    assert total == pc["total_count"] == len(dims)
    # every dimension carries a Chinese display label + group for the matrix
    for d in dims:
        assert d.get("label")
        assert d.get("group")


# --- figures integrity ------------------------------------------------------

def test_figures_match_source_hashes():
    for fig in SELECTED_FIGURES:
        site_fig = FIGURES / fig
        source_fig = REPO_ROOT / "outputs" / "plots" / fig
        assert (hashlib.sha256(site_fig.read_bytes()).hexdigest()
                == hashlib.sha256(source_fig.read_bytes()).hexdigest()), fig


def test_historical_results_json_shape():
    hr = json.loads((DATA / "historical_results.json").read_text(encoding="utf-8"))
    assert hr["claims"]
    assert len(hr["figures"]) == 3
    for fig in hr["figures"]:
        assert len(fig["sha256"]) == 64
        assert fig.get("read_note")


# --- mediation structured fields (unchanged research contract) -------------

def test_mediation_metrics_structured():
    an = json.loads((DATA / "analysis_results.json").read_text(encoding="utf-8"))
    paths = an["mediation"]["paths"]
    agency = next(p for p in paths if p["name"] == "agency")
    intel = next(p for p in paths if p["name"] == "perceived_intelligence")
    assert agency["crosses_zero"] is False
    assert intel["crosses_zero"] is True


# --- responsive hygiene -----------------------------------------------------

def test_css_responsive_hygiene():
    assert "minmax(0, 1fr)" in CSS_SRC
    assert "min-width: 0" in CSS_SRC
    assert "overflow-wrap: anywhere" in CSS_SRC
    assert "overflow-x: hidden" not in CSS_SRC
    assert "@media (max-width: 390px)" in CSS_SRC


# --- concept visual (kept from prior redesign) -----------------------------

CONCEPT_IMG = FIGURES / "attribution-research-concept.png"
INVENTORY = REPO_ROOT / "docs" / "showcase" / "PUBLIC_ASSET_INVENTORY.md"
CONCEPT_SHA = "FFCC3139FD2FBE71CC9049F06CF718BBBFBB6C56E2BF37210C8268FF702BC7F7"


def test_research_concept_image_is_valid_and_referenced():
    data = CONCEPT_IMG.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", data[16:24])
    assert 'width="{}"'.format(width) in HTML
    assert 'height="{}"'.format(height) in HTML
    digest = hashlib.sha256(data).hexdigest().upper()
    assert digest == CONCEPT_SHA
    assert CONCEPT_SHA in INVENTORY.read_text(encoding="utf-8")


def test_research_concept_in_research_question_with_caption():
    rq = HTML.split('id="research-question"', 1)[1].split("</section>", 1)[0]
    assert "attribution-research-concept.png" in rq
    assert "不承载统计结果" in rq


# --- SHOWCASE-FIX-001: copy / layout cleanup -------------------------------

def _load_stimuli():
    spec = importlib.util.spec_from_file_location(
        "stimuli", REPO_ROOT / "src" / "stimuli.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_no_read_image_prefix():
    # (2) the "读图：" prefix must not appear in the page or its script
    assert "读图：" not in HTML
    assert "读图：" not in JS_SRC


def test_no_forbidden_word_list():
    # (2) no self-checking forbidden-word list, and no forbidden claims
    for bad in ["「证明了」", "揭示了真实心理机制", "模型具备自由意志",
                "与人类完全一致", "不使用「证明了」"]:
        assert bad not in HTML, bad


def test_no_evidence_boundary_section():
    # (3, 4) the evidence-boundary section and its nav entry are removed
    assert 'id="evidence-boundary"' not in HTML
    assert "证据与来源边界" not in HTML
    nav = HTML.split('id="site-nav-list"', 1)[1].split("</nav>", 1)[0]
    assert "证据边界" not in nav
    assert "renderProvenance" not in JS_SRC
    assert "provenance-matrix" not in HTML


def test_no_public_pilot_counts_or_status_table():
    # (5, 6) no public 12/60 plan, no not_run/null status table
    for bad in ["12 / 60", "12 条真实 smoke", "60 条真实 pilot",
                "12 条 smoke", "60 条 pilot", "not_run", "readiness-status",
                "readiness-checklist", "readiness-plan"]:
        assert bad not in HTML, bad


def test_no_old_footer_text():
    # (7) footer simplified to title + GitHub link only
    for bad in ["研究数据源提交", "历史 DeepSeek API 模型输出", "测试型评测基准原型",
                'data-slot="source-commit"', 'data-slot="data-as-of"',
                'data-slot="generated-at"']:
        assert bad not in HTML, bad


def test_no_diagnostic_or_grad_markup():
    # (9) no diagnostic class / grad-tag / length-control special marking.
    # (Note: the legitimate "diagnostics" layout feature is unrelated and kept.)
    for token in ["grad-tag", "grad-node", "LENGTH_CONTROL_KEY"]:
        assert token not in JS_SRC, token
    for token in ["grad-tag", "grad-node", ".diagnostic"]:
        assert token not in CSS_SRC, token


def test_process_condition_cards_uniform():
    # (8) six process conditions render as uniform cards
    assert 'data-slot="process-cards"' in HTML
    assert "renderProcessConditions(" in JS_SRC
    assert ".pc-card" in CSS_SRC


def test_matrix_corner_has_visible_text_color():
    # (12) the design matrix corner cell must set an explicit visible colour
    corner = re.search(r"\.design-matrix \.corner \{[^}]*\}", CSS_SRC)
    assert corner, "missing .design-matrix .corner rule"
    assert "color: var(--text)" in corner.group(0)


def test_general_benchmark_flow_present():
    # (13) the general-evaluation roadmap flow exists
    assert 'data-slot="benchmark-flow"' in HTML
    assert "renderBenchmarkRoadmap(" in JS_SRC
    assert "从单一任务到通用评测" in HTML


def test_scenarios_have_case_content_matching_stimuli():
    # (10, 11) eight scenario cards carry context/options/choice, faithful to stimuli
    story = json.loads((DATA / "showcase_story.json").read_text(encoding="utf-8"))
    cards = {c["id"]: c for c in story["scenarios"]}
    assert len(cards) == 8
    stim = _load_stimuli()
    for s in stim.SCENARIOS:
        c = cards[s.scenario_id]
        for field in ("context", "option_a", "option_b", "fixed_choice"):
            assert c.get(field), (s.scenario_id, field)
        assert c["context"] == s.context
        assert c["option_a"] == s.option_a
        assert c["option_b"] == s.option_b
        assert c["fixed_choice"] == s.fixed_choice
        assert c["domain"] == s.domain


# --- public research sources and README contract ---------------------------

README = REPO_ROOT / "README.md"
README_SRC = README.read_text(encoding="utf-8")
STORY = json.loads((DATA / "showcase_story.json").read_text(encoding="utf-8"))
RESEARCH_SOURCES = STORY["research_sources"]
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")

EXPECTED_SOURCE_IDS = [
    "mind_perception", "free_will_beliefs", "perceived_intelligence",
    "reasons_responsiveness_responsibility", "self_authored_checks",
]


def test_page_has_research_sources_section():
    # (4) the page carries a "研究与测量来源" section, placed after 实验设计
    assert 'id="research-sources"' in HTML
    assert "研究与测量来源" in HTML
    dm = HTML.index('id="design-measurement"')
    rs = HTML.index('id="research-sources"')
    hd = HTML.index('id="historical-data"')
    assert dm < rs < hd


def test_page_has_no_evidence_boundary_section_still():
    # (5) the removed evidence-boundary section must not come back
    assert 'id="evidence-boundary"' not in HTML
    assert "证据与来源边界" not in HTML


def test_readme_uses_current_machine_only_title_and_question():
    # README now opens with the current machine-only research, not free will
    # or an AI/human comparison as the core.
    assert README_SRC.startswith(f"# {README_TITLE}\n")
    assert "以PA—Wu R1为主研究" in README_SRC
    assert "人工智能决策系统" in README_SRC
    # the first research definition must not lead with free will / AI-human core
    first = README_SRC.split("## ", 1)[0]
    assert "自由意志" not in first
    assert "AI 与 human 身份比较" not in first


def test_readme_separates_current_and_legacy():
    assert "## 当前主研究" in README_SRC
    assert "## 早期探索性研究归档" in README_SRC
    # the legacy AI/human route is explicitly not part of R1 and not merged
    assert "不属于当前 R1 设计" in README_SRC
    assert "不与当前 R1 结果合并" in README_SRC


def test_readme_links_current_and_legacy_documents():
    for path in [
        "docs/CURRENT_STUDY_CARD.md",
        "docs/STUDY_CARD.md",
        "docs/research_and_measurement_sources.md",
        "docs/scale_source_mapping.md",
    ]:
        assert path in README_SRC, path


def test_readme_free_will_is_downgraded():
    # free will is only an exploratory MSI item, never title/sole construct/total
    assert "自由意志只对应 MSI 中的一个探索性题项" in README_SRC


def test_readme_avoids_outdated_or_unsupported_public_claims():
    for bad in [
        "A Reproducible Study and Evaluation Prototype",
        "可复现的测试型评测基准原型",
        "测试型评测基准",
        "真人专家审核",
        "专家内容效度验证",
        "专家评审通过",
        "多模型真实运行已经完成",
    ]:
        assert bad not in README_SRC, bad


def test_source_cards_count_and_order_stable():
    # (6) exactly the five sources, in canonical order
    ids = [s["id"] for s in RESEARCH_SOURCES["sources"]]
    assert ids == EXPECTED_SOURCE_IDS


def test_every_source_card_has_constructs_and_usage():
    # (7) each source carries constructs + a usage description + role
    for s in RESEARCH_SOURCES["sources"]:
        assert s["constructs"], s["id"]
        assert s["role"], s["id"]
        assert s["usage"], s["id"]


def test_all_dois_are_well_formed():
    # (8) every DOI present must be a well-formed DOI
    seen = 0
    for ref in RESEARCH_SOURCES["references"]:
        if ref["doi"]:
            assert DOI_RE.match(ref["doi"]), ref["doi"]
            seen += 1
    assert seen >= 4  # four journal references carry DOIs


def test_full_references_present():
    # (9) the full reference list is non-empty and every entry has full text
    assert RESEARCH_SOURCES["references"]
    for ref in RESEARCH_SOURCES["references"]:
        assert ref["full"].strip()


def _source(sid):
    return next(s for s in RESEARCH_SOURCES["sources"] if s["id"] == sid)


def test_gray_maps_to_agency_and_experience():
    # (10) mind perception source covers agency + experience
    s = _source("mind_perception")
    assert "Gray" in s["citation_short"]
    assert "能动性" in s["constructs"] and "体验性" in s["constructs"]


def test_free_will_source_maps_to_fwi_and_fadplus():
    # (11) free-will attribution source cites FWI and FAD-Plus
    s = _source("free_will_beliefs")
    assert "FWI" in s["citation_short"] and "FAD-Plus" in s["citation_short"]
    assert "自由意志" in s["constructs"]
    dois = {r["doi"] for r in s["references"]}
    assert "10.1016/j.concog.2014.01.006" in dois
    assert "10.1080/00223891.2010.528483" in dois


def test_godspeed_maps_to_perceived_intelligence():
    # (12) perceived intelligence source is Godspeed
    s = _source("perceived_intelligence")
    assert "Godspeed" in s["citation_short"]
    assert s["references"][0]["doi"] == "10.1007/s12369-008-0001-3"


def test_fischer_ravizza_is_theory_background():
    # (13) reasons-responsiveness / responsibility source is theory, not a scale
    s = _source("reasons_responsiveness_responsibility")
    assert "Fischer" in s["citation_short"]
    assert "责任" in "".join(s["constructs"])
    assert "不是直接采用的心理量表" in s["role"]


def test_self_authored_checks_have_no_external_scale():
    # (14) self-authored manipulation checks carry no external reference
    s = _source("self_authored_checks")
    assert s["references"] == []
    assert "自编" in s["citation_short"] or "自编" in s["role"]


def test_autonomy_not_claimed_as_a_complete_scale():
    # (15) autonomy is never claimed to come directly from a complete scale
    doc = (REPO_ROOT / "docs" / "research_and_measurement_sources.md").read_text(encoding="utf-8")
    assert "自主性与行动控制相关理论背景" in doc
    for bad in ["Self-Determination Theory 量表", "直接采用自主性量表",
                "autonomy 量表原题"]:
        assert bad not in doc, bad


def test_page_does_not_claim_complete_scale_use_or_inherited_validity():
    # (16, 17) page never claims direct use of a complete scale or inherited validity
    blob = HTML + json.dumps(RESEARCH_SOURCES, ensure_ascii=False)
    # positive over-claims must never appear; the legitimate negation
    # "并非对原量表的完整直接使用" is expected and must NOT be flagged.
    for bad in ["直接使用完整量表", "直接使用成熟量表", "沿用原量表信效度",
                "继承原量表信效度"]:
        assert bad not in blob, bad


def test_item_ids_and_texts_unchanged():
    # (18) src/scales.py item ids and texts are untouched by this task
    stim_scales = _load_scales()
    ids = [it.item_id for it in stim_scales.ITEMS]
    assert len(ids) == 34
    assert len(set(ids)) == 34
    # a couple of anchor texts must remain verbatim
    texts = {it.item_id: it.text for it in stim_scales.ITEMS}
    assert texts["agency_self_control"] == "该决策者能够控制自己的行动，而不是只被情境推着走。"
    assert texts["subjective_not_sparse"] == "我认为材料中的决策过程不是只有一个稀疏结论。"


def _load_scales():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "scales", REPO_ROOT / "src" / "scales.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_no_public_future_pilot_numbers_on_page_or_readme():
    # (21) no concrete future smoke/pilot counts leak into page or README
    for bad in ["12 条真实 smoke", "60 条真实 pilot", "12 / 60",
                "每格 2 条", "每格 1 条"]:
        assert bad not in HTML, bad
        assert bad not in README_SRC, bad


# --- final polish: repository paths are clickable ---------------------------

def test_repository_document_paths_are_clickable():
    assert "function repoPathURL(path, kind)" in JS_SRC
    assert 'a.href = repoPathURL(d.path, "blob")' in JS_SRC
    assert 'a.href = repoPathURL(d.path, "tree")' in JS_SRC
    assert JS_SRC.count('a.target = "_blank"') >= 3
    assert JS_SRC.count('a.rel = "noopener"') >= 3


def test_repository_url_targets_current_slug_and_main():
    assert '"llm-attribution-behavior-evaluation"' in JS_SRC
    assert '"main"' in JS_SRC
    assert OLD_SLUG not in JS_SRC


# --- PR A follow-up: dynamic data + current-research positioning -----------

PILOT_SHOWCASE = json.loads(
    (REPO_ROOT / "tasks" / "attribution_behavior" / "evaluations"
     / "pa_wu_r1_pilot" / "outputs" / "showcase_data.json").read_text(encoding="utf-8"))


def test_hero_uses_current_study_object():
    # renderHero must read the current PA-Wu R1 study object, not the legacy
    # story.core_facts, and fail loudly if it is missing.
    hero = JS_SRC.split("function renderHero(", 1)[1].split("\n}", 1)[0]
    assert "story.current_study" in hero
    assert "core_facts" in hero
    # it must NOT fall back to the legacy top-level core_facts for the hero
    assert "story.core_facts" not in hero


def test_showcase_story_has_current_study_core_facts():
    cs = STORY.get("current_study")
    assert cs, "showcase_story.json missing current_study"
    facts = {f["label"]: f["value"] for f in cs["core_facts"]}
    assert facts["实验条件"] == 6
    assert facts["场景"] == 8
    assert facts["决策方向"] == 2
    assert facts["材料总数"] == 96
    assert facts["评判模型配置"] == 2
    assert facts["每次完整运行响应"] == 192
    assert facts["数据状态"] == "合成流程演示"
    assert facts["目标主体"] == "仅机器主体"


def test_current_study_facts_exclude_legacy_metrics():
    cs = STORY["current_study"]
    labels = {f["label"] for f in cs["core_facts"]}
    values = {str(f["value"]) for f in cs["core_facts"]}
    for bad_label in ["行动者身份", "历史记录", "测量题项", "测量构念",
                      "可复现 mock 运行", "真实接口离线准备"]:
        assert bad_label not in labels, bad_label
    for bad_value in ["360", "34", "10", "2"]:
        # 2 is legitimately used (directions / judge models); only guard the
        # legacy-only counts 360/34/10 as values.
        if bad_value in {"360", "34", "10"}:
            assert bad_value not in values, bad_value


def test_current_study_facts_match_pilot_showcase():
    cs = STORY["current_study"]
    facts = {f["label"]: f["value"] for f in cs["core_facts"]}
    q = PILOT_SHOWCASE["quality_summary"]
    assert facts["材料总数"] == q["n_materials"] == 96
    assert facts["每次完整运行响应"] == q["n_responses"] == 192


def test_current_study_points_to_current_sources_doc():
    cs = STORY["current_study"]
    assert cs["sources_doc"] == "docs/CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md"


def test_current_constructs_section_links_current_sources_doc():
    sec = HTML.split('id="current-constructs-sources"', 1)[1].split("</section>", 1)[0]
    assert "CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md" in sec
    # the current constructs section must NOT present the legacy sources doc as R1's
    assert "research_and_measurement_sources.md" not in sec.replace(
        "CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md", "")
    assert "未声称内容效度" in sec


def test_current_sources_doc_exists_and_lists_real_assets():
    doc = (REPO_ROOT / "docs" / "CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md").read_text(encoding="utf-8")
    assert doc.startswith("# 当前研究与测量来源：PA—Wu R1")
    for path in [
        "pa_wu_r1_pilot/study_protocol.yaml",
        "pa_wu_r1_pilot/scoring_spec.yaml",
        "pa_wu_p0/",
    ]:
        assert path in doc, path
    for real in ["Wu & Shen 2026", "PA 2024"]:
        assert real in doc, real


def test_legacy_sources_docs_carry_archive_banner():
    src = (REPO_ROOT / "docs" / "research_and_measurement_sources.md").read_text(encoding="utf-8")
    assert src.startswith("# 早期探索性研究的研究与测量来源")
    assert "CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md" in src
    mapping = (REPO_ROOT / "docs" / "scale_source_mapping.md").read_text(encoding="utf-8")
    assert mapping.startswith("# 早期题项与理论来源映射")
    assert "CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md" in mapping


def test_showcase_story_legacy_wording_is_archive():
    blob = json.dumps(STORY, ensure_ascii=False)
    for bad in ["当前项目", "当前题项池", "本项目当前"]:
        assert bad not in blob, bad
    assert ("早期" in blob) or ("历史路线" in blob)


def test_current_methods_links_r1_assets_and_not_archive():
    sec = HTML.split('id="current-methods"', 1)[1].split("</section>", 1)[0]
    for asset in ["CURRENT_STUDY_CARD.md", "CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md",
                  "study_protocol.yaml", "analysis_plan.md", "scoring_spec.yaml",
                  "render_report.py", "pa-wu-r1-pilot/"]:
        assert asset in sec, asset
    for bad in ["复现入口见下方早期探索性研究归档",
                "当前研究方法记录在历史归档对应区域"]:
        assert bad not in sec, bad


def test_legacy_history_data_files_still_present():
    for path in [
        "site/data/historical_results.json",
        "site/data/showcase_story.json",
        "docs/STUDY_CARD.md",
        "docs/research_and_measurement_sources.md",
        "docs/scale_source_mapping.md",
    ]:
        assert (REPO_ROOT / path).is_file(), path
