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

setupNavigation();
loadOverview();
