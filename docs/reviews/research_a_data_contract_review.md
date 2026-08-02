# 研究A数据契约核对

本文件在稳健性分析前核对研究A的真实数据源与数量，确认与现有文档一致。核对为只读，不修改任何源文件。

## 1. 原始文件路径
- `outputs/scale_scores.csv`

## 2. 聚合文件路径
- 生成脚本：`scripts/build_research_a_scenario_results.py`
- 公开聚合：`site/data/research_a_scenario_summary.json`
- 稳健性聚合（本轮新增，离线派生）：`site/data/research_a_robustness_summary.json`

## 3. 原始记录数
- 360 条（`participant_id` 唯一）。

## 4. 聚合单元数
- 96 个 = 场景(8) × 身份(2) × 过程条件(6)。

## 5. 每个设计格样本数范围
- 每个 `scenario_id × identity_label × process_condition` 单元包含 30 条响应中的按场景切分部分；
  按 (identity × process_condition) 计每格 30 条，按 96 单元计每单元来自对应场景的响应。
- 平衡性：每个 (identity, process_condition) 单元格计数一致（脚本 `build_units` 校验网格完整，缺格即报错）。

## 6. 缺失字段
- 分析所需字段（`scenario_id`、`identity_label`、`process_condition`、`char_len` 及五个公开构念）均存在。
- 说明：研究A使用 `participant_id` 作为行标识，没有 `material_id`（研究B才有 `material_id`）。

## 7. 重复键
- `participant_id` 唯一，无重复。

## 8. 非有限值
- 五个公开构念在聚合后无 NaN / Infinity；输出 JSON 经 `public_json` 严格序列化。

## 9. 构念名称与原量尺
- 公开构念（1–7 原量尺）：
  - `subjective_process_completeness` 主观过程完整性
  - `agency` 能动性
  - `free_will_attribution` 自由意志归因
  - `perceived_intelligence` 感知智能
  - `responsibility_total` 责任归因总分（结果责任、道德褒贬、过程可归责的合成分）

## 10. 固定对比定义（left − right）
| id | 左条件 | 右条件 | 含义 |
|---|---|---|---|
| A1 | alternatives | direct_choice | 候选方案线索 |
| A2 | reasons_concise | direct_choice_long | 短理由结构与长背景文本 |
| A3 | reflection_feedback | reasons | 反思反馈相对完整理由 |
| A4 | reflection_feedback | direct_choice_long | 高结构过程与长文本直接选择 |

## 核对结论
- 360 条原始记录、96 个聚合单元、5 个公开构念、A1–A4 固定对比，均与 `scripts/build_research_a_scenario_results.py` 与 `site/data/research_a_scenario_summary.json` 一致。
- 数量一致，可进行稳健性分析。分析未修改任何源文件。
