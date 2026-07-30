# 研究B离线研究包

本目录冻结研究B（机器主体决策过程归因）的离线研究协议。它把研究问题、材料、评价维度、评分规则、预设比较和分析计划整理为一组确定性、不依赖网络的资产，并定义外部离线评分结果的导入契约。

本包的可执行范围止于本地验证、结果导入和离线分析。它不调用任何模型 API，不连接模型服务，不读取 API Key，不生成模型评分。

## 内容

| 文件 | 作用 |
|---|---|
| `protocol_manifest.yaml` | 协议范围、计数、构念/比较编号与源路径 |
| `asset_hashes.json` | 冻结资产的 SHA-256 哈希 |
| `material_matrix.csv` | 每条材料一行，共 96 行 |
| `scoring_matrix_template.csv` | 每条材料 × 每个评判槽位一行，共 192 行的模板（无真实评分） |
| `external_result_schema.json` | 外部离线评分文件的最小验证 Schema |
| `external_result_example.jsonl` | 少量确定性示例记录，展示导入格式 |
| `DATA_DICTIONARY.md` | 字段定义 |
| `IMPORT_GUIDE.md` | 验证与导入流程 |
| `REVIEW_CHECKLIST.md` | 内部核查清单 |

## 生成与验证

```bash
uv run python scripts/build_study_b_protocol_package.py --check
uv run python scripts/validate_study_b_external_results.py --input research_packages/study_b/external_result_example.jsonl
```

`build_study_b_protocol_package.py` 在相同仓库状态下重复生成一致，`--check` 不修改任何跟踪文件。

## 边界

- 96 条材料、题项、评分规则、P1—P6 和正式统计模型公式在本包内保持不变。
- 评判模型 ID 仅作为分析协议元数据（`protocol_metadata_only: true`），不据此发起调用。
- 示例记录标记为 schema 示例，使用固定规则数值，不进入公开研究结果。
