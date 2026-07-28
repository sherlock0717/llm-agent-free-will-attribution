// 研究B（机器主体决策过程归因评测）中文展示页。读取 data/showcase_data.json（流程演示数据）。
"use strict";

const CONDS = ["C0", "C1", "C2", "C3", "C4", "C5"];
const ALL_CONSTRUCTS = ["IN", "GO", "MSI", "IC", "PA5", "PA8"];

// Reader-facing construct labels and short descriptions used by the demo
// selector and tables. The full construct cards are static markup in index.html.
const CONSTRUCT_META = {
  IN: {
    name: "知觉独立性",
    option: "知觉独立性（IN）",
    description: "评判模型是否把机器主体看作能够相对独立地形成决定。",
  },
  GO: {
    name: "目标导向性",
    option: "目标导向性（GO）",
    description: "评判模型是否把机器主体看作具有目标导向的决策过程。",
  },
  MSI: {
    name: "心理状态推断",
    option: "心理状态推断（MSI）",
    description: "评判模型是否向机器主体归因意识、思考、意图等心理状态。",
  },
  IC: {
    name: "影响能力",
    option: "影响能力（IC）",
    description: "评判模型是否认为机器主体具有影响决定与结果的能力。",
  },
  PA5: {
    name: "感知能动性补充指标",
    option: "感知能动性补充指标（PA5）",
    description: "PA 2024 感知能动性指标的五题官方成员子分数。",
  },
  PA8: {
    name: "感知能动性补充指标",
    option: "感知能动性补充指标（PA8）",
    description: "PA 2024 感知能动性指标的八题官方成员子分数。",
  },
};

// 主图条件标签：横轴用短标签 C0—C5，完整中文名称放在图例/表格。
const CONDITION_SHORT = {
  C0: "直接决定",
  C1: "明确备选",
  C2: "给出理由",
  C3: "收到反馈",
  C4: "维持决定",
  C5: "改变决定",
};

// 面向读者的 P1—P6 比较逻辑（叙事层；不改动数据文件中的 contrast_id 与统计值）。
const CONTRAST_CARDS = [
  {
    id: "P1", diff: "C1−C0", name: "加入明确备选方案",
    comparison: "比较呈现备选方案与直接决定。",
    reading: "用于观察评判模型对可选方案线索的敏感性。",
  },
  {
    id: "P2", diff: "C2−C0", name: "给出明确理由",
    comparison: "比较明确理由条件与直接决定。",
    reading: "参考条件为C0，因此它呈现的是明确理由条件与直接决定之间的整体差异。",
  },
  {
    id: "P3", diff: "C3−C2", name: "加入反馈",
    comparison: "比较收到反馈与只呈现决定及理由。",
    reading: "用于观察反馈信息加入后的评分变化。",
  },
  {
    id: "P4", diff: "C4−C2", name: "反馈后维持决定",
    comparison: "比较反馈并维持决定与只呈现决定及理由。",
    reading: "该差异同时包含反馈和维持决定两部分信息。",
  },
  {
    id: "P5", diff: "C5−C2", name: "反馈后改变决定",
    comparison: "比较反馈并改变决定与只呈现决定及理由。",
    reading: "该差异同时包含反馈和改变决定两部分信息。",
  },
  {
    id: "P6", diff: "C5−C4", name: "改变与维持",
    comparison: "在相同反馈结构下比较改变决定与维持决定。",
    reading: "用于观察评判模型对两种后续行为的相对敏感性。",
  },
];

