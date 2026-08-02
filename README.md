# LLM行动者归因评测

同一个决定采用不同的身份和过程写法时，语言模型会怎样改变对行动者的评价？

本项目控制材料中的身份标签、备选方案、理由、反馈与后续行动，观察模型对能动性、心智、自由意志相关归因、影响能力与责任的评分变化。项目由两项研究组成：研究A提供已有模型响应和场景分析；研究B把过程线索拆成六种材料条件，形成可复核的离线研究设计。

- 项目总览：https://sherlock0717.github.io/llm-attribution-behavior-evaluation/
- 研究A结果：https://sherlock0717.github.io/llm-attribution-behavior-evaluation/identity-process-attribution-baseline/
- 研究B设计：https://sherlock0717.github.io/llm-attribution-behavior-evaluation/machine-decision-process-attribution/

## 项目状态

- 项目：公开展示与离线复现版本完成。
- 研究A：已有360条模型响应、场景分析和稳健性分析。
- 研究B：材料、评价规则、离线协议和确定性结构审计完成；语义对称性、理由强度和反馈强度未纳入当前版本。

## 主要发现

研究A基于360条DeepSeek模型问卷响应，覆盖8个场景、6种过程条件和AI／人类两种身份标签。当前结果支持三点：

1. **高结构过程写法对应更高的能动性评分。** 包含理由、反思、反馈与后续行动的高结构过程写法，与只包含较长背景和最终选择的写法相比，能动性评分平均高出1.263分；16个场景×身份配对单元全部呈现相同方向。该比较对应两种成套写法的整体差异，不是反馈这一单项线索的独立效应。
2. **人类标签对应更高的自由意志归因。** 在任务场景和过程写法保持相同时，人类标签下的自由意志归因平均比AI标签高0.760分；48个场景×过程条件身份配对单元全部呈现相同方向。该结果只描述自由意志归因这一维度，不概括所有心智和责任维度。
3. **总体方向不能替代场景分析。** 过程效应和身份效应在留一场景分析中均保持同号，但差异幅度会随任务语境改变；总体均值可能掩盖某些场景的推动或抵消作用。

方向一致数是场景×条件配对单元的描述性统计，用于观察结果是否在不同材料组合中重复出现，不等同于独立样本数量或统计显著性检验。文本长度与过程条件共同变化，现有数据不能可靠分离两者的独立作用。

这些结果描述的是该模型配置在本项目材料和问卷提示下形成的评价模式，不证明跨模型泛化，也不证明行动者真实具有被评分的心理属性。

## 对实际评测的意义

### Benchmark与Rubric

- 将最终行为、决策过程和身份标签分开控制；
- 把“列出备选”“给出理由”“回应反馈”“实际改变行动”设置为不同能力点；
- 同一能力点使用多个场景和多种等价表述；
- 同时报告总体结果、场景范围和方向一致程度；
- 避免把身份标签造成的归因差异误解为能力差异。

### 训练数据与质检

- 不把更长的回答直接视为更强推理；
- 检查理由是否与目标和选择对应；
- 区分接受反馈、复述反馈和据此调整行动；
- 保持不同条件的措辞强度、信息量和结果严重程度可比；
- 在清洗和标注中记录过程信息类型，而不只记录最终答案是否正确。

### Agent与AI产品

- 将“会做决定”拆成方案比较、目标说明、反馈处理和后续执行；
- 把归因评分与任务成功率、约束满足率分别报告；
- 在不同风险、责任和协作场景中重复测试；
- 避免依据一次提示下的自我解释判断模型是否具有稳定的能动性或心智属性。

完整说明见[`docs/RESULTS_AND_PRACTICAL_IMPLICATIONS.md`](docs/RESULTS_AND_PRACTICAL_IMPLICATIONS.md)。

## 研究A：身份与决策过程归因

研究A交叉六种决策过程写法与AI／人类身份标签，共形成360条模型响应。公开页面展示：

- 六种过程条件下的主要评价变化；
- AI与人类标签下的评分差异；
- 八个场景中的方向一致程度和变化范围；
- 数据、题项、分析脚本和复现入口。

相关文档：

