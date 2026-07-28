# LLM行动者归因评测

本项目记录语言模型在不同身份、决策过程和反馈行为材料下形成的归因反应，重点分析能动性、心理状态、选择自主性、影响能力与责任判断的变化。

## 项目概览

项目由两项研究和一套共享方法组成。研究A建立身份与决策过程归因基线，研究B进一步拆分机器主体的决策信息、反馈与第二次决定。两项研究分别使用自己的材料、题项和分析结果，共同构成项目证据链。完整计划见 [`docs/RESEARCH_PROGRAM.md`](docs/RESEARCH_PROGRAM.md)。

## 研究计划

### 研究A：身份与决策过程归因基线

研究A采用六类决策过程与AI/人类身份标签的交叉设计，使用360条DeepSeek API模型模拟问卷响应，观察模型对能动性、体验性、自由意志相关归因与责任的评分变化。

研究A已经形成材料、34个情境化题项、构念得分、条件比较、场景材料、公开分析产物和复现链。扩展路线包括跨模型运行、Prompt盲化、场景级区组分析和测量结构复核。

- 独立展示页：https://sherlock0717.github.io/llm-attribution-behavior-evaluation/identity-process-attribution-baseline/
- 研究说明：[`docs/STUDY_CARD.md`](docs/STUDY_CARD.md)
- 研究与测量来源：[`docs/research_and_measurement_sources.md`](docs/research_and_measurement_sources.md)
- 题项来源映射：[`docs/scale_source_mapping.md`](docs/scale_source_mapping.md)
- 设计蓝图：[`docs/research_design_blueprint.md`](docs/research_design_blueprint.md)

### 研究B：机器主体决策过程归因评测

研究B聚焦机器主体，考察决定信息、反馈与第二次决定如何影响IN、GO、MSI、IC以及感知能动性的两个重叠评分版本PA5和PA8。设计包含6个D/U组合、8个场景和2个方向，共96条材料；两个评判模型对同一材料集独立评分。

研究B已经完成材料、评分、分析和展示管线。页面展示流程演示数据；下一阶段执行双评判模型运行，并沿用同一分析框架更新结果。

- 独立展示页：https://sherlock0717.github.io/llm-attribution-behavior-evaluation/machine-decision-process-attribution/
- 研究说明：[`docs/CURRENT_STUDY_CARD.md`](docs/CURRENT_STUDY_CARD.md)
- 研究与测量来源：[`docs/CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md`](docs/CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md)

## 为什么形成两项研究

研究A提出身份与决策过程如何影响归因的广义问题，并识别题项来源、构念交叉、文本长度和主体可比性等测量议题。研究B据此固定机器主体，将决定信息、反馈和后续行为拆分为六个可核查组合。两项研究分别报告结果，共享材料—评分—分析—展示的方法链。

## 证据组成

| 维度 | 研究A | 研究B |
|---|---|---|
| 研究功能 | 身份与过程归因基线 | 机器主体测量深化 |
| 设计 | 6类过程 × 2种身份 | 6个D/U组合 × 8场景 × 2方向 |
| 数据资产 | DeepSeek API模型模拟问卷响应 | 流程演示数据与双模型运行协议 |
| 结果用途 | 描述该模型配置在研究A材料中的归因模式 | 展示机器主体材料、评分、分析和图表链 |
| 测量路线 | 题项结构、构念区分、跨Prompt和跨模型复核 | 原量尺构念、重叠评分版本、跨主体可比性研究 |
| 扩展路线 | 场景级分析、Prompt盲化与跨模型运行 | 双评判模型运行与正式结果更新 |

研究A和研究B分别保存材料、题项、数据与分析结果。项目总览将两项研究放在同一研究计划中，并提供各自独立页面。

## 共享方法与复现

“归因评测方法与基础设施”统一记录材料、题项来源、评分、模型调用、质量检查、分析和页面输出。研究A与研究B分别调用这些工具，并保存各自的数据契约和分析结果。

本地预览全部页面：

```bash
python scripts/assemble_pages.py --output _site
python -m http.server 8000 --directory _site
```

组装后可访问：

- 项目总览：http://localhost:8000/
- 研究A：http://localhost:8000/identity-process-attribution-baseline/
- 研究B：http://localhost:8000/machine-decision-process-attribution/
- 研究B旧路径跳转：http://localhost:8000/pa-wu-r1-pilot/

生成数据与发布检查：

```bash
uv sync --frozen
uv run python scripts/build_site_data.py --check
uv run python scripts/build_showcase_data.py --check
uv run python scripts/check_public_json.py
uv run pytest -q tests/site
python scripts/assemble_pages.py --output _site
```

## 扩展路线

跨主体平行测量与可比性研究将独立建设人类主体题项，记录其来源和适用范围，并检验机器与人类两套测量在比较任务中的结构关系。

## 仓库结构

```text
src/freewill_attribution/   任务运行、模型接口、解析、计分与运行记录
configs/                    研究A任务、Prompt、模型和指标配置
tasks/                      研究B协议、材料、评分、分析与流程演示资产
outputs/                    研究A已有分析产物（保持只读）
scripts/                    站点数据、报告、严格JSON与Pages组装脚本
site/                       项目总览页面与共享公开数据
docs/identity-process-attribution-baseline/  研究A独立页面
docs/pa-wu-r1-pilot/        研究B独立页面源目录
docs/                       研究计划、研究说明、来源与复现文档
tests/                      单元、集成和站点测试
```

## 文档入口

1. [项目研究计划](docs/RESEARCH_PROGRAM.md)
2. [公开页面表达规范](docs/PUBLIC_PRESENTATION_GUIDE.md)
3. [统一数据来源字典](docs/data_provenance.yaml)
4. [研究A说明](docs/STUDY_CARD.md)
5. [研究B说明](docs/CURRENT_STUDY_CARD.md)
6. [研究A研究与测量来源](docs/research_and_measurement_sources.md)
7. [研究B研究与测量来源](docs/CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md)
8. [研究A设计蓝图](docs/research_design_blueprint.md)

## 权利与使用

仓库代码、材料、数据和文档由作者保留权利。项目引用请注明“LLM行动者归因评测”与仓库地址；各来源题项按照对应来源文档记录的许可状态使用。