const CONDITION_META = {
  C0: { title: "直接作出决定", du: "D0-U0", added: "只呈现最终决定，不展示备选方案、理由或反馈。", role: "P1、P2的参考条件" },
  C1: { title: "呈现备选方案后决定", du: "D1-U0", added: "在直接决定基础上加入备选方案。", role: "P1的对照条件" },
  C2: { title: "决定并说明理由", du: "D2-U0", added: "在决定基础上加入明确理由。", role: "P2、P3、P4、P5的参考条件" },
  C3: { title: "说明理由并收到反馈", du: "D2-U1", added: "在理由基础上加入外部反馈，无第二次决定。", role: "P3的对照条件" },
  C4: { title: "收到反馈后维持决定", du: "D2-U2", added: "在反馈基础上再次决定维持原选择。", role: "P4、P6的对照条件" },
  C5: { title: "收到反馈后改变决定", du: "D2-U3", added: "在反馈基础上再次决定改选另一方案。", role: "P5、P6的对照条件" },
};

const SCENARIO_META = {
  s1_scheduling: "会议排期",
  s2_customer_issue: "客户问题处理",
  s3_study_plan: "学习计划",
  s4_routing: "路线与物流",
  s5_task_allocation: "团队任务分配",
  s6_content_recommendation: "内容推荐",
  s7_game_strategy: "游戏策略",
  s8_energy_plan: "节能方案",
};

const CONTRAST_META = {
  P1: "呈现备选方案的差异（C1−C0）",
  P2: "明确说明理由的差异（C2−C0）",
  P3: "仅增加反馈的差异（C3−C2）",
  P4: "反馈后维持决定的差异（C4−C2）",
  P5: "反馈后改变决定的差异（C5−C2）",
  P6: "改变决定与维持决定的差异（C5−C4）",
};

// 研究状态说明（集中在 #status 章节）。
const STATUS_NOTES = [
  "六个构念保留各自原量尺并分别报告。",
  "流程演示数据用于检查材料、评分、分析和页面输出。",
  "正式双模型运行将沿用已经固定的材料和分析计划。",
  "跨主体研究将使用独立的人类题项和可比性检验。",
];

let DATA = null;

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  Object.entries(attrs).forEach(([key, value]) => {
    if (key === "class") node.className = value;
    else if (key === "html") node.innerHTML = value;
    else node.setAttribute(key, value);
  });
  children.forEach((child) => {
    if (child == null) return;
    node.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
  });
  return node;
}

function fmt(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return Number(value).toFixed(digits);
}

function signed(value, digits = 3) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  const numeric = Number(value);
  return `${numeric >= 0 ? "+" : ""}${numeric.toFixed(digits)}`;
}

function constructLabel(key) {
  return `${CONSTRUCT_META[key]?.name || key}（${key}）`;
}

function setLoadStatus(message, kind = "loading") {
  const status = document.getElementById("loadStatus");
  status.className = `load-status ${kind}`;
  status.textContent = message;
}

// Static research design does not depend on the demo JSON, so it renders first
// and stays visible even if showcase_data.json fails to load. Only the dynamic
// slots (material browser, coverage numbers, demo metrics, tables, charts) need
// DATA and degrade gracefully when it is missing.
function renderStatic() {
  renderConditions();
  renderContrastCards();
  renderStatus();
  renderEntries();
  setupImageFallbacks();
  setupLightbox();
}

function renderDynamic() {
  renderCoverage();
  renderScenarioBrowser();
  renderDemoMetrics();
  renderConstructView();
  renderContrasts();
  renderAppendixConditionTable();
  renderFitSummary();
  renderScenarioHet();
}

async function load() {
  setLoadStatus("正在加载流程演示数据……", "loading");
  renderStatic();
  let response;
  try {
    response = await fetch("data/showcase_data.json", { cache: "no-store" });
  } catch (networkError) {
    throw new Error(`无法请求数据文件：${networkError}`);
  }
  if (!response.ok) throw new Error(`数据请求失败：HTTP ${response.status}`);
  DATA = await response.json();
  renderDynamic();
  clearDemoError();
  enableBrowserControls(true);
  document.getElementById("snapshotStatus").textContent = "流程演示已完成";
  setLoadStatus("流程演示数据已载入，可浏览材料、统计表与图表输出。", "success");
}

