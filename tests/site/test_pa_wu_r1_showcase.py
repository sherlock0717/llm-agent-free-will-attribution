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


def test_synthetic_demo_declaration_chinese():
    assert "合成演示数据" in HTML


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

def test_no_real_result_claim():
    assert "不代表真实模型结果" in HTML


def test_no_model_ranking_claim():
    assert "不进行模型排名" in HTML or "不用于能力判断或模型排名" in HTML


def test_no_ai_human_comparison_result():
    assert "不进行AI与人类主体比较" in HTML


def test_english_source_material_preserved_in_js():
    # the referent bridge (actual English administration text) must remain
    assert '"the machine" refers to the AI system described above.' in JS


def test_no_external_cdn_assets():
    for src in re.findall(r'src="([^"]+)"', HTML):
        assert not src.startswith(("http://", "https://", "//")), src
    for href in re.findall(r'<link[^>]*href="([^"]+)"', HTML):
        assert not href.startswith(("http://", "https://", "//")), href
    assert "@import" not in CSS
    assert "http" not in CSS
