
"""Portfolio packaging and reader-attraction checks."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / "site" / "index.html"
README = ROOT / "README.md"
A_HTML = ROOT / "docs" / "identity-process-attribution-baseline" / "index.html"
B_HTML = ROOT / "docs" / "pa-wu-r1-pilot" / "index.html"
FIGURES = ROOT / "site" / "assets" / "figures"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_overview_leads_with_project_value_and_visible_outputs():
    page = text(HOME)
    for phrase in ["项目工作覆盖构念定义、材料与题项、模型评分、数据契约、结构审计、跨平台CI和公开展示", "项目完成了什么", "从研究结果到真实系统", "360", "96", "1005"]:
        assert phrase in page
    assert 'href="#build"' in page


def test_portfolio_visual_assets_exist_and_are_published():
    for name in ["social-preview.svg", "project-architecture.svg", "value-map.svg"]:
        path = FIGURES / name
        assert path.is_file(), path
        assert "<svg" in text(path)
    page = text(HOME)
    assert 'property="og:image"' in page
    assert "assets/figures/project-architecture.svg" in page
    assert "assets/figures/value-map.svg" in page


def test_readme_is_a_case_study_not_only_a_research_index():
    content = text(README)
    for phrase in ["项目一览", "项目工作覆盖", "从研究问题到公开交付", "从研究发现到实际问题", "关键工程决策", "项目案例摘要"]:
        assert phrase in content
    assert "site/assets/figures/social-preview.svg" in content
    assert "site/assets/figures/project-architecture.svg" in content
    assert "site/assets/figures/value-map.svg" in content


def test_research_pages_keep_clear_roles():
    assert "<strong>结果页：</strong>" in text(A_HTML)
    assert "<strong>设计页：</strong>" in text(B_HTML)


def test_defensive_or_meta_narrative_does_not_return():
    combined = "\n".join([text(HOME), text(README)])
    for phrase in ["证据支持什么", "不支持什么", "当前结果来自研究A", "项目关注的核心不是", "这个项目的重要性不在于", "本页不把研究B"]:
        assert phrase not in combined


def test_portfolio_case_study_is_available():
    case = ROOT / "docs" / "PORTFOLIO_CASE_STUDY.md"
    content = text(case)
    for phrase in ["30秒概览", "负责内容", "关键产出", "实际价值", "关键工程判断"]:
        assert phrase in content