function enableBrowserControls(enabled) {
  ["scenSelect", "scenCondSelect", "scenDirSelect"].forEach((id) => {
    const node = document.getElementById(id);
    if (node) node.disabled = !enabled;
  });
}

function clearDemoError() {
  const panel = document.getElementById("demoError");
  if (panel) { panel.hidden = true; panel.innerHTML = ""; }
  const content = document.getElementById("demoContent");
  if (content) content.hidden = false;
}

// #design: six condition cards with D/U combo, added information, P-role.
function renderConditions() {
  const host = document.getElementById("conditionCards");
  host.innerHTML = "";
  CONDS.forEach((key) => {
    const meta = CONDITION_META[key];
    host.appendChild(el("article", { class: "condition-card" },
      el("div", { class: "condition-head" },
        el("span", { class: "cond-pill" }, key),
        el("span", { class: "du-tag" }, meta.du)
      ),
      el("h4", {}, meta.title),
      el("p", { class: "cond-added" }, meta.added),
      el("p", { class: "cond-role" }, `在P1—P6中：${meta.role}`)
    ));
  });
}

// #materials coverage matrix + balance panel (collapsed in <details>).
function renderCoverage() {
  const table = el("table", { class: "coverage-matrix" });
  const head = el("tr", {}, el("th", {}, "场景"));
  CONDS.forEach((condition) => head.appendChild(el("th", {}, condition)));
  table.appendChild(head);
  DATA.scenarios.forEach((scenarioId) => {
    const row = el("tr", {}, el("th", {}, SCENARIO_META[scenarioId] || scenarioId));
    CONDS.forEach((condition) => {
      const count = (DATA.scenario_materials[scenarioId] || []).filter((item) => item.condition_id === condition).length;
      row.appendChild(el("td", {}, el("strong", {}, `${count}条`), el("span", {}, "A / B")));
    });
    table.appendChild(row);
  });
  const matrixHost = document.getElementById("coverageMatrix");
  matrixHost.innerHTML = "";
  matrixHost.appendChild(table);

  const balance = document.getElementById("balancePanel");
  balance.innerHTML = "";
  balance.appendChild(el("h4", {}, "平衡性检查"));
  const rows = [
    ["每个条件", `${Object.values(DATA.material_balance.per_condition)[0]}条`],
    ["每个场景", `${Object.values(DATA.material_balance.per_scenario)[0]}条`],
    ["方向A", `${DATA.material_balance.per_direction.A}条`],
    ["方向B", `${DATA.material_balance.per_direction.B}条`],
    ["目标主体", "机器主体"],
  ];
  rows.forEach(([label, value]) => balance.appendChild(el("div", { class: "balance-row" },
    el("span", {}, label), el("strong", {}, value)
  )));
  balance.appendChild(el("p", { class: "small muted" }, "所有条件、场景和方向均完整覆盖。"));

  // sync the static material count with the actual dataset.
  const countNode = document.getElementById("materialCount");
  if (countNode && DATA.quality_summary && DATA.quality_summary.n_materials) {
    countNode.textContent = String(DATA.quality_summary.n_materials);
  }
}

