"use strict";

function text(id, value) {
  const node = document.getElementById(id);
  if (node && value != null) node.textContent = String(value);
}

function renderFacts(id, facts) {
  const host = document.getElementById(id);
  if (!host || !Array.isArray(facts)) return;
  host.textContent = "";
  facts.forEach((fact) => {
    const row = document.createElement("div");
    const dt = document.createElement("dt");
    const dd = document.createElement("dd");
    dt.textContent = fact.label;
    dd.textContent = String(fact.value);
    row.append(dt, dd);
    host.appendChild(row);
  });
}

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

  renderFacts("programFacts", program.core_facts);
  renderFacts("studyAFacts", studyA.core_facts);
  renderFacts("studyBFacts", studyB.core_facts);
  text("studyATitle", studyA.title_zh);
  text("studyBTitle", studyB.title_zh);
  text("studyAStatus", studyA.evidence_status_zh);
  text("studyBStatus", studyB.evidence_status_zh);
  text("studyADesign", studyA.design_summary_zh);
  text("studyBDesign", studyB.design_summary_zh);
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

setupNavigation();
loadOverview();
