# LLM行动者归因评测

本项目研究：身份标签、决策过程线索与决策后行为，如何影响语言模型对行动者能动性、心理状态、选择自主性、影响能力与责任的归因判断。项目测量的是模型的归因反应，不判断 AI 或任何行动者是否真实拥有相应心理属性。

## 项目概览

项目稳定ID为 `llm_actor_attribution_program`。仓库组织两项相互独立的研究，以及一套共享的归因评测方法与基础设施。两项研究服务于同一总体问题，但材料、题项、设计、数据与可支持结论各自独立，统计结果不合并。

完整计划首先见 [`docs/RESEARCH_PROGRAM.md`](docs/RESEARCH_PROGRAM.md)。

## 研究计划

### 研究A：身份与决策过程归因基线

稳定ID：`identity_process_attribution_baseline`

研究A采用六类决策过程与 AI/人类身份标签的交叉设计，使用已有单模型输出探索 agency、experience、自由意志相关归因、责任与其他判断。它建立探索性基线，并暴露题项来源、构念交叉、文本长度和主体可比性问题。

研究A不是被废弃的研究。仓库继续保留其已有结果、PNG 图表、分析产物与从材料到报告的可核查链；这些结果只用于描述该研究材料下的模型归因反应，不与研究B合并。

- 研究说明：[`docs/STUDY_CARD.md`](docs/STUDY_CARD.md)
- 研究与测量来源：[`docs/research_and_measurement_sources.md`](docs/research_and_measurement_sources.md)
- 题项来源映射：[`docs/scale_source_mapping.md`](docs/scale_source_mapping.md)
- 设计蓝图：[`docs/research_design_blueprint.md`](docs/research_design_blueprint.md)

### 研究B：机器主体决策过程归因评测

稳定ID：`machine_decision_process_attribution`

研究B仅研究机器主体，考察决策信息、反馈与第二次决定如何影响 IN、GO、MSI、IC、PA5 和 PA8。设计为 6 条件 × 8 场景 × 2 方向，共 96 条材料；计划由两个评判模型对同一材料集独立评分。

研究B当前公开数据仅为 `synthetic_demo`，只验证材料、评分、分析与展示管线。尚无真实模型实证结果，不支持效应、模型差异、模型排名或理论结论。自由意志只对应 MSI 中的一个探索性题项，不是唯一核心问题、独立构念或总分。

- 研究说明：[`docs/CURRENT_STUDY_CARD.md`](docs/CURRENT_STUDY_CARD.md)
- 研究与测量来源：[`docs/CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md`](docs/CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md)
- 独立展示页：https://sherlock0717.github.io/llm-attribution-behavior-evaluation/pa-wu-r1-pilot/

## 为什么形成两项研究

研究A探索身份和过程归因，继而暴露题项来源、构念交叉、文本长度和主体可比性问题。研究B据此建立机器主体构念与反馈行为的测量深化路线，并为未来跨主体平行测量准备基础。

这是一条逻辑演进，而不是“新研究替代旧研究”的时间排序。研究B不抹去研究A的问题与证据，研究A也不为研究B提供可直接合并的统计结果。

## 证据状态对照

| 维度 | 研究A | 研究B |
|---|---|---|
| 功能 | 探索性基线与测量问题识别 | 机器主体测量深化 |
| 设计 | 6 类过程 × 2 种身份 | 6 条件 × 8 场景 × 2 方向；96 条材料 |
| 数据 | 有单模型历史输出与既有分析 | 仅 `synthetic_demo` 合成管线数据 |
| 模型 | 单模型历史运行 | 双评判模型计划，尚未真实运行 |
| 可支持内容 | 研究A材料下的描述性比较与关联性诊断 | 管线贯通与数据契约验证 |
| 主要边界 | 测量成熟度与运行溯源有限 | 无真实实证结果 |

方法约束更严格不等于证据已经完成。两项研究均不声称内容效度、构念效度或机器/人类测量等值性成立。

## 共享方法与复现

“归因评测方法与基础设施”覆盖材料、题项来源、评分、模型调用、质量检查、分析、展示与复现。共享代码与数据契约用于一致地追踪证据，但不会把研究A与研究B的数据混为一个统计样本。

研究A的既有输出保持只读。确定性 `mock` 与研究B的合成数据仅用于工程验证，不进入实证解释。

```bash
uv sync --frozen
uv run pytest -q
uv run python scripts/build_site_data.py --check
uv run python scripts/build_showcase_data.py --check
python -m http.server 8000 --directory site
```

## 后续扩展路线

研究C候选“跨主体平行测量与可比性研究”需要独立的人类题项资产，不能把机器题项直接改写后进行比较；在跨主体比较前还需开展专门的测量可比性研究。该路线尚未执行。

## 仓库结构

```text
src/freewill_attribution/   任务运行、模型接口、解析、计分与运行记录
configs/                    研究A任务、Prompt、模型和指标配置
tasks/                      研究B协议、材料、评分、分析与合成管线资产
outputs/                    研究A已有分析产物（保持只读）
scripts/                    站点数据与报告构建脚本
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

仓库暂未采用开放许可证。代码、材料、数据和文档的复制、再分发或用于其他项目，需先获得作者许可。引用公开页面或研究说明时请注明项目名称与仓库地址；各来源题项的许可状态以对应来源文档为准。
