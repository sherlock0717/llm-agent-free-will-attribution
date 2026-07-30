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
    assert "研究B当前范围覆盖材料、测量、分析计划、确定性示例与离线结果导入。" in HTML
    assert "外部提供的离线评分文件通过验证后，可以进入同一分析流程。" in HTML
    assert "仓库的可执行范围止于本地验证、结果导入和离线分析。" in HTML


def test_study_b_progress_chain_is_all_done():
    progress = HTML.split('id="progress"', 1)[1].split("</section>", 1)[0]
    assert 'class="next"' not in progress
    for step in ["确定性分析界面示例", "离线结果导入契约", "可复现离线分析流程"]:
        assert step in progress, step


def test_study_b_example_marked_as_analysis_interface_example():
    demo = HTML.split('id="demo"', 1)[1].split("</section>", 1)[0]
    assert "分析界面示例" in demo
    assert "以下数值用于展示结果页面的阅读方式" in demo


def test_study_b_model_ids_are_protocol_metadata():
    assert "仅作协议元数据" in HTML


def test_root_page_states_offline_scope_for_study_b():
    assert "下一步执行两个评判模型的正式评分" not in ROOT_HTML
    assert "双模型正式评分" not in ROOT_HTML
    assert "离线结果导入" in ROOT_HTML


def test_study_b_status_notes_reference_offline_import():
    assert "外部离线评分文件通过验证后，可以进入同一分析流程。" in JS


def test_no_development_labels_remain():
    for label in ["流程演示", "V2", "legacy", "CURRENT_"]:
        assert label not in HTML, label
