# 研究A分析V2：场景区组与模型生成重复

## 1. 分析目标

研究A V2以场景为主要组织层级，描述单一DeepSeek配置在六类过程条件与两种身份标签下的归因反应。分析重点包括：

- 各条件与身份组合的场景级均值；
- 预先指定条件比较在不同场景和身份中的方向；
- 场景范围与方向一致数；
- 留一场景后的平均差异范围；
- 既有模型生成重复在同一分析单元内的离散程度。

历史分析产物继续保存在`outputs/`。V2脚本将新结果写入独立目录，不覆盖历史CSV、图表与报告。

## 2. 数据来源

数据源：`outputs/scale_scores.csv`

公开名称：**DeepSeek API模型模拟问卷响应**

数据角色：研究A探索性基线

每条记录包含：

- `scenario_id`
- `identity_label`
- `process_condition`
- 模型生成记录编号
- 题项聚合后的构念分数
- 文本长度与选择倾向等设计字段

## 3. 核心分析单元

V2核心单元为：

```text
场景 × 身份标签 × 过程条件
8 × 2 × 6 = 96个单元
```

同一单元内的3—4条模型生成记录用于计算：

- 单元均值；
- 单元标准差；
- 单元记录数。

页面首层结果以96个单元及其场景结构为基础组织。调用级结果保留在数据文件与技术分析中。

## 4. 过程条件

六个过程条件作为分类变量：

1. `direct_choice`
2. `direct_choice_long`
3. `alternatives`
4. `reasons_concise`
5. `reasons`
6. `reflection_feedback`

`direct_choice_long`与`reasons_concise`承担长度—理由结构诊断功能。V2不把六个条件视为等距连续等级。

## 5. 预先指定比较

| ID | 左侧条件 | 右侧条件 | 研究用途 |
|---|---|---|---|
| A1 | alternatives | direct_choice | 候选方案线索 |
| A2 | reasons_concise | direct_choice_long | 短理由结构与长背景文本 |
| A3 | reflection_feedback | reasons | 反思反馈相对完整理由 |
| A4 | reflection_feedback | direct_choice_long | 高结构过程与长文本直接选择 |

每个比较在同一`scenario_id × identity_label`内计算左侧减右侧差值。

## 6. 公开报告字段

每个构念与比较报告：

- 平均差值；
- 中位数差值；
- 最小值与最大值；
- 正向、负向与零差异单元数；
- 方向一致率；
- 场景均值差异；
- 留一场景平均差异的最小值与最大值；
- 匹配单元数量。

公开页面优先展示差异方向、场景范围和一致数。既有OLS、Welch t检验与Bootstrap路径结果保留为历史探索性分析入口。

## 7. 构念

V2支持研究A数据中已有的构念列，包括：

- factual_manipulation_check
- subjective_process_completeness
- agency
- free_will_attribution
- autonomy
- experience
- perceived_intelligence
- outcome_accountability
- moral_praise_blame
- process_accountability
- responsibility_total

研究A页面首层重点展示：

- subjective_process_completeness
- agency
- free_will_attribution
- perceived_intelligence
- responsibility_total

## 8. 探索性关联路径

`structure_level → agency → free_will_attribution`保留为探索性关联路径诊断。该部分用于描述既有编码下的变量关系，主结果由分类条件比较和场景级差异构成。

## 9. 输出目录

默认输出：

```text
artifacts/research_a_v2/
├── unit_summary.csv
├── condition_summary.csv
├── contrast_unit_differences.csv
├── contrast_summary.csv
├── research_a_v2_summary.json
└── research_a_v2_report.md
```

`artifacts/`用于新分析产物和本地复核。正式公开后，可由单独发布步骤复制经过核查的摘要数据到研究A页面数据目录。

## 10. 页面更新规则

研究A页面在V2摘要文件发布前继续展示既有聚合结果，并明确V2分析结构。V2摘要发布后，页面新增：

- 场景方向一致数；
- 场景差异范围；
- 留一场景区间；
- 条件比较表；
- 场景级可视化。

研究A历史CSV、图表和报告保持原样。