function renderScenarioBrowser() {
  const scenarioSelect = document.getElementById("scenSelect");
  const conditionSelect = document.getElementById("scenCondSelect");
  const directionSelect = document.getElementById("scenDirSelect");
  scenarioSelect.innerHTML = conditionSelect.innerHTML = directionSelect.innerHTML = "";

  DATA.scenarios.forEach((scenarioId) => {
    scenarioSelect.appendChild(el("option", { value: scenarioId }, SCENARIO_META[scenarioId] || scenarioId));
  });
  CONDS.forEach((condition) => {
    conditionSelect.appendChild(el("option", { value: condition }, `${condition}｜${CONDITION_META[condition].title}`));
  });

  const DIRECTION_LABELS = { A: "方向A｜场景方案一", B: "方向B｜场景方案二" };
  const rebuildDirections = () => {
    directionSelect.innerHTML = "";
    ["A", "B"].forEach((direction) => {
      // 默认下拉只显示纯中文方案标签；具体英文决定仅在展开的英文原始材料中呈现。
      directionSelect.appendChild(el("option", { value: direction }, DIRECTION_LABELS[direction]));
    });
  };

  const update = () => {
    const scenarioId = scenarioSelect.value;
    const conditionId = conditionSelect.value;
    const direction = directionSelect.value;
    const material = (DATA.scenario_materials[scenarioId] || []).find(
      (item) => item.condition_id === conditionId && item.direction_version === direction
    );
    const host = document.getElementById("scenStim");
    host.innerHTML = "";
    if (!material) {
      host.appendChild(el("p", { class: "error-panel" }, "没有找到这一组合对应的材料。"));
      return;
    }
    host.appendChild(renderStim(material, scenarioId));
  };

  scenarioSelect.addEventListener("change", () => { rebuildDirections(); update(); });
  conditionSelect.addEventListener("change", update);
  directionSelect.addEventListener("change", update);
  rebuildDirections();
  update();
}

function renderStim(material, scenarioId = null) {
  const bridge = 'In the following items, "the machine" refers to the AI system described above.';
  let sourceText = material.complete_stimulus_text;
  if (sourceText.includes(bridge)) sourceText = sourceText.replace(bridge, "").trim();
  const scenarioName = SCENARIO_META[scenarioId] || SCENARIO_META[material.material_id.split("__")[1]] || "材料";
  const condition = CONDITION_META[material.condition_id];

  return el("article", { class: "stim" },
    el("div", { class: "stim-summary" },
      el("div", { class: "stim-meta" },
        el("span", { class: "badge" }, scenarioName),
        el("span", { class: "badge" }, `${material.condition_id}｜${condition.title}`),
        el("span", { class: "badge" }, `方向${material.direction_version}`)
      ),
      el("p", {}, `中文结构说明：该材料在“${scenarioName}”场景中，采用“${condition.title}”的信息结构，并选择方向${material.direction_version}。`)
    ),
    el("details", { class: "source-details" },
      el("summary", {}, "展开查看英文原始材料"),
      el("p", { class: "source-note" }, "以下保留评判模型实际接收的英文原文；上方中文内容用于说明材料结构。"),
      el("div", { class: "source-text" }, sourceText),
      el("div", { class: "bridge" }, "题项指称说明：后续量表中的“the machine”均指上述AI系统。")
    ),
    el("div", { class: "material-id" }, `材料ID：${material.material_id}`)
  );
}



function tableFrom(headers, rows, numericColumns = []) {
  const table = el("table");
  const headerRow = el("tr");
  headers.forEach((header, index) => headerRow.appendChild(el("th", numericColumns.includes(index) ? { class: "num" } : {}, header)));
  table.appendChild(headerRow);
  rows.forEach((row) => {
    const tr = el("tr");
    row.forEach((cellValue, index) => {
      const td = el("td", numericColumns.includes(index) ? { class: "num" } : {});
      if (cellValue && typeof cellValue === "object" && cellValue.node) td.appendChild(cellValue.node);
      else td.textContent = cellValue;
      tr.appendChild(td);
    });
    table.appendChild(tr);
  });
  return table;
}

// Parse a native scale string like "1-7" into numeric [min, max].
function scaleBounds(key) {
  const raw = String(DATA.constructs.native_scales[key] || "1-7");
  const parts = raw.split(/[-–—]/).map((piece) => Number(piece.trim()));
  const min = Number.isFinite(parts[0]) ? parts[0] : 1;
  const max = Number.isFinite(parts[1]) ? parts[1] : 7;
  return [min, max];
}

