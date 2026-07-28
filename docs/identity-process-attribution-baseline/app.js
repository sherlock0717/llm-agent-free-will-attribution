"use strict";

const DATA_ROOT = "../data/";
const STATUS = document.getElementById("pageStatus");
const GROUP_STATE = { story: "loading", measurement: "loading", analysis: "loading" };

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatNumber(value, digits = 3) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "—";
  return number.toFixed(digits).replace(/0+$/, "").replace(/\.$/, "");
}

function formatP(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "—";
  return number < 0.001 ? "< .001" : `= ${number.toFixed(3)}`;
}

async function fetchJson(name) {
  const response = await fetch(`${DATA_ROOT}${name}`, { cache: "no-store" });
  if (!response.ok) throw new Error(`${name}: HTTP ${response.status}`);
  return response.json();
}

function updateStatus() {
  if (!STATUS) return;
  const states = Object.values(GROUP_STATE);
  const success = states.filter((state) => state === "success").length;
  const error = states.filter((state) => state === "error").length;
  const loading = states.filter((state) => state === "loading").length;
  if (success === states.length) {
    STATUS.textContent = "公开研究数据已载入。";
    STATUS.dataset.kind = "success";
  } else if (error > 0) {
    STATUS.textContent = `已载入 ${success} 组数据；${error} 组数据提供重新加载入口。`;
    STATUS.dataset.kind = "partial";
  } else if (loading > 0) {
    STATUS.textContent = "正在载入公开研究数据……";
    STATUS.dataset.kind = "loading";
  }
}

function errorPanel(targetId, title, error, retry) {
  const target = document.getElementById(targetId);
  if (!target) return;
  target.innerHTML = `
    <div class="error-panel">
      <strong>${escapeHtml(title)}</strong>
      <p>页面已保留静态研究说明，可重新载入该数据区。</p>
      <button type="button" class="retry-btn">重新加载</button>
      <details><summary>技术信息</summary><code>${escapeHtml(error.message || error)}</code></details>
    </div>`;
  target.querySelector("button")?.addEventListener("click", retry, { once: true });
}

async function runGroup(name, loader) {
  GROUP_STATE[name] = "loading";
  updateStatus();
  try {
    await loader();
    GROUP_STATE[name] = "success";
  } catch (error) {
    GROUP_STATE[name] = "error";
    throw error;
  } finally {
    updateStatus();
  }
}

function renderScenarios(story) {
  const target = document.getElementById("scenarioCards");
  const rows = story.scenarios || [];
  target.innerHTML = rows.map((row) => `
    <article class="scenario-card">
      <div class="card-head"><span>${escapeHtml(row.domain)}</span><code>${escapeHtml(row.id)}</code></div>
      <h3>${escapeHtml(row.label)}</h3>
      <p>${escapeHtml(row.context)}</p>
      <dl>
        <div><dt>方案A</dt><dd>${escapeHtml(row.option_a)}</dd></div>
        <div><dt>方案B</dt><dd>${escapeHtml(row.option_b)}</dd></div>
        <div><dt>材料固定选择</dt><dd>${escapeHtml(row.fixed_choice)}</dd></div>
      </dl>
    </article>`).join("");
}

function renderConstructs(measurement) {
  const target = document.getElementById("constructCards");
  const rows = measurement.constructs || [];
  target.innerHTML = rows.map((row) => `
    <article class="construct-card">
      <div class="card-head"><span>${escapeHtml(row.role)}</span><code>${escapeHtml(row.key)}</code></div>
      <h3>${escapeHtml(row.label)}</h3>
      <p>${escapeHtml(row.note)}</p>
      <dl class="construct-meta">
        <div><dt>题项</dt><dd>${escapeHtml(row.n_items)}</dd></div>
        <div><dt>量尺</dt><dd>${escapeHtml(row.range)}</dd></div>
        <div><dt>完整记录</dt><dd>${escapeHtml(row.n_cases)}</dd></div>
        <div><dt>Cronbach α</dt><dd>${formatNumber(row.alpha)}</dd></div>
      </dl>
    </article>`).join("");
}

