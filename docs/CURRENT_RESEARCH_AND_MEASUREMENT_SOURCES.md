# 研究B的研究与测量来源

本文件描述研究B“机器主体决策过程归因评测”的构念与测量来源。研究B属于“LLM行动者归因评测”研究计划；内容严格基于仓库现有机器主体评测资产，不复制受版权保护的题项原文，也不新增最终中文题项翻译。

## 使用原则

- R1 固定为机器主体；
- Wu & Shen 题项保持机器专属原文；
- 不把机器题项改写为人类版本；
- 各构念使用自身原量尺；
- 六个构念不合并为总分；
- 自由意志只为 MSI 探索性单项。

## 主要构念与来源

各构念的来源、角色、原量尺与证据路径如下（依据 `scoring_spec.yaml` 与 P0 资产）：

| 构念 | 来源 | 来源构念 | 原量尺 | 角色 | 证据路径 |
|---|---|---|---|---|---|
| IN（知觉独立性） | Wu & Shen 2026 | perceived_machine_independence | 1–7 | 主要构念 | `tasks/attribution_behavior/measurement_candidates/pa_wu_p0/items_wu_shen_2026.yaml` |
| GO（目标导向性） | Wu & Shen 2026 | perceived_machine_goal_orientation | 1–7 | 主要构念 | `tasks/attribution_behavior/measurement_candidates/pa_wu_p0/items_wu_shen_2026.yaml` |
| MSI（心理状态推断） | Wu & Shen 2026 | mental_state_inference | 1–5（语义差异） | 主要构念 | `tasks/attribution_behavior/measurement_candidates/pa_wu_p0/items_wu_shen_2026.yaml` |
| IC（影响能力） | Wu & Shen 2026 | influential_capacity_judgment | 1–7 | 主要构念 | `tasks/attribution_behavior/measurement_candidates/pa_wu_p0/items_wu_shen_2026.yaml` |
| PA5（感知能动性 5 题） | PA 2024 | perceived agency (pa5) | 1–5 | 补充构念 | `tasks/attribution_behavior/measurement_candidates/pa_wu_p0/items_pa_2024.yaml` |
| PA8（感知能动性 8 题） | PA 2024 | perceived agency (pa8) | 1–5 | 补充构念 | `tasks/attribution_behavior/measurement_candidates/pa_wu_p0/items_pa_2024.yaml` |

说明：

- 主要构念 IN、GO、MSI、IC 来自 Wu & Shen 2026 的机器专属题项；
- 补充构念 PA5、PA8 来自 PA 2024 的感知能动性题项；
- MSI 中的自由意志题项（`wu_ms3`）在 `scoring_spec.yaml` 中标记为探索性单项（`free_will_items_exploratory: [wu_ms3]`），不作为独立构念，也不生成总分；
- 各构念按 `scoring_spec.yaml` 的 `method: mean` 在自身原量尺上计算，`no_cross_scale_total: true` 禁止跨量尺总分。

## 题项处理边界

- **哪些保持原文**：Wu & Shen 2026 与 PA 2024 的题项由 `scoring_spec.yaml` 顶部注释声明「REFERENCES the P0 item files verbatim; it does NOT rewrite」——即逐字引用 P0 文件，不改写；
- **哪些是补充资产**：PA5 / PA8 属于 PA 2024 的补充感知能动性指标；
- **中文题项状态**：当前评分链未新增最终中文题项翻译；施测使用英文刺激材料与英文题项，评判模型接收英文原始材料；
- **后续验证计划**：内容效度、构念效度与跨主体测量可比性列入后续验证；机器主体测量与人类主体测量之间的可比性将在独立人类题项建成后另行检验。

## 完整文献与许可状态

本节严格依据 `tasks/attribution_behavior/measurement_candidates/pa_wu_p0/manifest.yaml` 与同目录 `README.md`，如实记录两套来源工具的文献与许可边界，不作超出源文件的概括。

### PA 2024（Trafton et al., 2024）

- 完整引用：Trafton, J. G., McCurry, J. M., Zish, K., & Frazier, C. R. (2024). The Perception of Agency. *ACM Transactions on Human-Robot Interaction, 13*(1), 1–23. DOI: `10.1145/3640011`。
- 许可分三项事实**分开记录**，不收敛为单一标签：
  - 正式 ACM 论文及其中发表的 **PA13 题项文本**为 **CC BY 4.0**（`pa_2024_article_and_pa13_item_text: CC BY 4.0`）；
  - 本目录使用的 **PA13 / PA8 / PA5 版本成员归属**取自作者公开页面（`pa8_pa5_membership_source: author_public_page`，gregtrafton.com/agency）；
  - 该作者页面**本身未单独声明网页内容许可**（`author_page_separate_license_statement: not_stated`）。
- PA8、PA5 是 **PA13 的官方子集/子分数**：PA8=8 项、PA5=5 项，成员逐条取自作者公开页面版本归属表（2026-07-22 核验），未自行推断或缩减。
- R1 使用的是这些官方成员集合上的**派生子分数**（各版本成员均值），属综合表单上下文中的子分数，**不等同于独立短表施测**。

### Wu & Shen 2026

- 完整引用：Wu, Y., & Shen, F. (2026). Machine agency attribution in human–AI interaction. *Journal of Computer-Mediated Communication, 31*(3), zmag009. DOI: `10.1093/jcmc/zmag009`。
- 许可：**CC BY 4.0**（`license: CC BY 4.0`）。
- 逐字题项取自 OUP 正式 Table 1（最终 19 项），含四构念（IN/GO/MSI/IC）映射；MSI 为 5 点语义差异量表。

### 许可边界小结

- 三项 PA 许可事实分开记录，避免把整套工具错误概括为单一许可标签；
- Wu & Shen 2026 为统一的 CC BY 4.0；
- PA5 / PA8 为 PA13 的官方子分数，R1 采用其派生分数，不构成独立验证短表，也未声称其独立信效度。

## 仓库证据入口

以下为经确认存在的真实路径：

- R1 研究协议：`tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/study_protocol.yaml`
- R1 评分规则：`tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/scoring_spec.yaml`
- R1 分析计划：`tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/analysis_plan.md`
- R1 身份范围决策：`tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/identity_scope_decision.md`
- P0 题项资产目录：`tasks/attribution_behavior/measurement_candidates/pa_wu_p0/`
  - `items_wu_shen_2026.yaml`、`items_pa_2024.yaml`、`forms.yaml`、`scoring.yaml`、`manifest.yaml`、`README.md`

研究B说明见 [`CURRENT_STUDY_CARD.md`](CURRENT_STUDY_CARD.md)。研究A的来源见 [`research_and_measurement_sources.md`](research_and_measurement_sources.md)；两项研究的数据与结论不混合。