// #analysis: six reader-facing contrast cards (comparison + reading; no statistics).
function renderContrastCards() {
  const host = document.getElementById("contrastCards");
  if (!host) return;
  host.innerHTML = "";
  CONTRAST_CARDS.forEach((card) => {
    host.appendChild(el("article", { class: "contrast-card" },
      el("div", { class: "contrast-head" },
        el("span", { class: "cond-pill" }, card.id),
        el("span", { class: "diff-tag" }, card.diff)
      ),
      el("h4", {}, card.name),
      el("p", { class: "contrast-comparison" }, el("strong", {}, "比较："), card.comparison),
      el("p", { class: "contrast-reading" }, el("strong", {}, "读法："), card.reading)
    ));
  });
}

// #demo metrics: pipeline demonstration counters read from showcase_data.
function renderDemoMetrics() {
  const host = document.getElementById("demoMetrics");
  if (!host) return;
  host.innerHTML = "";
  const q = DATA.quality_summary;
  const contrastCount = DATA.model_adjusted_results.contrasts.length;
  const figureCount = DATA.figure_paths.length;
  [
    ["流程演示响应数", String(q.n_responses)],
    ["题项有效率", `${fmt(q.item_valid_rate * 100, 0)}%`],
    ["构念得分率", `${fmt(q.construct_scored_rate * 100, 0)}%`],
    ["预设对比数", String(contrastCount)],
    ["图表数量", String(figureCount)],
  ].forEach(([label, value]) => {
    host.appendChild(el("div", { class: "demo-metric" },
      el("strong", {}, value),
      el("span", {}, label)
    ));
  });
}

// #demo single-construct view: selector drives explain + scale + SVG + table.
function renderConstructView() {
  const select = document.getElementById("resConstructSelect");
  select.innerHTML = "";
  ALL_CONSTRUCTS.forEach((key) =>
    select.appendChild(el("option", { value: key }, CONSTRUCT_META[key].option)));
  select.value = "IN";

  const update = () => {
    const key = select.value;
    const meta = CONSTRUCT_META[key];
    const scaleText = DATA.constructs.native_scales[key];
    document.getElementById("constructExplain").textContent =
      `${meta.name}（${key}）：${meta.description}`;
    document.getElementById("chartScaleNote").textContent =
      `纵轴按当前构念原量尺 ${scaleText} 显示；1—5 与 1—7 构念分别使用各自坐标轴。`;
    renderConditionProfile(key);
    const values = DATA.descriptive_results.condition_means[key] || {};
    const rows = CONDS.map((condition) => [
      condition,
      CONDITION_META[condition].title,
      fmt(values[condition]),
      scaleText,
      "流程演示",
    ]);
    replaceTable("condResultTable",
      tableFrom(["条件ID", "条件名称", "流程演示均值", "原量尺", "数据状态"], rows, [2]));
  };

  select.addEventListener("change", update);
  update();
}

