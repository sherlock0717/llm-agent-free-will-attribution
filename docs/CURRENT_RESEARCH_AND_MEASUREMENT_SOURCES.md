# 当前研究与测量来源：PA—Wu R1

本文件描述当前主研究 PA—Wu R1 的构念与测量来源。内容严格基于仓库现有 R1 资产，不复制受版权保护的题项原文，也不新增最终中文题项翻译。

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
| IN（知觉独立性） | Wu & Shen 2026 | perceived_machine_independence | 1–7 | 主要构念 | `pa_wu_p0/items_wu_shen_2026.yaml` |
| GO（目标导向性） | Wu & Shen 2026 | perceived_machine_goal_orientation | 1–7 | 主要构念 | `pa_wu_p0/items_wu_shen_2026.yaml` |
| MSI（心理状态推断） | Wu & Shen 2026 | mental_state_inference | 1–5（语义差异） | 主要构念 | `pa_wu_p0/items_wu_shen_2026.yaml` |
| IC（影响能力） | Wu & Shen 2026 | influential_capacity_judgment | 1–7 | 主要构念 | `pa_wu_p0/items_wu_shen_2026.yaml` |
| PA5（感知能动性 5 题） | PA 2024 | perceived agency (pa5) | 1–5 | 补充构念 | `pa_wu_p0/items_pa_2024.yaml` |
| PA8（感知能动性 8 题） | PA 2024 | perceived agency (pa8) | 1–5 | 补充构念 | `pa_wu_p0/items_pa_2024.yaml` |

说明：

- 主要构念 IN、GO、MSI、IC 来自 Wu & Shen 2026 的机器专属题项；
- 补充构念 PA5、PA8 来自 PA 2024 的感知能动性题项；
- MSI 中的自由意志题项（`wu_ms3`）在 `scoring_spec.yaml` 中标记为探索性单项（`free_will_items_exploratory: [wu_ms3]`），不作为独立构念，也不生成总分；
- 各构念按 `scoring_spec.yaml` 的 `method: mean` 在自身原量尺上计算，`no_cross_scale_total: true` 禁止跨量尺总分。

## 题项处理边界

- **哪些保持原文**：Wu & Shen 2026 与 PA 2024 的题项由 `scoring_spec.yaml` 顶部注释声明「REFERENCES the P0 item files verbatim; it does NOT rewrite」——即逐字引用 P0 文件，不改写；
- **哪些是补充资产**：PA5 / PA8 属于 PA 2024 的补充感知能动性指标；
- **哪些未进行翻译**：本文件与评分链均未新增最终中文题项翻译，评判模型接收的是英文原始材料；
- **未声称内容效度**：当前内部流程未确认内容效度；
- **未声称构念效度**：当前内部流程未确认构念效度；
- **未声称机器与人类测量等值**：R1 仅机器主体，不声称与人类测量等值。

## 仓库证据入口

以下为经确认存在的真实路径：

- R1 研究协议：`tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/study_protocol.yaml`
- R1 评分规则：`tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/scoring_spec.yaml`
- R1 分析计划：`tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/analysis_plan.md`
- R1 身份范围决策：`tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/identity_scope_decision.md`
- P0 题项资产目录：`tasks/attribution_behavior/measurement_candidates/pa_wu_p0/`
  - `items_wu_shen_2026.yaml`、`items_pa_2024.yaml`、`forms.yaml`、`scoring.yaml`、`manifest.yaml`、`README.md`

当前研究说明见 [`CURRENT_STUDY_CARD.md`](CURRENT_STUDY_CARD.md)。早期探索性研究路线的来源见 [`research_and_measurement_sources.md`](research_and_measurement_sources.md)（早期归档）。
