// PA—Wu R1 Pilot 中文展示页。读取 data/showcase_data.json（合成演示数据）。
"use strict";

const CONDS = ["C0", "C1", "C2", "C3", "C4", "C5"];
const ALL_CONSTRUCTS = ["IN", "GO", "MSI", "IC", "PA5", "PA8"];

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
    description: "评判模型是否向机器主体归因意识、思考、意图等心理状态。自由意志只是其中一个探索性题项。",
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
    question: "仅增加备选方案信息后，归因评分是否变化。",
    allow: "评判模型是否对“存在可选方案”这一文本线索敏感。",
    forbid: "机器主体真实拥有选择自由。",
  },
  {
    id: "P2", diff: "C2−C1", name: "加入明确理由",
    question: "在已有备选方案的基础上，增加理由说明是否改变评分。",
    allow: "评判模型是否对理由表达敏感。",
    forbid: "机器主体真实进行了人类式理性推理。",
  },
  {
    id: "P3", diff: "C3−C2", name: "加入反馈信息",
    question: "在已有决定和理由的基础上，仅增加反馈是否改变评分。",
    allow: "评判模型是否对“主体收到反馈”这一线索敏感。",
    forbid: "机器主体真实具有反思或学习能力。",
  },
  {
    id: "P4", diff: "C4−C3", name: "反馈后维持决定",
    question: "反馈后明确维持原决定是否改变评分。",
    allow: "评判模型如何响应决定一致性或坚持行为。",
    forbid: "维持决定必然代表更强能动性或更优决策。",
  },
  {
    id: "P5", diff: "C5−C3", name: "反馈后改变决定",
    question: "反馈后改变原决定是否改变评分。",
    allow: "评判模型如何响应行为修正线索。",
    forbid: "改变决定必然代表更强反思能力。",
  },
  {
    id: "P6", diff: "C5−C4", name: "改变与维持的比较",
    question: "同样收到反馈后，改变决定与维持决定的评分是否不同。",
    allow: "评判模型对两类后续行为的相对敏感性。",
    forbid: "任一行为在规范意义上更正确或更自主。",
  },
];