// Native inline SVG single-construct profile across C0—C5 (no external library).
function renderConditionProfile(key) {
  const svg = document.getElementById("conditionProfileChart");
  if (!svg) return;
  const NS = "http://www.w3.org/2000/svg";
  const meta = CONSTRUCT_META[key];
  const values = DATA.descriptive_results.condition_means[key] || {};
  const [minScale, maxScale] = scaleBounds(key);

  const W = 720;
  const H = 320;
  const padL = 54;
  const padR = 24;
  const padT = 44;
  const padB = 58;
  const plotW = W - padL - padR;
  const plotH = H - padT - padB;

  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.setAttribute("aria-label",
    `${meta.name}（${key}）在C0至C5六个条件下的流程演示平均得分，原量尺 ${minScale}—${maxScale}`);
  while (svg.firstChild) svg.removeChild(svg.firstChild);

  const mk = (tag, attrs = {}, text = null) => {
    const node = document.createElementNS(NS, tag);
    Object.entries(attrs).forEach(([k, v]) => node.setAttribute(k, v));
    if (text != null) node.textContent = text;
    return node;
  };

  svg.appendChild(mk("text",
    { x: padL, y: 24, class: "svg-title" },
    `${meta.name}（${key}）｜原量尺 ${minScale}—${maxScale}`));

  const x = (i) => padL + (plotW * i) / (CONDS.length - 1);
  const y = (v) => padT + plotH - (plotH * (v - minScale)) / (maxScale - minScale);

  const ticks = 4;
  for (let t = 0; t <= ticks; t += 1) {
    const val = minScale + ((maxScale - minScale) * t) / ticks;
    const gy = y(val);
    svg.appendChild(mk("line",
      { x1: padL, y1: gy, x2: W - padR, y2: gy, class: "svg-grid" }));
    svg.appendChild(mk("text",
      { x: padL - 8, y: gy + 4, class: "svg-tick", "text-anchor": "end" },
      val.toFixed(0)));
  }

  CONDS.forEach((cond, i) => {
    svg.appendChild(mk("text",
      { x: x(i), y: H - padB + 20, class: "svg-xlabel", "text-anchor": "middle" }, cond));
    svg.appendChild(mk("text",
      { x: x(i), y: H - padB + 38, class: "svg-xsub", "text-anchor": "middle" },
      CONDITION_SHORT[cond]));
  });

  const pts = CONDS
    .map((cond, i) => {
      const v = values[cond];
      return v == null ? null : `${x(i)},${y(v)}`;
    })
    .filter(Boolean)
    .join(" ");
  svg.appendChild(mk("polyline", { points: pts, class: "svg-line" }));

  CONDS.forEach((cond, i) => {
    const v = values[cond];
    if (v == null) return;
    svg.appendChild(mk("circle", { cx: x(i), cy: y(v), r: 5, class: "svg-dot" }));
    svg.appendChild(mk("text",
      { x: x(i), y: y(v) - 12, class: "svg-value", "text-anchor": "middle" },
      Number(v).toFixed(2)));
  });
}

// #demo appendix: full condition-means table (all constructs).
function renderAppendixConditionTable() {
  const host = document.getElementById("appxCondTable");
  if (!host) return;
  const rows = [];
  ALL_CONSTRUCTS.forEach((key) => {
    const values = DATA.descriptive_results.condition_means[key] || {};
    CONDS.forEach((condition) => {
      rows.push([
        constructLabel(key),
        `${condition}｜${CONDITION_META[condition].title}`,
        fmt(values[condition]),
        DATA.constructs.native_scales[key],
      ]);
    });
  });
  replaceTable("appxCondTable",
    tableFrom(["构念", "实验条件", "流程演示均值", "原量尺"], rows, [2]));
}

