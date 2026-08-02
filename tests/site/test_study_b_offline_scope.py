"""Public-contract tests for the Study B offline research scope."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUDY_B = ROOT / "docs" / "pa-wu-r1-pilot"
HTML = (STUDY_B / "index.html").read_text(encoding="utf-8")
JS = (STUDY_B / "app.js").read_text(encoding="utf-8")
ROOT_HTML = (ROOT / "site" / "index.html").read_text(encoding="utf-8")

FORBIDDEN_PROMISES = [
    "双模型正式评分：下一步",
    "即将调用两个模型",
    "运行两个评判模型",
    "请求量",
    "API运行",
    "费用",
    "等待模型结果",
    "正式评分完成后自动更新",
    "下一阶段运行两个评判模型",
    "下一步执行两个评判模型的正式评分",
]


def test_study_b_page_makes_no_formal_api_run_promise():
    for phrase in FORBIDDEN_PROMISES:
        assert phrase not in HTML, phrase
        assert phrase not in JS, phrase


def test_study_b_page_states_offline_scope():
    # the offline scope is stated once, in the analysis interface note.
    assert "界面中的数值用于校验分析流程、统计表和图表结构。" in HTML
    assert "外部提供的离线评价记录通过验证后" in HTML


def test_study_b_demo_pipeline_uses_offline_records():
    demo = HTML.split('id="demo"', 1)[1].split("</section>", 1)[0]
    assert "分析流程示例" in demo
    assert "检查场景与评价来源差异" in demo


def test_study_b_example_marked_as_analysis_interface():
    demo = HTML.split('id="demo"', 1)[1].split("</section>", 1)[0]
    assert "条件变化与预设比较" in demo
    assert "界面中的数值用于校验分析流程" in demo


def test_study_b_no_internal_slot_wording():
    for token in ["槽位", "评判槽位", "双评判槽位", "judge_slot", "评分槽"]:
        assert token not in HTML, token
        assert token not in JS, token


def test_root_page_states_offline_scope_for_study_b():
    assert "下一步执行两个评判模型的正式评分" not in ROOT_HTML
    assert "双模型正式评分" not in ROOT_HTML
    assert "离线分析方案" in ROOT_HTML


def test_study_b_status_notes_reference_offline_import():
    assert "外部离线" in JS and "分析" in JS


def test_no_development_labels_remain():
    for label in ["流程演示", "V2", "legacy", "CURRENT_"]:
        assert label not in HTML, label