const CONDITION_META = {
  C0: { title: "直接作出决定", description: "只呈现最终决定，不展示备选方案、理由或反馈。" },
  C1: { title: "呈现备选方案后决定", description: "展示两种可选方案，再呈现最终决定。" },
  C2: { title: "决定并说明理由", description: "呈现最终决定及其明确理由。" },
  C3: { title: "说明理由并收到反馈", description: "在决定和理由之后增加外部反馈，但不呈现第二次决定。" },
  C4: { title: "收到反馈后维持决定", description: "呈现反馈，并明确机器主体再次决定维持原选择。" },
  C5: { title: "收到反馈后改变决定", description: "呈现反馈，并明确机器主体再次决定改选另一方案。" },
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

const BOUNDARY_TRANSLATIONS = [
  "R1只研究机器主体，不进行AI与人类主体比较。",
  "当前采用六水平条件因子，不把结果解释为完整D×U因果交互。",
  "各构念按原量尺推断；0—1标准化仅可用于展示。",
  "不进行缺失值插补；构念得分要求相关题项均有效。",
  "自由意志题项仅作为MSI中的探索性单项，不构成独立总分。",
  "不进行模型排名；两个评判模型的差异只作描述性展示。",
];

const REPLACEMENT_TRANSLATIONS = [
  "完成并通过双模型真实运行的授权与前置检查。",
  "让两个模型对同一套96条机器主体材料完成真实评分。",
  "将真实响应写入独立运行目录，不覆盖当前合成演示数据。",
  "沿用既有评分、描述统计、混合效应模型和报告生成流程。",
  "在每个构念内报告经Holm校正的P1—P6预设对比。",
  "只有真实结果完成核验后，才可移除合成演示数据提示。",
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

async function load() {
  setLoadStatus("正在加载合成演示数据……", "loading");
  const response = await fetch("data/showcase_data.json", { cache: "no-store" });
  if (!response.ok) throw new Error(`数据请求失败：HTTP ${response.status}`);
  DATA = await response.json();
  render();
  setLoadStatus("合成演示数据已加载。可使用下拉框和结果切换按钮查看不同内容。", "success");
}

function render() {
  renderQuestion();
  renderConstructs();
  renderConditions();
  renderCoverage();
  renderScenarioBrowser();
  renderJudges();
  renderConstructView();      // #s7: selector drives title + explain + scale + SVG + table
  renderContrastCards();      // #s8: reader-facing P1—P6 comparison logic
  renderContrasts();          // #s8 appendix: synthetic stats tables
  renderAppendixConditionTable();
  renderJudgeConfig();        // #s9: model configuration + comparison plan (no ranking)
  renderScenarioHet();
  renderMaterialExamples();
  renderBoundaries();
  renderReplacement();
  renderGithub();
  setupImageFallbacks();
  setupLightbox();
}

function renderQuestion() {
  document.getElementById("researchQuestion").textContent =
    "本评测考察：当机器主体的材料中依次加入备选方案、理由、反馈以及第二次决定时，大语言模型对其知觉独立性、目标导向性、心理状态、影响能力与感知能动性的评分是否发生变化。";
  document.getElementById("freeWillRole").textContent =
    "自由意志只对应心理状态推断（MSI）中的一个探索性题项，不作为唯一核心构念，也不生成跨量尺总分。";
  document.getElementById("identityScope").textContent =
    "当前R1固定为机器主体。页面不生成或解释AI与人类主体之间的比较。";
}

function renderConstructs() {
  const host = document.getElementById("constructCards");
  host.innerHTML = "";
  const primary = new Set(DATA.constructs.primary);
  ALL_CONSTRUCTS.forEach((key) => {
    const meta = CONSTRUCT_META[key];
    host.appendChild(el("article", { class: "card construct-card" },
      el("div", { class: "card-title-row" },
        el("h3", {}, `${meta.name}（${key}）`),
        el("span", { class: `badge ${primary.has(key) ? "primary" : "supplementary"}` }, primary.has(key) ? "主要构念" : "补充构念")
      ),
      el("p", {}, meta.description),
      el("p", { class: "small" }, `原量尺：${DATA.constructs.native_scales[key]}`),
      key === "MSI" ? el("p", { class: "small warn-text" }, "包含一个自由意志探索性题项。") : null
    ));
  });
}

function renderConditions() {
  const host = document.getElementById("conditionCards");
  host.innerHTML = "";
  CONDS.forEach((key) => {
    const meta = CONDITION_META[key];
    host.appendChild(el("article", { class: "card condition-card" },
      el("div", { class: "card-title-row" },
        el("span", { class: "cond-pill" }, key),
        el("h3", {}, meta.title)
      ),
      el("p", {}, meta.description)
    ));
  });
}

function renderCoverage() {
  const metrics = document.getElementById("coverageMetrics");
  metrics.innerHTML = "";
  const q = DATA.quality_summary;
  [
    ["实验条件", "6"],
    ["场景", "8"],
    ["决策方向", "2"],
    ["材料总数", String(q.n_materials)],
    ["合成评分响应", String(q.n_responses)],
    ["有效构念得分率", `${fmt(q.construct_scored_rate * 100, 0)}%`],
  ].forEach(([label, value]) => {
    metrics.appendChild(el("div", { class: "metric-card" },
      el("strong", {}, value),
      el("span", {}, label)
    ));
  });

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
  balance.appendChild(el("h3", {}, "平衡性检查"));
  const rows = [
    ["每个条件", `${Object.values(DATA.material_balance.per_condition)[0]}条`],
    ["每个场景", `${Object.values(DATA.material_balance.per_scenario)[0]}条`],
    ["方向A", `${DATA.material_balance.per_direction.A}条`],
    ["方向B", `${DATA.material_balance.per_direction.B}条`],
    ["目标主体", "仅机器主体"],
  ];
  rows.forEach(([label, value]) => balance.appendChild(el("div", { class: "balance-row" },
    el("span", {}, label), el("strong", {}, value)
  )));
  balance.appendChild(el("p", { class: "small muted" }, "所有条件、场景和方向均完整覆盖，没有缺格。"));
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
  const scenarioName = SCENARIO_META[scenarioId] || SCENARIO_META[material.material_id.split("__")[1]] || "材料示例";
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
      el("p", { class: "source-note" }, "以下英文为评判模型实际接收的源材料，不是中文翻译版本。"),
      el("div", { class: "source-text" }, sourceText),
      el("div", { class: "bridge" }, "题项指称说明：后续量表中的“the machine”均指上述AI系统。")
    ),
    el("div", { class: "material-id" }, `材料ID：${material.material_id}`)
  );
}

