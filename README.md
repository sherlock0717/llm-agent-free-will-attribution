# LLM行动者归因评测

本项目研究一个问题：同一个决定被写成不同的身份和决策过程时，语言模型会不会改变对行动者的评价。研究A观察身份标签和过程描述是否对应不同的模型评价；研究B固定机器主体，把备选方案、理由、反馈和反馈后的行动拆成具体条件，分析哪些线索推动评价变化。

## 项目概览

项目由两项研究组成。研究A用已有模型响应观察现象，研究B把决策过程拆得更细，分别考察每一类线索。两项研究分别使用自己的材料、题项和分析结果。完整计划见 [`docs/RESEARCH_PROGRAM.md`](docs/RESEARCH_PROGRAM.md)。

## 研究A：身份与决策过程归因

研究A让DeepSeek模型阅读八类决策场景。材料一方面改变行动者的身份标签，另一方面改变决策过程的写法，从只给最终选择逐步扩展到理由、反馈和后续修正。360条模型响应用于观察模型对能动性、体验性、自由意志相关归因与责任的评分变化。

研究A已经形成材料、34个情境化题项、构念得分、条件比较、场景一致性分析和复现链。扩展路线包括跨模型运行、Prompt盲化和测量结构复核。

- 独立展示页：https://sherlock0717.github.io/llm-attribution-behavior-evaluation/identity-process-attribution-baseline/
- 研究说明：[`docs/STUDY_CARD.md`](docs/STUDY_CARD.md)
- 研究与测量来源：[`docs/research_and_measurement_sources.md`](docs/research_and_measurement_sources.md)
- 题项来源映射：[`docs/scale_source_mapping.md`](docs/scale_source_mapping.md)
- 设计蓝图：[`docs/research_design_blueprint.md`](docs/research_design_blueprint.md)

## 研究B：机器主体决策过程归因

研究B固定机器主体，考察备选方案、明确理由、外部反馈以及反馈后的维持或改变分别如何影响模型的评价。四个主要评价维度是知觉独立性（IN）、目标导向性（GO）、心理状态推断（MSI）和影响能力（IC），另有两个感知能动性补充指标（PA5、PA8）。设计包含六个条件、八个场景和两个方向，共96条材料；两个评判模型对同一材料集独立评分。

研究B已经建立材料、评分规则、分析计划、确定性分析界面示例，以及外部离线结果导入契约与可复现分析流程。仓库的可执行范围止于本地验证、结果导入和离线分析；外部提供的离线评分文件通过验证后，可以进入同一分析流程。

- 独立展示页：https://sherlock0717.github.io/llm-attribution-behavior-evaluation/machine-decision-process-attribution/
- 研究说明：[`docs/STUDY_B_CARD.md`](docs/STUDY_B_CARD.md)
- 研究与测量来源：[`docs/STUDY_B_RESEARCH_AND_MEASUREMENT_SOURCES.md`](docs/STUDY_B_RESEARCH_AND_MEASUREMENT_SOURCES.md)
- 离线研究包：[`research_packages/study_b/`](research_packages/study_b/README.md)（协议、材料矩阵、评分模板、导入 Schema）

## 两项研究如何衔接

研究A提出身份与决策过程如何影响归因的问题，并识别题项来源、构念交叉、文本长度和主体可比性等测量议题。研究B据此固定机器主体，把决定信息、反馈和后续行为拆分为六个可核查条件。两项研究分别报告结果，使用同一套材料—评分—分析方法。

未来工作在外部离线评分结果进入分析流程后，建立与机器主体平行的人类主体测量，分析两类主体的评价结构如何对应。

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
tasks/                      研究B协议、材料、评分、分析与示例资产
outputs/                    研究A已有分析产物（保持只读）
scripts/                    站点数据、报告、严格JSON与Pages组装脚本
site/                       项目总览页面与共享公开数据
docs/identity-process-attribution-baseline/  研究A独立页面
docs/pa-wu-r1-pilot/        研究B独立页面源目录
docs/study_b/               研究B文档入口
docs/                       研究计划、研究说明、来源与复现文档
tests/                      单元、集成和站点测试
```

## 文档入口

1. [项目研究计划](docs/RESEARCH_PROGRAM.md)
2. [公开页面表达规范](docs/PUBLIC_PRESENTATION_GUIDE.md)
3. [统一数据来源字典](docs/data_provenance.yaml)
4. [研究A说明](docs/STUDY_CARD.md)
5. [研究B说明](docs/STUDY_B_CARD.md)
6. [研究A研究与测量来源](docs/research_and_measurement_sources.md)
7. [研究B研究与测量来源](docs/STUDY_B_RESEARCH_AND_MEASUREMENT_SOURCES.md)
8. [研究A设计蓝图](docs/research_design_blueprint.md)

## 权利与使用

仓库代码、材料、数据和文档由作者保留权利。项目引用请注明“LLM行动者归因评测”与仓库地址；各来源题项按照对应来源文档记录的许可状态使用。
