# LLM行动者归因评测

本项目记录语言模型在不同身份、决策过程和反馈行为材料下形成的归因反应，重点分析能动性、心理状态、选择自主性、影响能力与责任判断的变化。

## 项目概览

项目由两项研究和一套共享方法组成。研究A是身份与决策过程归因的探索性基线，研究B进一步拆分机器主体的决策信息和反馈行为。两项研究分别使用自己的材料、题项和分析结果，共同构成项目证据链。完整计划见 [`docs/RESEARCH_PROGRAM.md`](docs/RESEARCH_PROGRAM.md)。

## 研究计划

### 研究A：身份与决策过程归因基线

研究A采用六类决策过程与 AI/人类身份标签的交叉设计，使用已有单模型输出观察模型对能动性、体验性、自由意志相关归因与责任的评分变化。它建立探索性基线，并在分析中识别出题项来源、构念交叉、文本长度和主体可比性等需要继续完善的测量问题。

研究A保留为身份与决策过程归因的探索性基线，已有模型输出、分析图表和复现链继续作为该研究的证据，并按本研究设计单独呈现。

- 研究说明：[`docs/STUDY_CARD.md`](docs/STUDY_CARD.md)
- 研究与测量来源：[`docs/research_and_measurement_sources.md`](docs/research_and_measurement_sources.md)
- 题项来源映射：[`docs/scale_source_mapping.md`](docs/scale_source_mapping.md)
- 设计蓝图：[`docs/research_design_blueprint.md`](docs/research_design_blueprint.md)

### 研究B：机器主体决策过程归因评测

研究B聚焦机器主体，考察决策信息、反馈与第二次决定如何影响 IN、GO、MSI、IC、PA5 和 PA8。设计为 6 条件 × 8 场景 × 2 方向，共 96 条材料，并计划由两个评判模型对同一材料集独立评分。自由意志对应 MSI 中的一个探索性题项，按单项报告。

研究B已经完成材料、评分、分析和展示管线。页面当前展示流程演示数据；真实双模型运行完成后，将在同一分析框架下更新结果。

- 研究说明：[`docs/CURRENT_STUDY_CARD.md`](docs/CURRENT_STUDY_CARD.md)
- 研究与测量来源：[`docs/CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md`](docs/CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md)
- 独立展示页：https://sherlock0717.github.io/llm-attribution-behavior-evaluation/machine-decision-process-attribution/

## 为什么形成两项研究

研究A提出关于身份与决策过程如何影响归因的广义问题，并在分析中识别出题项来源、构念交叉、文本长度和主体可比性问题。研究B据此聚焦机器主体，对决策信息和反馈行为做进一步拆分。两项研究分别报告结果，共同构成项目的证据链。

## 证据状态对照

| 维度 | 研究A | 研究B |
|---|---|---|
| 研究功能 | 探索性基线与测量问题识别 | 机器主体测量深化 |
| 设计 | 6 类过程 × 2 种身份 | 6 条件 × 8 场景 × 2 方向，96 条材料 |
| 已有数据 | 单模型输出与既有分析 | 材料与合成流程演示数据 |
| 当前可回答 | 研究A材料下的描述性比较与关联性诊断 | 材料、评分、分析和展示链是否能够按协议运行 |
| 测量状态 | 题项来源、构念交叉与主体可比性仍在完善 | 内容效度、构念效度与跨主体可比性列入后续验证 |
| 下一步 | 跨模型与提示稳健性、测量验证、运行溯源补全 | 执行双评判模型运行并更新实证结果 |

研究A和研究B分别使用自己的材料、题项和分析结果。项目总览把两项研究放在同一研究计划中展示，同时保留各自的证据来源。

## 共享方法与复现

“归因评测方法与基础设施”统一记录材料、题项来源、评分、模型调用、质量检查、分析和页面输出。研究A与研究B分别调用这些工具，并保存各自的数据契约和分析结果。

本地预览根页面和研究B页面时，先组装再启动服务器：

```bash
python scripts/assemble_pages.py --output _site
python -m http.server 8000 --directory _site
```

组装后可访问：

- 根页面 http://localhost:8000/
- 研究B http://localhost:8000/machine-decision-process-attribution/
- 旧路径跳转 http://localhost:8000/pa-wu-r1-pilot/

生成站点数据与运行测试：

```bash
uv sync --frozen
uv run pytest -q
uv run python scripts/build_site_data.py --check
uv run python scripts/build_showcase_data.py --check
```

## 后续扩展路线

下一步研究是“跨主体平行测量与可比性研究”。它将独立建设人类主体题项，记录其来源和适用范围，并在跨主体比较前检验机器与人类两套测量的可比性。

## 仓库结构

```text
src/freewill_attribution/   任务运行、模型接口、解析、计分与运行记录
configs/                    研究A任务、Prompt、模型和指标配置
tasks/                      研究B协议、材料、评分、分析与合成管线资产
outputs/                    研究A已有分析产物（保持只读）
scripts/                    站点数据、报告与 Pages 组装脚本
site/                       项目级静态展示页
docs/                       研究计划、研究说明、来源与复现文档
tests/                      单元、集成和站点测试
```

## 文档入口

1. [项目研究计划](docs/RESEARCH_PROGRAM.md)
2. [研究A：身份与决策过程归因基线](docs/STUDY_CARD.md)
3. [研究B：机器主体决策过程归因评测](docs/CURRENT_STUDY_CARD.md)
4. [研究A的研究与测量来源](docs/research_and_measurement_sources.md)
5. [研究B的研究与测量来源](docs/CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md)
6. [研究A设计蓝图](docs/research_design_blueprint.md)

## 权利与使用

仓库暂未采用开放许可证。代码、材料、数据和文档的复制、再分发或用于其他项目，请先获得作者许可。引用公开页面或研究说明时请注明项目名称与仓库地址；各来源题项的许可状态以对应来源文档为准。