function renderJudges() {
  const host = document.getElementById("judgeCards");
  host.innerHTML = "";
  DATA.judge_models.forEach((model) => {
    host.appendChild(el("article", { class: "card" },
      el("h3", {}, model.id),
      el("p", {}, `提供方：${model.provider}`),
      el("p", { class: "small" }, "角色：共同主要评判模型（配置已确定）；后续完整运行时将对同一套96条材料独立评分。"),
      el("p", { class: "small warn-text" }, "当前展示为合成流程演示数据，不代表该模型的实际评分行为，实证表现未评估。")
    ));
  });
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

// #s7 selector: one handler synchronises title, explanation, native-scale label,
// the single-construct SVG chart and the condition-means table together.
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
      `纵轴按当前构念原量尺 ${scaleText} 显示；1—5 与 1—7 构念不共用同一坐标轴。`;
    renderConditionProfile(key);
    const values = DATA.descriptive_results.condition_means[key] || {};
    const rows = CONDS.map((condition) => [
      condition,
      CONDITION_META[condition].title,
      fmt(values[condition]),
      scaleText,
      "合成流程演示",
    ]);
    replaceTable("condResultTable",
      tableFrom(["条件ID", "条件名称", "合成均值", "原量尺", "数据状态"], rows, [2]));
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

  // viewBox coordinate space; width is fluid via CSS, height fixed by ratio.
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
    `${meta.name}（${key}）在C0至C5六个条件下的合成平均得分，原量尺 ${minScale}—${maxScale}`);
  while (svg.firstChild) svg.removeChild(svg.firstChild);

  const mk = (tag, attrs = {}, text = null) => {
    const node = document.createElementNS(NS, tag);
    Object.entries(attrs).forEach(([k, v]) => node.setAttribute(k, v));
    if (text != null) node.textContent = text;
    return node;
  };

  // Title inside the SVG (changes with construct).
  svg.appendChild(mk("text",
    { x: padL, y: 24, class: "svg-title" },
    `${meta.name}（${key}）｜原量尺 ${minScale}—${maxScale}`));

  const x = (i) => padL + (plotW * i) / (CONDS.length - 1);
  const y = (v) => padT + plotH - (plotH * (v - minScale)) / (maxScale - minScale);

  // Axis frame + a few horizontal gridlines with scale ticks.
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

  // X labels (short) C0—C5.
  CONDS.forEach((cond, i) => {
    svg.appendChild(mk("text",
      { x: x(i), y: H - padB + 20, class: "svg-xlabel", "text-anchor": "middle" }, cond));
    svg.appendChild(mk("text",
      { x: x(i), y: H - padB + 38, class: "svg-xsub", "text-anchor": "middle" },
      CONDITION_SHORT[cond]));
  });

  // Connecting polyline + points with value labels.
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

// #s8 appendix: full condition-means table (all constructs, raw synthetic values).
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
    tableFrom(["构念", "实验条件", "合成均值", "原量尺"], rows, [2]));
}

