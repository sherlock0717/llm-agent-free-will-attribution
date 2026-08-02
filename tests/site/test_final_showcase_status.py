"""Final-showcase status and evidence-boundary contract tests.

These tests lock the wording that the public release converged on:

  - project / Study A / Study B status statements are unified and no longer
    describe finished work as an upcoming "next step";
  - the Study A process finding is described as a bundled high-structure
    writing style, never as an isolated feedback effect;
  - the length result keeps a single first-layer boundary sentence and the
    length-adjusted coefficients stay in the robustness report;
  - Study B material wording separates the deterministic structural audit
    from semantic review;
  - CI and the Pages workflow keep the generated-artefact gates.

They are read-only: no script is executed and no research asset is touched.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

README = ROOT / "README.md"
RESEARCH_PROGRAM = ROOT / "docs" / "RESEARCH_PROGRAM.md"
ROADMAP_DOC = ROOT / "docs" / "RESULTS_FIRST_ROADMAP.md"
STUDY_CARD = ROOT / "docs" / "STUDY_CARD.md"
STUDY_B_CARD = ROOT / "docs" / "STUDY_B_CARD.md"
PRESENTATION_GUIDE = ROOT / "docs" / "PUBLIC_PRESENTATION_GUIDE.md"
ROOT_HTML = ROOT / "site" / "index.html"
ROOT_JS = ROOT / "site" / "assets" / "js" / "site.js"
STUDY_A_HTML = ROOT / "docs" / "identity-process-attribution-baseline" / "index.html"
STUDY_A_JS = ROOT / "docs" / "identity-process-attribution-baseline" / "app.js"
STUDY_B_HTML = ROOT / "docs" / "pa-wu-r1-pilot" / "index.html"
STUDY_B_JS = ROOT / "docs" / "pa-wu-r1-pilot" / "app.js"
CI = ROOT / ".github" / "workflows" / "ci.yml"
PAGES = ROOT / ".github" / "workflows" / "pages.yml"
SITE_SUMMARY = ROOT / "site" / "data" / "site_summary.json"

STATUS_DOCS = [README, RESEARCH_PROGRAM, ROADMAP_DOC, STUDY_CARD, STUDY_B_CARD,
               PRESENTATION_GUIDE]
PUBLIC_SURFACES = [ROOT_HTML, ROOT_JS, STUDY_A_HTML, STUDY_A_JS,
                   STUDY_B_HTML, STUDY_B_JS]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# --- 1. status unification -------------------------------------------------

def test_status_docs_drop_completed_work_as_next_step():
    stale = [
        "下一步进行研究A稳健性分析",
        "下一步开展研究A稳健性分析",
        "下一步进行研究B结构审计",
        "下一步开展研究B结构审计",
        "当前执行任务是材料操纵完整性审计",
        "当前将开展跨模型API运行",
        "当前将进行跨模型API运行",
        "当前将开展正式双模型评分",
        "当前将进行正式双模型评分",
        "正式模型结果即将更新",
        "release_verification_status = pending_verification",
        "benchmark_status = planned",
    ]
    for path in STATUS_DOCS:
        text = _read(path)
        for phrase in stale:
            assert phrase not in text, (path.name, phrase)


def test_status_docs_state_the_final_release_state():
    program = _read(RESEARCH_PROGRAM)
    assert "公开展示与离线复现版本完成" in program
    assert "已有360条模型响应、场景分析和稳健性分析" in program
    assert "确定性结构审计完成" in program

    readme = _read(README)
    assert "公开展示与离线复现版本完成" in readme
    assert "确定性结构审计完成" in readme


def test_site_summary_status_fields_are_final():
    payload = json.loads(_read(SITE_SUMMARY))
    assert payload["release_verification_status"] == "completed"
    assert "benchmark_status" not in payload


def test_site_summary_keeps_missing_provenance_fields_untouched():
    """Historical gaps must stay explicit; they are never back-filled."""
    payload = json.loads(_read(SITE_SUMMARY))
    assert payload["provenance_status"] == "incomplete_run_metadata"
    assert payload["model_version_snapshot"] is None
    assert payload["token_usage_total"] is None
    assert payload["estimated_cost_usd"] is None


def test_no_pending_verification_left_in_public_status_surfaces():
    for path in [SITE_SUMMARY, ROOT / "site" / "data" / "roadmap.json",
                 *STATUS_DOCS, *PUBLIC_SURFACES]:
        assert "pending_verification" not in _read(path), path.name


# --- 2. Study A process finding --------------------------------------------

def test_process_finding_is_described_as_bundled_writing_style():
    for path in [README, ROOT_HTML, ROOT_JS, STUDY_A_HTML, STUDY_CARD]:
        text = _read(path)
        assert "高结构过程写法" in text, path.name


def test_process_finding_explains_both_sides_of_the_comparison():
    for path in [README, ROOT_JS, STUDY_A_HTML, STUDY_CARD]:
        text = _read(path)
        assert "理由、反思、反馈与后续行动" in text, path.name
        assert "较长背景和最终选择" in text, path.name


def test_process_finding_is_not_written_as_an_isolated_feedback_effect():
    banned = [
        "反馈本身使评分提高",
        "反馈的独立因果效应",
        "反馈的独立效应",
        "单独加入反思的效应",
        "单独加入反馈的效应",
    ]
    for path in [README, *PUBLIC_SURFACES, STUDY_CARD, RESEARCH_PROGRAM]:
        text = _read(path)
        for phrase in banned:
            assert phrase not in text, (path.name, phrase)


# --- 3. length sensitivity --------------------------------------------------

LENGTH_BOUNDARY = "文本长度与过程条件共同变化，现有数据不能可靠分离两者的独立作用。"


def test_length_boundary_sentence_is_the_first_layer_statement():
    for path in [README, RESEARCH_PROGRAM, STUDY_A_HTML, STUDY_A_JS]:
        assert LENGTH_BOUNDARY in _read(path), path.name


def test_first_layer_does_not_surface_length_adjusted_coefficients():
    for path in [README, ROOT_HTML, ROOT_JS, STUDY_A_HTML, STUDY_A_JS]:
        text = _read(path)
        assert "3.267" not in text, path.name
        assert "A4估计由" not in text, path.name


def test_length_adjusted_detail_stays_in_the_robustness_report():
    report = ROOT / "docs" / "research_a_robustness_report.md"
    assert report.is_file()
    assert "长度敏感性" in _read(report)


def test_length_wording_avoids_net_effect_claims():
    banned = ["控制长度后效果更强", "排除文本长度影响", "长度不是混杂因素",
              "调整后结果更加稳健", "过程信息的净效应", "已经排除文本长度影响"]
    for path in [README, RESEARCH_PROGRAM, STUDY_CARD, *PUBLIC_SURFACES]:
        text = _read(path)
        for phrase in banned:
            assert phrase not in text, (path.name, phrase)


# --- 4. Study B material wording -------------------------------------------

def test_study_b_page_uses_information_increment_wording():
    html = _read(STUDY_B_HTML)
    assert "每项预设比较对应明确的信息增量" in html
    assert "每个条件只改变一个目标信息单元" not in html


def test_study_b_page_scopes_direction_symmetry_to_thresholds():
    html = _read(STUDY_B_HTML)
    assert "方向版本未触发预设长度和句子数量阈值" in html
    assert "措辞强度和语义对称性未纳入当前审计" in html
    assert "方向版本保持长度和措辞强度可比" not in html


def test_study_b_material_text_is_protocol_defined_not_model_received():
    for path in [STUDY_B_HTML, STUDY_B_JS]:
        text = _read(path)
        assert "协议中定义的英文材料原文" in text, path.name
        assert "评判模型实际接收的英文原文" not in text, path.name
        assert "实际接收的英文原文" not in text, path.name


def test_study_b_never_claims_verified_materials():
    banned = ["96条材料全部验证通过", "材料质量已经验证", "内容效度通过",
              "0条需要人工复核", "措辞强度已经证明可比"]
    for path in [README, STUDY_B_CARD, STUDY_B_HTML, STUDY_B_JS, ROOT_HTML]:
        text = _read(path)
        for phrase in banned:
            assert phrase not in text, (path.name, phrase)


def test_study_b_card_separates_structural_check_from_semantic_review():
    card = _read(STUDY_B_CARD)
    assert "96条材料全部通过确定性结构检查" in card
    assert "语义对称性、理由强度和反馈强度未纳入当前版本" in card
    assert "not_assessed" in card


# --- 5. CI / Pages generated-artefact gates --------------------------------

ROBUSTNESS_GATE = "python scripts/check_research_a_robustness_outputs.py"
AUDIT_GATE = "python scripts/audit_study_b_materials.py --check"


def test_ci_runs_both_generated_artefact_checks():
    ci = _read(CI)
    assert ROBUSTNESS_GATE in ci
    assert AUDIT_GATE in ci


def test_pages_runs_both_generated_artefact_checks():
    pages = _read(PAGES)
    assert ROBUSTNESS_GATE in pages
    assert AUDIT_GATE in pages


def test_pages_verifies_no_tracked_drift_after_assembly():
    pages = _read(PAGES)
    assert "git diff --exit-code" in pages
    assembly = pages.index("scripts/assemble_pages.py")
    drift = pages.index("git diff --exit-code")
    assert drift > assembly, "drift check must run after assembly"


def test_existing_ci_gates_are_preserved():
    ci = _read(CI)
    for step in [
        "ubuntu-latest",
        "windows-latest",
        "ruff check src scripts tests",
        "python -m compileall -q src scripts tests",
        "scripts/build_study_b_protocol_package.py --check",
        "scripts/check_public_json.py",
        "pytest -q",
        "freewill_attribution.cli run",
        "repository and historical outputs unchanged",
    ]:
        assert step in ci, step