function renderTakeaways(story) {
  const target = document.getElementById("takeaways");
  target.innerHTML = `<ol>${(story.result_takeaways || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ol>`;
}

function renderConditionTable(results) {
  const target = document.getElementById("conditionTable");
  const profile = results.condition_profile;
  const conditions = profile.conditions || [];
  const labels = profile.condition_labels || {};
  const series = profile.series || [];
  const values = Object.fromEntries(series.map((row) => [row.construct, Object.fromEntries(row.points.map((point) => [point.condition, point.value]))]));

  target.innerHTML = `
    <table>
      <thead><tr><th>过程条件</th>${series.map((row) => `<th>${escapeHtml(row.label)}</th>`).join("")}</tr></thead>
      <tbody>${conditions.map((condition) => `
        <tr>
          <th>${escapeHtml(labels[condition] || condition)}</th>
          ${series.map((row) => `<td>${formatNumber(values[row.construct]?.[condition])}</td>`).join("")}
        </tr>`).join("")}</tbody>
    </table>`;
}

function renderIdentityEffects(results) {
  const target = document.getElementById("identityEffects");
  const effects = results.identity_effect?.effects || [];
  target.innerHTML = effects.map((row) => {
    const eta = Math.max(0, Math.min(1, Number(row.partial_eta_sq) || 0));
    const means = Object.entries(row.means_by_identity || {})
      .map(([label, value]) => `${escapeHtml(label)} ${formatNumber(value)}`)
      .join(" · ");
    return `
      <article class="effect-row">
        <div class="effect-label"><strong>${escapeHtml(row.label)}</strong><span>${means}</span></div>
        <div class="effect-track" aria-label="partial eta squared ${formatNumber(eta)}"><span style="width:${eta * 100}%"></span></div>
        <div class="effect-stat">η²p=${formatNumber(eta)} · F=${formatNumber(row.F, 2)} · p ${formatP(row.p)}</div>
      </article>`;
  }).join("");
}

function renderContrasts(results) {
  const target = document.getElementById("contrastTables");
  const groups = results.planned_contrasts?.groups || [];
  target.innerHTML = groups.map((group) => `
    <article class="contrast-group">
      <h3>${escapeHtml(group.label)}</h3>
      <div class="table-scroll"><table>
        <thead><tr><th>比较</th><th>均值A</th><th>均值B</th><th>差值</th><th>t</th><th>p</th></tr></thead>
        <tbody>${group.contrasts.map((row) => `
          <tr><th>${escapeHtml(row.label)}</th><td>${formatNumber(row.mean_a)}</td><td>${formatNumber(row.mean_b)}</td><td>${formatNumber(row.diff)}</td><td>${formatNumber(row.t)}</td><td>${formatP(row.p)}</td></tr>`).join("")}</tbody>
      </table></div>
    </article>`).join("");
}

async function loadStoryGroup() {
  try {
    const story = await fetchJson("showcase_story.json");
    renderScenarios(story);
    renderTakeaways(story);
  } catch (error) {
    const retry = () => runGroup("story", loadStoryGroup);
    errorPanel("scenarioCards", "场景数据", error, retry);
    errorPanel("takeaways", "结果摘要", error, retry);
    throw error;
  }
}

async function loadMeasurementGroup() {
  try {
    renderConstructs(await fetchJson("measurement_summary.json"));
  } catch (error) {
    errorPanel("constructCards", "构念数据", error, () => runGroup("measurement", loadMeasurementGroup));
    throw error;
  }
}

async function loadAnalysisGroup() {
  try {
    const results = await fetchJson("analysis_results.json");
    renderConditionTable(results);
    renderIdentityEffects(results);
    renderContrasts(results);
  } catch (error) {
    const retry = () => runGroup("analysis", loadAnalysisGroup);
    for (const [id, title] of [
      ["conditionTable", "条件均值"],
      ["identityEffects", "身份效应"],
      ["contrastTables", "条件比较"],
    ]) errorPanel(id, title, error, retry);
    throw error;
  }
}

updateStatus();
Promise.allSettled([
  runGroup("story", loadStoryGroup),
  runGroup("measurement", loadMeasurementGroup),
  runGroup("analysis", loadAnalysisGroup),
]);
