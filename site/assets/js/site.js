"use strict";

function setStatus(message, kind) {
  const node = document.getElementById("loadStatus");
  if (!node) return;
  node.textContent = message;
  node.dataset.kind = kind;
}

function renderStory(story) {
  const program = story.research_program;
  const studyA = program?.studies?.study_a;
  const studyB = program?.studies?.study_b;
  if (!program || !studyA || !studyB) throw new Error("研究计划数据缺少研究A或研究B");
  // The overview text, study relationship and section order stay static in the
  // page. The data file only confirms that both studies resolve.
}

async function loadOverview() {
  setStatus("正在载入项目数据……", "loading");
  try {
    const response = await fetch("data/showcase_story.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    renderStory(await response.json());
    setStatus("项目数据已载入。", "success");
  } catch (error) {
    setStatus("项目总览使用页面内置说明；研究A与研究B入口保持可用。", "fallback");
    const node = document.getElementById("loadStatus");
    if (node) {
      const details = document.createElement("details");
      const summary = document.createElement("summary");
      const code = document.createElement("code");
      summary.textContent = "查看技术信息";
      code.textContent = error?.message || String(error);
      details.append(summary, code);
      node.appendChild(details);
    }
  }
}

function setupNavigation() {
  const button = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".site-nav");
  if (!button || !nav) return;
  button.addEventListener("click", () => {
    const open = button.getAttribute("aria-expanded") === "true";
    button.setAttribute("aria-expanded", String(!open));
    nav.classList.toggle("open", !open);
  });
  nav.addEventListener("click", (event) => {
    if (event.target instanceof HTMLAnchorElement) {
      button.setAttribute("aria-expanded", "false");
      nav.classList.remove("open");
    }
  });
}

// The three findings each show at most one key number, filled from the
// existing-data robustness summary. This loads separately and fails silently,
// so the single primary data dependency (showcase_story.json) is unchanged and
// the static finding text always remains readable.
async function loadFindingMetrics() {
  let summary;
  try {
    const response = await fetch("data/research_a_robustness_summary.json", { cache: "no-store" });
    if (!response.ok) return;
    summary = await response.json();
  } catch (error) {
    return;
  }
  const findings = summary.public_findings || {};
  const proc = findings.process_information;
  const ident = findings.identity_label;
  const scen = findings.scenario_dependence;

  if (proc) {
    setFindingBody(
      "process",
      `包含理由、反思、反馈与后续行动的高结构过程写法，与只包含较长背景和最终选择的写法相比，能动性评分平均高出${fmt(proc.full_effect)}分。`
      + `${proc.direction_majority_count}/${proc.total_unit_count}个场景×身份配对单元呈现相同方向。`
      + "该比较对应两种成套写法的整体差异，不是反馈这一单项线索的独立效应。");
    setFindingMetric(
      "process",
      `${proc.direction_majority_count}/${proc.total_unit_count}个场景×身份配对单元方向一致`);
  }
  if (ident) {
    setFindingBody(
      "identity",
      `在任务场景和过程写法保持相同时，人类标签下的自由意志归因平均比AI标签高${fmt(ident.overall_identity_difference)}分。`
      + `${ident.direction_majority_count}/${ident.total_unit_count}个场景×过程条件身份配对单元呈现相同方向。`
      + "该差异只描述自由意志归因这一维度，不概括所有心智和责任维度。");
    setFindingMetric(
      "identity",
      `${ident.direction_majority_count}/${ident.total_unit_count}个场景×过程条件身份配对方向一致`);
  }
  if (scen && Array.isArray(scen.process_effect_range)) {
    const [lo, hi] = scen.process_effect_range;
    if (lo != null && hi != null) {
      setFindingMetric(
        "scenario",
        `过程效应在八个场景中的平均差异范围为${fmt(lo)}至${fmt(hi)}`);
    }
  }
}

function setFindingBody(id, text) {
  const node = document.querySelector(`[data-finding-body="${id}"]`);
  if (node) node.textContent = text;
}

function fmt(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return "—";
  return n.toFixed(2);
}

function setFindingMetric(id, text) {
  const node = document.querySelector(`[data-finding-metric="${id}"]`);
  if (!node) return;
  node.textContent = text;
  node.hidden = false;
}

setupNavigation();
loadOverview();
loadFindingMetrics();