- [`docs/STUDY_CARD.md`](docs/STUDY_CARD.md)
- [`docs/research_and_measurement_sources.md`](docs/research_and_measurement_sources.md)
- [`docs/scale_source_mapping.md`](docs/scale_source_mapping.md)
- [`docs/research_design_blueprint.md`](docs/research_design_blueprint.md)

## 研究B：机器主体决策过程归因

研究B固定机器主体，将过程信息拆为六种条件：只给出决定、展示备选方案、给出明确理由、加入外部反馈、反馈后维持决定、反馈后改变决定。设计覆盖8个场景与2个方向，共96条材料。

四个主要评价维度为：

- 知觉独立性（IN）
- 目标导向性（GO）
- 心理状态推断（MSI）
- 影响能力（IC）

PA5和PA8作为感知能动性的补充指标。研究B当前提供材料、评价规则、P1—P6、确定性分析界面、外部离线评价记录格式和可复现分析流程，并完成96条材料的确定性结构审计；语义对称性、理由强度和反馈强度未纳入当前版本。固定数据只用于校验分析流程和页面结构，不构成新的模型研究结果。

相关文档：

- [`docs/STUDY_B_CARD.md`](docs/STUDY_B_CARD.md)
- [`docs/STUDY_B_RESEARCH_AND_MEASUREMENT_SOURCES.md`](docs/STUDY_B_RESEARCH_AND_MEASUREMENT_SOURCES.md)
- [`research_packages/study_b/`](research_packages/study_b/README.md)

## 证据边界

| 内容 | 当前状态 | 可以回答 | 不能据此回答 |
|---|---|---|---|
| 研究A | 360条既有模型响应、场景分析与稳健性分析 | 该模型配置如何根据身份与过程写法调整评价 | 其他模型是否相同、模型是否真实拥有相关心理属性 |
| 研究B | 96条材料、评价规则、离线协议与确定性结构审计 | 如何把备选、理由、反馈和后续行动拆成可核查条件 | 六种条件在正式模型评价中产生了什么结果、材料的语义对称性是否成立 |
| 固定示例 | 确定性数据与图表 | 分析流程、数据格式和页面结构是否可复核 | 正式效应、显著性或模型优劣 |

## 项目结构

```text
src/freewill_attribution/   研究A任务运行、解析、计分与记录
configs/                    研究A任务、Prompt、模型和指标配置
tasks/                      研究B协议、材料、评价与分析资产
outputs/                    研究A已有分析产物（保持只读）
research_packages/study_b/  研究B离线协议与外部记录格式
runs/study_b_offline_demo/  固定数据分析流程示例
scripts/                    数据构建、分析、检查与Pages组装脚本
site/                       项目总览页面
docs/                       研究页面、研究计划、来源与复现文档
tests/                      单元、集成和站点测试
```

## 本地预览

```bash
uv sync --frozen
uv run python scripts/build_site_data.py --check
uv run python scripts/build_showcase_data.py --check
uv run python scripts/build_study_b_protocol_package.py --check
uv run python scripts/analyze_research_a_robustness.py --check
uv run python scripts/audit_study_b_materials.py --check
uv run python scripts/check_public_json.py
uv run pytest -q
python scripts/assemble_pages.py --output _site
python -m http.server 8000 --directory _site
```

访问：

- 项目总览：http://localhost:8000/
- 研究A：http://localhost:8000/identity-process-attribution-baseline/
- 研究B：http://localhost:8000/machine-decision-process-attribution/

## 文档入口

1. [结果与实践启示](docs/RESULTS_AND_PRACTICAL_IMPLICATIONS.md)
2. [总体研究计划](docs/RESEARCH_PROGRAM.md)
3. [评测设计检查清单](docs/EVALUATION_DESIGN_CHECKLIST.md)
4. [统一数据来源字典](docs/data_provenance.yaml)
5. [研究A说明](docs/STUDY_CARD.md)
6. [研究B说明](docs/STUDY_B_CARD.md)
7. [公开页面表达规范](docs/PUBLIC_PRESENTATION_GUIDE.md)

## 权利与使用

仓库代码、材料、数据和文档由作者保留权利。引用时请注明“LLM行动者归因评测”与仓库地址；来源题项按照对应来源文档记录的许可状态使用。
