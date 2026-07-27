// PA—Wu R1 Pilot 中文展示页。读取 data/showcase_data.json（合成演示数据）。
"use strict";

const CONDS = ["C0", "C1", "C2", "C3", "C4", "C5"];
const ALL_CONSTRUCTS = ["IN", "GO", "MSI", "IC", "PA5", "PA8"];

const CONSTRUCT_META = {
  IN: { name: "知觉独立性", description: "判断机器主体是否被视为具有相对独立的知觉与判断。" },
  GO: { name: "目标导向性", description: "判断机器主体的行为是否被视为围绕目标组织。" },
  MSI: { name: "心理状态推断", description: "判断评判模型是否倾向于使用意图、信念等心理状态描述机器主体。" },
  IC: { name: "影响能力", description: "判断机器主体是否被视为能够对人或环境产生影响。" },
  PA5: { name: "感知能动性（5题版）", description: "PA 2024 的5题补充指标。" },
  PA8: { name: "感知能动性（8题版）", description: "PA 2024 的8题补充指标。" },
};

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
  renderConditionResults();
  renderContrasts();
  renderJudgeDiff();
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

function renderConditionResults() {
  const select = document.getElementById("resConstructSelect");
  select.innerHTML = "";
  ALL_CONSTRUCTS.forEach((key) => select.appendChild(el("option", { value: key }, constructLabel(key))));
  const rebuild = () => {
    const key = select.value;
    const values = DATA.descriptive_results.condition_means[key] || {};
    const rows = CONDS.map((condition) => [
      `${condition}｜${CONDITION_META[condition].title}`,
      fmt(values[condition]),
      DATA.constructs.native_scales[key],
    ]);
    replaceTable("condResultTable", tableFrom(["实验条件", "合成平均得分", "原量尺"], rows, [1]));
  };
  select.addEventListener("change", rebuild);
  rebuild();
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

function colorCell(text) {
  const className = text.startsWith("+") ? "pos" : text.startsWith("-") ? "neg" : "";
  return { node: el("span", { class: className }, text) };
}

function renderJudgeDiff() {
  const means = DATA.descriptive_results.model_means;
  const modelIds = DATA.judge_models.map((model) => model.id);
  const rows = ALL_CONSTRUCTS.map((key) => [
    constructLabel(key),
    fmt((means[key] || {})[modelIds[0]]),
    fmt((means[key] || {})[modelIds[1]]),
  ]);
  replaceTable("judgeDiffTable", tableFrom(["构念", modelIds[0], modelIds[1]], rows, [1, 2]));
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
