# 外部离线结果导入指南

本指南说明如何验证并导入外部产生的离线评分文件。整个流程离线运行：不联网、不读取 API Key、不调用模型、不修改输入文件。

## 1. 准备外部离线文件

外部文件为 JSONL（每行一条记录）或 CSV，字段遵循 `external_result_schema.json`。每条记录对应一个评判槽位对一条材料的评分，必须包含全部 28 个必需题项，数值落在各自原量尺范围。

## 2. 验证

```bash
uv run python scripts/validate_study_b_external_results.py \
  --input path/to/external_results.jsonl \
  --report validation_report.json
```

验证器检查：Schema 字段、`material_id` 是否存在、`judge_slot`、模型 ID、题项完整性、数值范围、重复键、未知字段，并拒绝 NaN 与 Infinity。验证器只读，不补齐或修复数据。

## 3. 导入（先验证）

```bash
# 只验证，不写输出
uv run python scripts/import_study_b_external_results.py \
  --input path/to/external_results.jsonl \
  --validate-only

# 预演，报告将执行的操作，不写输出
uv run python scripts/import_study_b_external_results.py \
  --input path/to/external_results.jsonl \
  --output runs/study_b_external_import/example \
  --dry-run

# 正式导入到新的离线目录（拒绝覆盖已有目录）
uv run python scripts/import_study_b_external_results.py \
  --input path/to/external_results.jsonl \
  --output runs/study_b_external_import/example
```

导入只接受通过验证的文件，并保存源文件 SHA-256、导入时间、验证报告与标准化记录。

## 4. 边界

- 导入器不联网、不读取 API Key、不导入模型 SDK；
- 导入器不覆盖已有导入目录；
- 导入器不推断缺失题项，不用语言模型修复数据；
- 本仓库当前只使用 `external_result_example.jsonl` 走通验证工具，不导入任何真实结果文件。
