# 研究B离线研究包数据字典

## material_matrix.csv（96 行）

| 字段 | 含义 |
|---|---|
| `material_id` | 材料唯一键，形如 `C0__s1_scheduling__A__machine`（条件__场景__方向__身份） |
| `condition_id` | 条件 C0—C5 |
| `scenario_id` | 八个场景之一（`s1_scheduling` … `s8_energy_plan`） |
| `direction_version` | 方向 A / B |
| `decision_information_level` | 决定信息层级：`direct_decision` / `shows_alternatives` / `shows_reasons` |
| `feedback_state` | 反馈状态：`none` / `given` |
| `second_decision_state` | 反馈后行动：`none` / `keep` / `change` |
| `source_path` | 材料源文件路径 |
| `content_sha256` | 该材料规范化内容（键排序 JSON）的 SHA-256 |

条件与决策过程的对应关系取自 `condition_matrix.csv`：C0=直接决定；C1=展示备选方案；C2=给出理由；C3=理由+反馈；C4=理由+反馈+维持；C5=理由+反馈+改变。

## scoring_matrix_template.csv（192 行）

每条材料对应两个评判槽位（`judge_1`、`judge_2`），共 96 × 2 = 192 行。该文件只定义未来离线结果应具备的行结构，不含真实评分。

| 字段 | 默认值 | 含义 |
|---|---|---|
| `record_id` | `<material_id>__<judge_slot>` | 行唯一键 |
| `material_id` | — | 对应材料 |
| `judge_slot` | `judge_1` / `judge_2` | 评判槽位 |
| `judge_model_id` | `deepseek-v4-pro` / `gpt-5.6-terra` | 协议元数据，不据此调用 |
| `response_source` | `external_offline_file` | 结果来源类型 |
| `response_file` | 空 | 外部结果文件（导入后填写） |
| `imported_at` | 空 | 导入时间（导入后填写） |
| `validation_status` | `awaiting_input` | 验证状态 |
| `parse_status` | `not_started` | 解析状态 |
| `item_score_status` | `not_started` | 题项评分状态 |
| `notes` | 空 | 备注 |

## external_result_schema.json 记录字段

| 字段 | 含义 |
|---|---|
| `material_id` | 必须存在于 `material_matrix.csv` |
| `judge_slot` | `judge_1` / `judge_2` |
| `judge_model_id` | `deepseek-v4-pro` / `gpt-5.6-terra` |
| `item_responses` | 覆盖全部必需题项，数值落在各自原量尺范围 |
| `source_record_id` | 外部记录标识 |
| `source_file_hash` | 源文件 SHA-256 |

题项与原量尺：IN/GO/IC 为 likert_7（1–7），MSI 为 semantic_differential_5（1–5），PA5/PA8 为 likert_5（1–5）。全部 27 个必需题项覆盖四个主要维度与两个补充指标（PA5 的题项是 PA8 的子集，合并去重后共 27 个），取自 `scoring_spec.yaml` 与 P0 题项文件，未在此改写。
