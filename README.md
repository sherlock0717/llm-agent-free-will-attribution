# LLM机器主体归因评测

本项目当前以PA—Wu R1为主研究，考察决策过程线索与决策后行为如何影响大语言模型对人工智能决策系统的独立性、目标导向性、心理状态和影响能力等属性的归因判断。

- 当前研究说明：[`docs/CURRENT_STUDY_CARD.md`](docs/CURRENT_STUDY_CARD.md)
- 当前研究与测量来源：[`docs/CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md`](docs/CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md)
- 当前研究展示页：https://sherlock0717.github.io/llm-attribution-behavior-evaluation/pa-wu-r1-pilot/
- 早期研究来源归档：[`docs/research_and_measurement_sources.md`](docs/research_and_measurement_sources.md)
- 早期题项来源映射：[`docs/scale_source_mapping.md`](docs/scale_source_mapping.md)
- 早期研究说明：[`docs/STUDY_CARD.md`](docs/STUDY_CARD.md)

## 当前主研究

当前主研究是 **PA—Wu R1机器主体归因评测**：

- 仅机器主体（人工智能决策系统），不含人类身份比较；
- 6 个条件（C0—C5），逐步加入备选方案、理由、反馈与第二次决定；
- 8 个场景、2 个方向；
- 96 条材料；
- 两个共同主要评判模型配置；每次完整 repeat 产生 192 条模型—材料响应；
- 构念为知觉独立性（IN）、目标导向性（GO）、心理状态推断（MSI）、影响能力（IC），以及感知能动性补充指标（PA5、PA8）。

自由意志只对应 MSI 中的一个探索性题项，不是项目标题、不是唯一核心问题、不作为独立构念，也不生成总分。

当前页面公开数据为 synthetic_demo，仅用于验证材料、评分、分析与展示链，不代表两个评判模型的真实输出、不用于模型排名、不构成理论实证结论。详见 [`docs/CURRENT_STUDY_CARD.md`](docs/CURRENT_STUDY_CARD.md)。

## 早期探索性研究归档

仓库保留一条更早的探索性研究路线，作为**早期探索性研究归档**：

- 包含旧的 AI 与人类身份比较；
- 包含旧的单模型结果；
- 包含自由意志和责任相关的旧指标；
- **不属于当前 R1 设计**；
- **不与当前 R1 结果合并**解释；
- 保留用于版本追踪与方法反思。

早期路线的设计与历史结果记录在 [`docs/STUDY_CARD.md`](docs/STUDY_CARD.md) 与项目总览首页的「早期探索性研究归档」区域。

## 早期探索性研究的原设计

> 以下内容描述的是 PA—Wu R1 建立之前的早期探索性研究路线，**不代表当前主研究设计**。当前研究请见 [`docs/CURRENT_STUDY_CARD.md`](docs/CURRENT_STUDY_CARD.md)。

早期路线使用八个决策情境。每个情境分别呈现六种决策过程，并将行动者标记为 AI 决策者或人类决策者。模型阅读材料后，对行动控制、理由响应、选择自主性、体验性、感知智能和责任等题项评分。

早期设计包含：

- 六种过程表述：直接选择、较长的直接选择、列出方案、简洁理由比较、完整理由比较、反思与反馈修正；
- 两种行动者身份：AI 决策者、人类决策者；
- 八个情境，覆盖道德冲突、自我控制、人际关系、风险决策、责任困境与服从情境；
- 结构化响应、题项计分、条件比较和运行记录。

早期路线的分析单位是**模型对一份材料给出的评分响应**。

### 早期历史公开结果

> 以下结果属于早期探索性研究路线，与 PA—Wu R1 的合成流程演示无关，不应混为当前设计。

早期公开结果支持三项较稳妥的描述：

1. 能动性评分对过程表述最敏感，包含理由比较和行为修正的材料通常获得更高评分。
2. 行动者身份会明显影响体验性、自由意志与责任相关评分，模型对 AI 与人类标签采用了不同判断方式。
3. 在加入感知智能与文本长度后，自由意志评分的直接过程差异明显减弱；能动性与自由意志评分之间的关系仅作为关联性诊断。

这些结果来自单一模型和早期材料，更适合理解为**早期的模型归因敏感性测试**，而不是关于人类心理或 AI 主体性的结论。

### 早期路线的可核查链路

早期路线保留以下对象，使其历史结论能够回到具体输入和产物：

```text
情境与条件
→ 实际 Prompt
→ 模型响应
→ 题项与构念分数
→ 条件比较
→ 图表与报告
```

运行器会记录任务配置、刺激快照、Prompt、响应、评分、错误信息和运行清单，并使用哈希关联输入与产物。确定性 `mock` 仅用于检查解析、校验、计分和文件生成流程。

### 早期运行与复现说明

早期路线使用 Python 3.12 和 `uv` 管理依赖。

```bash
git clone https://github.com/sherlock0717/llm-attribution-behavior-evaluation.git
cd llm-attribution-behavior-evaluation

uv sync --frozen
uv run pytest -q

# 在临时目录执行确定性模拟运行
uv run python -m freewill_attribution.cli run \
  --mock \
  --n-per-cell 2 \
  --out <临时目录>
```

生成并预览展示页：

```bash
uv run python scripts/build_site_data.py
uv run python scripts/build_public_report.py
uv run python scripts/build_showcase_data.py
python -m http.server 8000 --directory site
```

## 仓库结构

```text
src/freewill_attribution/   任务运行、模型接口、解析、计分与运行记录
configs/                    任务、Prompt、模型和指标配置
outputs/                    当前公开分析产物
scripts/                    报告与展示页数据生成脚本
site/                       静态展示页
docs/                       研究说明、测量来源和复现文档
tests/                      单元、集成和站点测试
```

## 文档入口

当前研究：

- 当前研究说明：[`docs/CURRENT_STUDY_CARD.md`](docs/CURRENT_STUDY_CARD.md)
- 当前研究与测量来源：[`docs/CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md`](docs/CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md)
- 当前研究展示页：https://sherlock0717.github.io/llm-attribution-behavior-evaluation/pa-wu-r1-pilot/

早期探索性研究归档：

- 早期研究说明：[`docs/STUDY_CARD.md`](docs/STUDY_CARD.md)
- 早期研究来源归档：[`docs/research_and_measurement_sources.md`](docs/research_and_measurement_sources.md)
- 早期题项来源映射：[`docs/scale_source_mapping.md`](docs/scale_source_mapping.md)
- 早期研究设计：[`docs/research_design_blueprint.md`](docs/research_design_blueprint.md)
- 项目总览首页（含早期归档）：https://sherlock0717.github.io/llm-attribution-behavior-evaluation/

## 权利与使用

仓库暂未采用开放许可证。代码、材料、数据和文档的复制、再分发或用于其他项目，需先获得作者许可。引用公开页面或研究说明时请注明项目名称与仓库地址。