// #demo appendix: contrast tables with raw / adjusted mode toggle.
function renderContrasts() {
  const select = document.getElementById("contrastConstructSelect");
  const modeGroup = document.getElementById("contrastMode");
  const help = document.getElementById("contrastHelp");
  select.innerHTML = "";
  ALL_CONSTRUCTS.forEach((key) => select.appendChild(el("option", { value: key }, constructLabel(key))));
  let mode = "adjusted";

  const build = () => {
    const key = select.value;
    if (mode === "adjusted") {
      help.textContent = "模型调整后差异：在混合效应模型中控制场景、方向等因素后得到的估计差异。Holm校正用于同一构念内的多重比较。";
      const rows = DATA.model_adjusted_results.contrasts
        .filter((row) => row.construct === key)
        .map((row) => [
          row.contrast_id,
          CONTRAST_META[row.contrast_id] || row.contrast,
          colorCell(signed(row.estimate)),
          fmt(row.standard_error, 3),
          fmt(row.p_value_holm, 3),
          row.ci95_low == null ? "—" : `[${fmt(row.ci95_low, 2)}, ${fmt(row.ci95_high, 2)}]`,
        ]);
      replaceTable("contrastTable", tableFrom(["编号", "比较含义", "调整后差异", "标准误", "Holm校正p值", "95%置信区间"], rows, [2, 3, 4]));
    } else {
      help.textContent = "直接均值差：直接比较两个条件在流程演示数据中的平均得分，作为控制场景与方向之前的参照。";
      const rows = DATA.raw_planned_contrasts
        .filter((row) => row.construct === key)
        .map((row) => [
          row.contrast_id,
          CONTRAST_META[row.contrast_id] || row.contrast,
          colorCell(signed(row.difference)),
          fmt(row.effect_size_d, 2),
          row.ci95_low == null ? "—" : `[${fmt(row.ci95_low, 2)}, ${fmt(row.ci95_high, 2)}]`,
          `${row.n_left} / ${row.n_right}`,
        ]);
      replaceTable("contrastTable", tableFrom(["编号", "比较含义", "直接均值差", "效应量d", "95%置信区间", "两侧样本数"], rows, [2, 3]));
    }
  };

  modeGroup.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      modeGroup.querySelectorAll("button").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      mode = button.dataset.mode;
      build();
    });
  });
  select.addEventListener("change", build);
  build();
}

function replaceTable(id, table) {
  table.id = id;
  document.getElementById(id).replaceWith(table);
}

// Neutral direction semantics: sign shows numeric direction only, never value
// judgement. Uses direction-up / direction-down / direction-neutral.
function colorCell(text) {
  const className = text.startsWith("+")
    ? "direction-up"
    : text.startsWith("-")
      ? "direction-down"
      : "direction-neutral";
  return { node: el("span", { class: className }, text) };
}

function renderScenarioHet() {
  const heterogeneity = DATA.quality_summary.scenario_heterogeneity;
  const rows = ALL_CONSTRUCTS.filter((key) => heterogeneity[key]).map((key) => [
    constructLabel(key),
    fmt(heterogeneity[key].scenario_mean_min),
    fmt(heterogeneity[key].scenario_mean_max),
    fmt(heterogeneity[key].scenario_mean_range),
  ]);
  replaceTable("scenHetTable", tableFrom(["构念", "场景最低均值", "场景最高均值", "场景范围"], rows, [1, 2, 3]));
}

// null/empty captured_warnings displays as "无记录", never the literal "null".
function warningText(value) {
  if (value === null || value === undefined || value === "") return "无记录";
  return String(value);
}

// #demo appendix: per-construct model fit + optimizer + captured warnings.
function renderFitSummary() {
  const host = document.getElementById("fitSummaryTable");
  if (!host) return;
  const fit = (DATA.model_adjusted_results && DATA.model_adjusted_results.fit_summary) || [];
  const rows = fit.map((row) => [
    constructLabel(row.construct),
    row.converged ? "是" : "否",
    row.optimizer_used || "—",
    fmt(row.material_random_intercept_variance, 3),
    fmt(row.residual_variance, 3),
    warningText(row.captured_warnings),
  ]);
  replaceTable("fitSummaryTable",
    tableFrom(["构念", "收敛", "使用的优化器", "材料随机截距方差", "残差方差", "记录的警告"],
      rows, [3, 4]));
}

// #status: concentrated status notes.
function renderStatus() {
  const host = document.getElementById("statusNotes");
  if (!host) return;
  host.innerHTML = "";
  STATUS_NOTES.forEach((text) => host.appendChild(el("li", {}, text)));
}

// #status: reproduction and documentation entries. Static links only, so they
// stay available even if the demo JSON fails to load.
const REPO_BASE = "https://github.com/sherlock0717/llm-attribution-behavior-evaluation/";
const REPO_PATH = "tasks/attribution_behavior/evaluations/pa_wu_r1_pilot";

