"use strict";

const DATA_ROOT = "../data/";
const STATUS = document.getElementById("pageStatus");
const GROUP_STATE = { story: "loading", measurement: "loading", analysis: "loading", scenario: "loading", robustness: "loading" };
const CONSTRUCT_LABELS_ZH = {
  subjective_process_completeness: "主观过程完整性",
  agency: "能动性",
  free_will_attribution: "自由意志归因",
  perceived_intelligence: "感知智能",
  responsibility_total: "责任总分",
};
const PUBLIC_TAKEAWAYS = [
  "理由与反思描述对应更高的能动性评价：从直接选择到给出理由、再到加入反思反馈，能动性评分总体抬升。",
  "AI与人类身份标签对应了自由意志、体验与责任相关评分上的系统差异。",
  "能动性与自由意志归因关系紧密：两者在这批响应中一起变化，同时各自保留清晰的过程条件模式。",
  "这些差异在八类场景中方向大体一致，去掉任意一个场景后的整体结果保持稳定。",
  "研究A结果描述该DeepSeek配置在本材料集与问卷模拟Prompt中的归因反应。",
];

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
  target.innerHTML = (story.scenarios || []).map((row) => `
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
  target.innerHTML = (measurement.constructs || []).map((row) => `
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

function renderTakeaways() {
  document.getElementById("takeaways").innerHTML = `<ol>${PUBLIC_TAKEAWAYS.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ol>`;
}

// The four main findings stay fixed and are ordered by the research questions,
// not by whichever contrast happens to have the largest absolute difference.
// The scenario summary only fills in the numeric range of the consistency
// finding (item four), so a large value never re-orders the findings.
function renderTakeawaysFromScenario(summary) {
  const rows = (summary.public_contrast_summary || []).filter((row) => row.scope === "all_identities");
  if (!rows.length) { renderTakeaways(); return; }
  const consistency = rows.map((row) => Number(row.direction_consistency)).filter(Number.isFinite);
  const minConsistency = consistency.length ? Math.min(...consistency) : null;
  const items = PUBLIC_TAKEAWAYS.slice();
  items[3] =
    `这些差异在八类场景中方向大体一致：${summary.record_count}条响应汇总为` +
    `${summary.unit_count}个场景×身份×过程条件单元，` +
    (minConsistency != null
      ? `预设对比的方向一致率最低为${formatNumber(minConsistency, 2)}，`
      : "") +
    "去掉任意一个场景后的整体结果保持稳定。";
  document.getElementById("takeaways").innerHTML = `<ol>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ol>`;
}

function scenarioContrastRow(row) {
  return `<tr>
    <th>${escapeHtml(row.contrast_id)} · ${escapeHtml(row.contrast_label)}</th>
    <td>${formatNumber(row.mean_difference)}</td>
    <td>${escapeHtml(row.positive_count)} / ${escapeHtml(row.negative_count)}</td>
    <td>${formatNumber(row.direction_consistency, 2)}</td>
    <td>[${formatNumber(row.scenario_mean_min)}, ${formatNumber(row.scenario_mean_max)}]</td>
    <td>[${formatNumber(row.leave_one_scenario_mean_min)}, ${formatNumber(row.leave_one_scenario_mean_max)}]</td>
  </tr>`;
}

function renderScenarioConstruct(summary, construct) {
  const rows = (summary.public_contrast_summary || [])
    .filter((row) => row.scope === "all_identities" && row.construct === construct);
  const target = document.getElementById("scenarioResult");
  target.innerHTML = `<div class="table-scroll"><table class="scenario-table">
    <thead><tr>
      <th>比较内容</th><th>平均变化</th><th>呈现相同方向的单元</th>
      <th>场景间一致程度</th><th>八个场景中的变化范围</th><th>去掉任意一个场景后的范围</th>
    </tr></thead>
    <tbody>${rows.map(scenarioContrastRow).join("")}</tbody>
  </table></div>`;
}

// Finding 3 first-layer chart: scenario consistency.
// The construct/contrast pair is fixed (agency × contrast A4, high-structure
// process vs long-text direct choice), chosen ahead of time to match the primary
// process construct. It is NOT selected by largest absolute difference, smallest
// p-value or largest effect size. The chart only counts how the 16 scenario×identity
// units move (same / opposite / no direction) and shows the raw-scale ranges; the
// full per-construct table stays in the collapsed technical block.
const SCENARIO_FINDING_CONSTRUCT = "agency";
const SCENARIO_FINDING_CONTRAST = "A4";

function renderScenarioFindingChart(summary) {
  const target = document.getElementById("scenarioFindingChart");
  if (!target) return;
  const row = (summary.public_contrast_summary || []).find(
    (item) => item.scope === "all_identities"
      && item.construct === SCENARIO_FINDING_CONSTRUCT
      && item.contrast_id === SCENARIO_FINDING_CONTRAST);
  if (!row) return;
  const same = Number(row.positive_count) || 0;
  const opposite = Number(row.negative_count) || 0;
  const zero = Number(row.zero_count) || 0;
  const total = same + opposite + zero;
  const seg = (label, count, cls) => {
    if (total <= 0 || count <= 0) return "";
    const pct = (count / total) * 100;
    return `<span class="stack-seg ${cls}" style="width:${pct.toFixed(1)}%"><span class="stack-count">${count}</span></span>`;
  };
  const scenarioRange = `[${formatNumber(row.scenario_mean_min, 2)}, ${formatNumber(row.scenario_mean_max, 2)}]`;
  const looRange = `[${formatNumber(row.leave_one_scenario_mean_min, 2)}, ${formatNumber(row.leave_one_scenario_mean_max, 2)}]`;
  target.setAttribute(
    "aria-label",
    `共${total}个场景与身份组合：变化方向相同${same}个、方向相反${opposite}个、没有变化${zero}个；`
    + `八个场景中的变化范围${scenarioRange}，依次排除一个场景后的变化范围${looRange}。`);
  target.innerHTML = `
    <div class="stack-bar">
      ${seg("相同方向", same, "same")}
      ${seg("相反方向", opposite, "opp")}
      ${seg("没有变化", zero, "zero")}
    </div>
    <ul class="stack-legend">
      <li><span class="dot same"></span>相同方向 ${same}</li>
      <li><span class="dot opp"></span>相反方向 ${opposite}</li>
      <li><span class="dot zero"></span>没有变化 ${zero}</li>
      <li class="stack-total">共 ${total} 个场景与身份组合</li>
    </ul>
    <dl class="stack-range">
      <div><dt>八个场景中的变化范围</dt><dd>${scenarioRange}</dd></div>
      <div><dt>依次排除一个场景后的变化范围</dt><dd>${looRange}</dd></div>
    </dl>`;
}

function renderScenarioAnalysis(summary) {
  const intro = document.getElementById("scenarioIntro");
  if (intro) {
    intro.textContent =
      `${summary.record_count}条模型响应按场景、身份和过程条件汇总为` +
      `${summary.unit_count}个分析单元（${summary.scenario_count}个场景、${summary.identity_count}种身份、` +
      `${summary.condition_count}种过程条件）。下表按评价维度读取每个比较在这些单元上的平均变化、方向一致程度，` +
      "以及去掉任意一个场景后结果的变化范围。数值保留各维度原量尺。";
  }
  renderScenarioFindingChart(summary);
  const controls = document.getElementById("scenarioControls");
  const select = document.getElementById("scenarioConstructSelect");
  const constructs = summary.public_constructs || [];
  select.innerHTML = constructs
    .map((key) => `<option value="${escapeHtml(key)}">${escapeHtml(CONSTRUCT_LABELS_ZH[key] || key)}</option>`)
    .join("");
  select.onchange = () => renderScenarioConstruct(summary, select.value);
  if (controls) controls.hidden = false;
  if (constructs.length) renderScenarioConstruct(summary, constructs[0]);
  renderTakeawaysFromScenario(summary);
}



function renderConditionTable(results) {
  const target = document.getElementById("conditionTable");
  const profile = results.condition_profile;
  const conditions = profile.conditions || [];
  const labels = profile.condition_labels || {};
  const series = profile.series || [];
  const values = Object.fromEntries(series.map((row) => [row.construct, Object.fromEntries(row.points.map((point) => [point.condition, point.value]))]));
  target.innerHTML = `<table><thead><tr><th>过程条件</th>${series.map((row) => `<th>${escapeHtml(row.label)}</th>`).join("")}</tr></thead><tbody>${conditions.map((condition) => `<tr><th>${escapeHtml(labels[condition] || condition)}</th>${series.map((row) => `<td>${formatNumber(values[row.construct]?.[condition])}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
}

// Finding 1 first-layer chart: process-condition means.
// The evaluation dimension is fixed to "agency" (能动性), chosen ahead of time
// because it is the pre-registered primary construct for the process manipulation
// (stability.points[0] in analysis_results.json describes agency as the most
// direction-stable primary result). It is NOT selected by largest absolute
// difference. All six conditions C0–C5 are shown on the construct's own 1–7 scale.
const PROCESS_FINDING_CONSTRUCT = "agency";

function renderProcessFindingChart(results) {
  const svg = document.getElementById("processFindingChart");
  if (!svg) return;
  const profile = results.condition_profile || {};
  const series = (profile.series || []).find((row) => row.construct === PROCESS_FINDING_CONSTRUCT);
  if (!series || !series.points || !series.points.length) return;
  const points = series.points;
  const W = 640, H = 260, padL = 52, padR = 24, padT = 28, padB = 56;
  const plotW = W - padL - padR, plotH = H - padT - padB;
  // Fixed raw scale 1–7 (constructs use a 1–7 range per condition_profile.scale_note).
  const yMin = 1, yMax = 7;
  const x = (i) => padL + (points.length === 1 ? plotW / 2 : (plotW * i) / (points.length - 1));
  const y = (v) => padT + plotH - ((v - yMin) / (yMax - yMin)) * plotH;
  const gridVals = [1, 2, 3, 4, 5, 6, 7];
  const gridLines = gridVals.map((v) => `<line x1="${padL}" y1="${y(v).toFixed(1)}" x2="${(W - padR)}" y2="${y(v).toFixed(1)}" class="chart-grid" /><text x="${padL - 8}" y="${(y(v) + 4).toFixed(1)}" class="chart-axis-label" text-anchor="end">${v}</text>`).join("");
  const path = points.map((p, i) => `${i === 0 ? "M" : "L"}${x(i).toFixed(1)},${y(p.value).toFixed(1)}`).join(" ");
  const dots = points.map((p, i) => `<circle cx="${x(i).toFixed(1)}" cy="${y(p.value).toFixed(1)}" r="4" class="chart-dot" /><text x="${x(i).toFixed(1)}" y="${(y(p.value) - 10).toFixed(1)}" class="chart-value" text-anchor="middle">${formatNumber(p.value, 2)}</text>`).join("");
  const xLabels = points.map((p, i) => `<text x="${x(i).toFixed(1)}" y="${(H - padB + 20).toFixed(1)}" class="chart-cat" text-anchor="middle">C${i}</text>`).join("");
  const summary = points.map((p, i) => `C${i} ${escapeHtml(p.label)} ${formatNumber(p.value, 2)}`).join("，");
  svg.setAttribute("aria-label", `${escapeHtml(series.label)}在六种过程条件下的平均评分，原始量尺1至7：${summary}`);
  svg.innerHTML = `${gridLines}<path d="${path}" class="chart-line" fill="none" />${dots}${xLabels}`;
}

function renderIdentityEffects(results) {
  const target = document.getElementById("identityEffects");
  target.innerHTML = (results.identity_effect?.effects || []).map((row) => {
    const eta = Math.max(0, Math.min(1, Number(row.partial_eta_sq) || 0));
    const means = Object.entries(row.means_by_identity || {}).map(([label, value]) => `${escapeHtml(label)} ${formatNumber(value)}`).join(" · ");
    return `<article class="effect-row"><div class="effect-label"><strong>${escapeHtml(row.label)}</strong><span>${means}</span></div><div class="effect-track" aria-label="partial eta squared ${formatNumber(eta)}"><span style="width:${eta * 100}%"></span></div><div class="effect-stat">η²p=${formatNumber(eta)} · F=${formatNumber(row.F, 2)} · p ${formatP(row.p)}</div></article>`;
  }).join("");
}

// Finding 2 first-layer chart: identity-label comparison.
// The evaluation dimension is fixed to "free_will_attribution" (自由意志归因),
// chosen ahead of time because it is the pre-registered primary mind/responsibility
// construct for the identity manipulation (it is the identity contrast highlighted
// in stability.points and planned_contrasts). It is NOT selected by largest effect.
// Only this single construct is shown at the first layer; the full identity table
// stays in the collapsed block.
const IDENTITY_FINDING_CONSTRUCT = "free_will_attribution";

function renderIdentityFindingChart(results) {
  const target = document.getElementById("identityFindingChart");
  if (!target) return;
  const effect = (results.identity_effect?.effects || []).find((row) => row.construct === IDENTITY_FINDING_CONSTRUCT);
  if (!effect || !effect.means_by_identity) return;
  const entries = Object.entries(effect.means_by_identity);
  const yMax = 7; // raw 1–7 scale
  const rows = entries.map(([label, value]) => {
    const pct = Math.max(0, Math.min(100, (Number(value) / yMax) * 100));
    return `<div class="bar-row"><span class="bar-name">${escapeHtml(label)}</span><span class="bar-track"><span class="bar-fill" style="width:${pct.toFixed(1)}%"></span></span><span class="bar-value">${formatNumber(value, 2)}</span></div>`;
  }).join("");
  const summary = entries.map(([label, value]) => `${escapeHtml(label)} ${formatNumber(value, 2)}`).join("，");
  target.setAttribute("aria-label", `${escapeHtml(effect.label)}在AI标签与人类标签下的平均评分，原始量尺1至7：${summary}`);
  target.innerHTML = `<div class="bar-scale">量尺 1–7</div>${rows}`;
}

function renderContrasts(results) {
  const target = document.getElementById("contrastTables");
  target.innerHTML = (results.planned_contrasts?.groups || []).map((group) => `
    <article class="contrast-group"><h3>${escapeHtml(group.label)}</h3><div class="table-scroll"><table>
      <thead><tr><th>比较</th><th>均值A</th><th>均值B</th><th>差值</th><th>t</th><th>p</th></tr></thead>
      <tbody>${group.contrasts.map((row) => `<tr><th>${escapeHtml(row.label)}</th><td>${formatNumber(row.mean_a)}</td><td>${formatNumber(row.mean_b)}</td><td>${formatNumber(row.diff)}</td><td>${formatNumber(row.t)}</td><td>${formatP(row.p)}</td></tr>`).join("")}</tbody>
    </table></div></article>`).join("");
}

// --- Robustness (existing-data diagnostics) --------------------------------
const ROBUST_STATUS_LABELS = {
  cross_scenario_stable: "跨场景较稳定",
  scenario_dependent: "存在明显场景依赖",
  limited_evidence: "证据有限",
};

function renderRobustnessModules(summary) {
  const findings = summary.public_findings || {};
  const proc = findings.process_information;

  // module 1: does the majority of scenario×identity units keep one direction?
  if (proc) {
    setText("#robustDirection .robust-conclusion",
      `在${proc.total_unit_count}个场景与身份组合中，${proc.direction_majority_count}个保持相同方向；`
      + `依次去掉一个场景后，平均差异${proc.leave_one_scenario_same_sign ? "始终保持同号" : "出现跨零"}。`);
    setText('[data-robust="direction-number"]', `${proc.direction_majority_count}/${proc.total_unit_count}`);
    renderStackVisual(document.querySelector('[data-robust-figure="direction"]'),
      proc.direction_majority_count, proc.total_unit_count - proc.direction_majority_count);
  }

  // module 2: does a small number of scenarios drive the overall result?
  if (proc && (proc.scenario_influence || []).length) {
    const top = proc.scenario_influence[0];
    const after = top.leave_one_effect;
    setText("#robustInfluence .robust-conclusion",
      `影响最大的场景（${top.scenario_id}）被排除后，平均差异从${formatNumber(proc.full_effect, 2)}`
      + `变为${formatNumber(after, 2)}。`);
    setText('[data-robust="influence-number"]', formatNumber(top.influence, 3));
    renderInfluenceVisual(document.querySelector('[data-robust-figure="influence"]'),
      proc.scenario_influence.slice(0, 5));
  }

  // module 3: how does the result change after adding text length?
  const length = proc?.length_sensitivity;
  if (length) {
    const flip = length.direction_flips ? "方向发生改变" : "方向没有改变";
    setText("#robustLength .robust-conclusion",
      `加入字符数和句子数后，A4估计由${formatNumber(length.base_estimate, 2)}`
      + `变为${formatNumber(length.length_adjusted_estimate, 2)}，${flip}。`
      + "由于文本长度与过程条件共同变化，这一分析说明估计对模型设定较敏感，"
      + "无法据此分离文本长度和过程信息各自的独立作用。");
    const pct = length.absolute_shrink_ratio != null
      ? `${(length.absolute_shrink_ratio * 100).toFixed(0)}%` : "—";
    setText('[data-robust="length-number"]', pct);
    renderLengthVisual(document.querySelector('[data-robust-figure="length"]'),
      length.base_estimate, length.length_adjusted_estimate);
  }

  renderEvidenceStatusTable(summary);
}

function setText(selector, text) {
  const el = document.querySelector(selector);
  if (el) { el.textContent = text; el.classList.remove("loading"); }
}

function renderStackVisual(target, same, other) {
  if (!target) return;
  const total = same + other || 1;
  target.setAttribute("aria-label", `方向相同${same}个，其余${other}个，共${total}个组合`);
  target.innerHTML = `<div class="stack-bar"><span class="stack-seg same" style="width:${(same / total * 100).toFixed(1)}%">${same}</span>`
    + (other > 0 ? `<span class="stack-seg rest" style="width:${(other / total * 100).toFixed(1)}%">${other}</span>` : "")
    + `</div>`;
}

function renderInfluenceVisual(target, rows) {
  if (!target) return;
  const max = Math.max(...rows.map((r) => Math.abs(r.influence || 0)), 0.0001);
  target.setAttribute("aria-label", rows.map((r) => `${r.scenario_id} 影响 ${formatNumber(r.influence, 3)}`).join("，"));
  target.innerHTML = rows.map((r) => `<div class="mini-bar-row"><span class="mini-bar-name">${escapeHtml(r.scenario_id)}</span>`
    + `<span class="mini-bar-track"><span class="mini-bar-fill${r.direction_changes ? " flip" : ""}" style="width:${(Math.abs(r.influence || 0) / max * 100).toFixed(1)}%"></span></span>`
    + `<span class="mini-bar-value">${formatNumber(r.influence, 3)}</span></div>`).join("");
}

function renderLengthVisual(target, base, adjusted) {
  if (!target) return;
  const max = Math.max(Math.abs(base || 0), Math.abs(adjusted || 0), 0.0001);
  target.setAttribute("aria-label", `原估计${formatNumber(base, 2)}，加入长度后${formatNumber(adjusted, 2)}`);
  target.innerHTML = `<div class="mini-bar-row"><span class="mini-bar-name">原估计</span>`
    + `<span class="mini-bar-track"><span class="mini-bar-fill" style="width:${(Math.abs(base || 0) / max * 100).toFixed(1)}%"></span></span>`
    + `<span class="mini-bar-value">${formatNumber(base, 2)}</span></div>`
    + `<div class="mini-bar-row"><span class="mini-bar-name">加长度后</span>`
    + `<span class="mini-bar-track"><span class="mini-bar-fill alt" style="width:${(Math.abs(adjusted || 0) / max * 100).toFixed(1)}%"></span></span>`
    + `<span class="mini-bar-value">${formatNumber(adjusted, 2)}</span></div>`;
}

function renderEvidenceStatusTable(summary) {
  const body = document.querySelector("#evidenceStatusTable tbody");
  if (!body) return;
  const f = summary.public_findings || {};
  const proc = f.process_information;
  const ident = f.identity_label;
  const scen = f.scenario_dependence;
  const rows = [];
  if (proc) {
    rows.push({
      finding: "过程信息进入能动性评价",
      status: proc.status_label,
      support: `${proc.construct_label}｜过程对比${proc.contrast_id}｜同方向${proc.direction_majority_count}/${proc.total_unit_count}`,
      limit: proc.leave_one_scenario_same_sign ? "总体估计随场景有幅度变化" : "留一场景后方向不稳定",
    });
  }
  if (ident) {
    rows.push({
      finding: "身份标签改变自由意志归因",
      status: ident.status_label,
      support: `${ident.construct_label}｜human−AI｜同方向${ident.direction_majority_count}/${ident.total_unit_count}`,
      limit: ident.leave_one_scenario_same_sign ? "身份差随场景有幅度变化" : "留一场景后方向不稳定",
    });
  }
  if (scen) {
    rows.push({
      finding: "结论方向重复但幅度依赖场景",
      status: "方向一致但幅度存在场景差异",
      support: `过程范围${JSON.stringify(scen.process_effect_range)}｜身份范围${JSON.stringify(scen.identity_effect_range)}`,
      limit: `影响最大场景：过程${scen.largest_process_influence}／身份${scen.largest_identity_influence}`,
    });
  }
  body.innerHTML = rows.slice(0, 4).map((row) =>
    `<tr><th>${escapeHtml(row.finding)}</th><td>${escapeHtml(row.status)}</td>`
    + `<td>${escapeHtml(row.support)}</td><td>${escapeHtml(row.limit)}</td></tr>`).join("");
}

async function loadRobustnessGroup() {
  try {
    renderRobustnessModules(await fetchJson("research_a_robustness_summary.json"));
  } catch (error) {
    const retry = () => runGroup("robustness", loadRobustnessGroup);
    errorPanel("robustDirection", "稳健性结果", error, retry);
    throw error;
  }
}

async function loadStoryGroup() {
  try {
    renderScenarios(await fetchJson("showcase_story.json"));
    renderTakeaways();
  } catch (error) {
    const retry = () => runGroup("story", loadStoryGroup);
    errorPanel("scenarioCards", "场景数据", error, retry);
    renderTakeaways();
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
    renderProcessFindingChart(results);
    renderIdentityEffects(results);
    renderIdentityFindingChart(results);
    renderContrasts(results);
  } catch (error) {
    const retry = () => runGroup("analysis", loadAnalysisGroup);
    for (const [id, title] of [["conditionTable", "条件均值"], ["identityEffects", "身份效应"], ["contrastTables", "条件比较"]]) errorPanel(id, title, error, retry);
    throw error;
  }
}

async function loadScenarioGroup() {
  try {
    renderScenarioAnalysis(await fetchJson("research_a_scenario_summary.json"));
  } catch (error) {
    const retry = () => runGroup("scenario", loadScenarioGroup);
    errorPanel("scenarioResult", "场景一致性结果", error, retry);
    throw error;
  }
}

renderTakeaways();
updateStatus();
Promise.allSettled([
  runGroup("story", loadStoryGroup),
  runGroup("measurement", loadMeasurementGroup),
  runGroup("analysis", loadAnalysisGroup),
  runGroup("scenario", loadScenarioGroup),
  runGroup("robustness", loadRobustnessGroup),
]);
