from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected text missing in {path}: {old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


static_test = ROOT / "tests" / "site" / "test_static_site.py"
replace_once(
    static_test,
    'ROOT_SECTIONS = ["overview", "findings", "studies", "implications", "methods"]',
    'ROOT_SECTIONS = ["overview", "findings", "studies", "build", "implications", "methods"]',
)
replace_once(
    static_test,
    "def test_root_page_has_exactly_five_ordered_sections(html: str):",
    "def test_root_page_has_ordered_portfolio_sections(html: str):",
)
replace_once(
    static_test,
    '    assert "360条响应、主要结果与场景分析" in hero',
    '    assert "360次模型评分、主要结果与场景分析" in hero',
)
replace_once(
    static_test,
    "    assert html.index('id=\"studies\"') < html.index('id=\"implications\"')\n    assert html.index('id=\"implications\"') < html.index('id=\"methods\"')",
    "    assert html.index('id=\"studies\"') < html.index('id=\"build\"')\n    assert html.index('id=\"build\"') < html.index('id=\"implications\"')\n    assert html.index('id=\"implications\"') < html.index('id=\"methods\"')",
)

home = ROOT / "site" / "index.html"
html = home.read_text(encoding="utf-8")
if "信任校准" not in html:
    start = html.index('<section id="implications"')
    end = html.index("</section>", start)
    marker = '<div class="actions">'
    marker_at = html.rfind(marker, start, end)
    if marker_at < 0:
        raise RuntimeError("implications actions marker missing")
    note = (
        '        <p class="reading practical-note">产品评估还可以观察用户在系统正确时是否采纳、'
        '错误时是否覆盖，以及信任能否随准确率、不确定性和执行权限变化；这构成信任校准问题。</p>\n'
    )
    html = html[:marker_at] + note + html[marker_at:]
    home.write_text(html, encoding="utf-8")

Path(__file__).unlink()