// #s8 main area: six reader-facing contrast cards (no statistics).
function renderContrastCards() {
  const host = document.getElementById("contrastCards");
  if (!host) return;
  host.innerHTML = "";
  CONTRAST_CARDS.forEach((card) => {
    host.appendChild(el("article", { class: "card contrast-card" },
      el("div", { class: "card-title-row" },
        el("span", { class: "cond-pill" }, card.id),
        el("h3", {}, card.name)
      ),
      el("p", { class: "small muted" }, `条件差：${card.diff}`),
      el("p", {}, el("strong", {}, "研究问题："), card.question),
      el("p", { class: "allow-line" }, el("strong", {}, "允许解释："), card.allow),
      el("p", { class: "forbid-line" }, el("strong", {}, "禁止解释："), card.forbid)
    ));
  });
}

// #s9: two neutral model-configuration cards + comparison plan (no ranking).
function renderJudgeConfig() {
  const host = document.getElementById("judgeConfigCards");
  if (!host) return;
  host.innerHTML = "";
  DATA.judge_models.forEach((model) => {
    host.appendChild(el("article", { class: "card judge-config-card" },
      el("h3", {}, model.id),
      el("dl", { class: "config-list" },
        el("div", {}, el("dt", {}, "角色"), el("dd", {}, "共同主要评判模型")),
        el("div", {}, el("dt", {}, "供应方类别"), el("dd", {}, model.provider)),
        el("div", {}, el("dt", {}, "当前状态"), el("dd", {}, "配置已确定")),
        el("div", {}, el("dt", {}, "实证表现"), el("dd", { class: "status-neutral" }, "未评估"))
      )
    ));
  });
}

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
      help.textContent = "直接均值差：不进行模型调整，直接比较两个条件在合成数据中的平均得分。该模式更直观，但没有控制场景与方向。";
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

function renderMaterialExamples() {
  const host = document.getElementById("materialExamples");
  host.innerHTML = "";
  const scenarioId = DATA.scenarios[0];
  const materials = DATA.scenario_materials[scenarioId] || [];
  CONDS.forEach((condition) => {
    const material = materials.find((item) => item.condition_id === condition && item.direction_version === "A");
    if (material) host.appendChild(renderStim(material, scenarioId));
  });
}

function renderBoundaries() {
  const host = document.getElementById("boundaryList");
  host.innerHTML = "";
  BOUNDARY_TRANSLATIONS.forEach((text) => host.appendChild(el("li", {}, text)));
}

function renderReplacement() {
  const host = document.getElementById("replacementList");
  host.innerHTML = "";
  REPLACEMENT_TRANSLATIONS.forEach((text) => host.appendChild(el("li", {}, text)));
}

function renderGithub() {
  const entry = DATA.github_entry;
  const host = document.getElementById("githubCard");
  host.innerHTML = "";
  const base = "https://github.com/sherlock0717/llm-attribution-behavior-evaluation/tree/main/";
  host.appendChild(el("p", {}, "评测目录：", el("a", { href: base + entry.repo_path, target: "_blank", rel: "noopener" }, entry.repo_path)));
  host.appendChild(el("p", {}, "输出目录：", el("a", { href: base + entry.repo_path + "/" + entry.outputs, target: "_blank", rel: "noopener" }, entry.outputs)));
  host.appendChild(el("p", {}, "演示报告：", el("a", { href: base + entry.repo_path + "/" + entry.report, target: "_blank", rel: "noopener" }, entry.report)));
  host.appendChild(el("p", { class: "small muted" }, "真实授权运行应写入独立运行目录，并保留当前合成演示版本，不直接覆盖。"));
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
  const status = document.getElementById("loadStatus");
  status.className = "load-status error";
  status.innerHTML = "";
  status.appendChild(el("strong", {}, "数据加载失败。"));
  status.appendChild(document.createTextNode(` ${String(error)}`));
  const button = el("button", { type: "button" }, "重新加载");
  button.addEventListener("click", () => load().catch(showLoadError));
  status.appendChild(button);
}

load().catch(showLoadError);