function renderEntries() {
  const host = document.getElementById("entryGrid");
  if (!host) return;
  host.innerHTML = "";
  const tree = REPO_BASE + "tree/main/";
  const blob = REPO_BASE + "blob/main/";
  const links = [
    ["浏览完整材料", "#materials"],
    ["研究B说明", blob + "docs/CURRENT_STUDY_CARD.md"],
    ["测量来源", blob + "docs/CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md"],
    ["研究协议", blob + REPO_PATH + "/study_protocol.yaml"],
    ["分析计划", blob + REPO_PATH + "/analysis_plan.md"],
    ["评分规则", blob + REPO_PATH + "/scoring_spec.yaml"],
    ["输出目录", tree + REPO_PATH + "/outputs/"],
    ["GitHub仓库", REPO_BASE],
  ];
  links.forEach(([label, href]) => {
    const attrs = href.startsWith("#")
      ? { class: "entry-item", href }
      : { class: "entry-item", href, target: "_blank", rel: "noopener" };
    host.appendChild(el("a", attrs, el("strong", {}, label)));
  });
  host.appendChild(el("a", { class: "entry-item entry-back", href: "../" },
    el("strong", {}, "返回项目总览")));
}

function setupImageFallbacks() {
  document.querySelectorAll(".figure img").forEach((image) => {
    image.addEventListener("error", () => {
      image.hidden = true;
      let panel = image.parentElement.querySelector(".image-error");
      if (!panel) {
        panel = el("div", { class: "image-error" },
          el("strong", {}, "图表加载失败"),
          el("p", {}, `未能加载：${image.getAttribute("data-fig") || image.src}`),
          el("button", { type: "button" }, "重新加载")
        );
        panel.querySelector("button").addEventListener("click", () => {
          panel.remove();
          image.hidden = false;
          const source = image.getAttribute("data-fig");
          image.src = `assets/figures/${source}?retry=${Date.now()}`;
        });
        image.parentElement.insertBefore(panel, image);
      }
    });
  });
}

function setupLightbox() {
  const lightbox = document.getElementById("lightbox");
  const largeImage = document.getElementById("lbImg");
  const caption = document.getElementById("lbCap");
  const closeButton = document.getElementById("lbClose");
  const close = () => lightbox.classList.remove("open");

  document.querySelectorAll(".figure img").forEach((image) => {
    image.addEventListener("click", () => {
      largeImage.src = image.src;
      caption.textContent = image.parentElement.querySelector("figcaption")?.textContent || "";
      lightbox.classList.add("open");
      closeButton.focus();
    });
  });
  closeButton.addEventListener("click", close);
  lightbox.addEventListener("click", (event) => { if (event.target === lightbox) close(); });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") close(); });
}

function showLoadError(error) {
  // 1. Hero status stays plain-language; the technical error is not shown here.
  const status = document.getElementById("loadStatus");
  status.className = "load-status error";
  status.textContent = "流程演示数据暂时未载入，研究设计和分析计划仍可浏览。";

  // 2. Snapshot status reflects the pending data.
  const snapshot = document.getElementById("snapshotStatus");
  if (snapshot) snapshot.textContent = "页面数据待恢复";

  // 3. Dynamic demo content is hidden; a clear error panel takes its place.
  const content = document.getElementById("demoContent");
  if (content) content.hidden = true;
  enableBrowserControls(false);

  const panel = document.getElementById("demoError");
  if (panel) {
    panel.hidden = false;
    panel.innerHTML = "";
    panel.appendChild(el("strong", {}, "流程演示数据未能载入"));
    panel.appendChild(el("p", {}, "数据文件：data/showcase_data.json"));
    const details = el("details", {},
      el("summary", {}, "查看技术错误"),
      el("p", { class: "tech-error" }, String(error)));
    panel.appendChild(details);
    const button = el("button", { type: "button" }, "重新加载");
    button.addEventListener("click", () => load().catch(showLoadError));
    panel.appendChild(button);
  }
}

load().catch(showLoadError);
