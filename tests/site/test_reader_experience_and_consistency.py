"""Reader-facing structure and research-consistency checks."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / "site" / "index.html"
A_HTML = ROOT / "docs" / "identity-process-attribution-baseline" / "index.html"
A_JS = ROOT / "docs" / "identity-process-attribution-baseline" / "app.js"
B_HTML = ROOT / "docs" / "pa-wu-r1-pilot" / "index.html"
README = ROOT / "README.md"
PROGRAM = ROOT / "docs" / "RESEARCH_PROGRAM.md"
RESULTS = ROOT / "docs" / "RESULTS_AND_PRACTICAL_IMPLICATIONS.md"
STUDY_A = ROOT / "docs" / "STUDY_CARD.md"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_public_html_ids_are_unique():
    for path in [HOME, A_HTML, B_HTML]:
        ids = re.findall(r'id="([^"]+)"', text(path))
        duplicates = sorted(key for key, count in Counter(ids).items() if count > 1)
        assert not duplicates, (path, duplicates)


def test_study_b_has_one_material_browser_and_clear_navigation():
    page = text(B_HTML)
    for element_id in ["scenSelect", "scenCondSelect", "scenDirSelect", "scenStim", "duDetails", "conditionCards"]:
        assert page.count(f'id="{element_id}"') == 1, element_id
    assert "返回项目总览" in page
    assert 'class="skip-link"' in page
    assert "分析流程示例" in page
    assert "查看示例分析输出" in page
    assert "计划使用的统计模型" in page
    assert "对Benchmark材料生产的意义" not in page


def test_study_a_explains_scale_and_sampling_units():
    page = text(A_HTML)
    for phrase in [
        "12个实验组合",
        "每个组合包含30次",
        "96个场景×身份×条件分析单元",
        "每个单元约3—4条响应",
        "1—7分量尺",
    ]:
        assert phrase in page
    for condition in ["直接选择", "长文本直接选择", "列出可选方案", "简洁理由权衡", "完整理由权衡", "反思与反馈修正"]:
        assert condition in page


def test_study_a_identity_finding_is_consistent():
    for path in [HOME, A_HTML, A_JS, README, RESULTS, STUDY_A]:
        content = text(path)
        assert "自由意志归因" in content, path
    assert "身份标签对应部分心智和责任评价差异" not in text(A_HTML)


def test_historical_report_is_not_the_current_result_entry():
    page = text(A_HTML)
    assert "研究A说明与当前解释" in page
    assert "历史探索性报告" in page
    assert "结果报告</a>" not in page
    assert "早期探索性分析" in text(STUDY_A)
    assert "以当前稳健性报告和本说明为准" in text(STUDY_A)


def test_practical_value_is_specific_and_frontier_linked():
    combined = "\n".join(text(path) for path in [HOME, README, PROGRAM, RESULTS])
    for phrase in [
        "过程监督",
        "推理忠实性",
        "Agent轨迹",
        "副作用",
        "信任校准",
        "责任",
        "NIST AI RMF",
    ]:
        assert phrase in combined
    for token in ["AgentRewardBench", "TRAJECT-Bench", "AgentLens"]:
        assert token in text(RESULTS)


def test_success_status_messages_are_hidden_by_javascript():
    assert 'node.hidden = kind === "success"' in text(ROOT / "site" / "assets" / "js" / "site.js")
    assert "STATUS.hidden = true" in text(A_JS)
    assert 'status.hidden = kind === "success"' in text(ROOT / "docs" / "pa-wu-r1-pilot" / "app.js")


def test_readme_defines_attribution_scale_and_counting_units():
    content = text(README)
    for phrase in [
        "行动者归因",
        "1—7分量尺",
        "360表示模型评分输出次数",
        "16和48表示材料组合的配对数量",
    ]:
        assert phrase in content
