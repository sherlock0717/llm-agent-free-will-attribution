# 研究B离线协议内部Agent多视角审查

本文件记录的是内部Agent多视角审查。它不是专家审查，不构成内容效度验证、构念效度验证、测量等值性结论或真实模型表现验证。审查基于已冻结的离线资产与脚本静态检查。

审查对象：`research_packages/study_b/` 离线研究包、导入脚本与研究B公开页面（源提交 9cb4aae1）。

## 视角一：研究设计一致性

- `material_matrix.csv` 96 行，`material_id` 唯一，覆盖 6 条件 × 8 场景 × 2 方向 × 1 机器身份。
- `condition_id` C0—C5 与 `condition_matrix.csv` 的 D/U 组合一致（C0=D0-U0 直接决定 … C5=D2-U3 反馈后改变）。
- 材料矩阵的 `decision_information_level`、`feedback_state`、`second_decision_state` 与条件定义对应。
- P1—P6 与条件定义一致：P1=C1−C0、P2=C2−C0、P3=C3−C2、P4=C4−C2、P5=C5−C2、P6=C5−C4，与 `analysis_plan.md` 一致。
- 结论：材料字段与条件、场景、方向、比较定义在离线包内保持一致。

## 视角二：数据契约与可复现性

- `build_study_b_protocol_package.py --check` 在相同仓库状态下重复生成一致，`--check` 不修改跟踪文件。
- `asset_hashes.json` 覆盖 96 条材料的规范化内容、题项文件、评分规范、分析计划、示例数据与关键脚本。
- `scoring_matrix_template.csv` 192 行，每条材料对应 `judge_1` 与 `judge_2` 两个槽位。
- `external_result_schema.json` 要求覆盖全部 28 个必需题项，数值落在各自原量尺范围，并拒绝缺失题项、未知题项、越界值、重复键、NaN 与 Infinity。
- 结论：离线数据契约足以在导入前阻止缺失与越界值；确定性演示链可重复生成。

## 视角三：公开叙事可理解性

- 四个主要评价维度（IN/GO/MSI/IC）与题项映射一致；PA5、PA8 保持补充评分位置，未升级为主要维度。
- 研究B页面说明当前研究范围覆盖材料、测量、分析计划、确定性示例与离线结果导入。
- README、研究计划、研究B说明与页面使用同一表述。
- 结论：公开层可读地表达当前研究范围。

## 视角四：误用与误读风险

- 模型 ID 在 `protocol_manifest.yaml` 标记 `protocol_metadata_only: true`，在 Schema 中标注仅为协议元数据，脚本不据此发起调用。
- 离线演示链输出统一标记 `data_role = analysis_interface_example` 与 `generation_method = deterministic_fixture`，不使用 `synthetic_model_response`、`simulated_real_model`、`proxy_model_score`、`estimated_model_output` 或 `formal_result`。
- `external_result_example.jsonl` 标记为 schema 示例，使用固定规则数值，不进入公开研究结果，不覆盖分析界面示例数据。
- 页面不再承诺正式模型 API 评分。
- 结论：示例数据被误读为正式结果的风险由标签与文案降低；仍需在正式结果产生后再更新研究结论。

## 遗留事项

- 正式研究结论需在外部离线评分文件通过验证并进入同一分析流程后才能报告。
- 跨主体（机器/人类）测量等值性未作任何声明，需独立测量与后续研究。
