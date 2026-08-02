# LLM行动者归因评测

当语言模型读到一个人或AI作出决定时，它会怎样判断这个行动者是否自主、有意图、能影响结果，或者应当承担责任？本项目把这种判断称为**行动者归因**。

项目通过两项相互衔接的研究考察身份标签和决策过程写法如何进入模型评价：

- [项目总览](https://sherlock0717.github.io/llm-attribution-behavior-evaluation/)
- [研究A：身份与决策过程](https://sherlock0717.github.io/llm-attribution-behavior-evaluation/identity-process-attribution-baseline/)
- [研究B：机器主体决策过程](https://sherlock0717.github.io/llm-attribution-behavior-evaluation/machine-decision-process-attribution/)

## 两项研究

### [研究A：身份与决策过程归因](https://sherlock0717.github.io/llm-attribution-behavior-evaluation/identity-process-attribution-baseline/)

研究A交叉六种决策过程写法与AI／人类身份标签，分析360次DeepSeek模型问卷评分输出。六种过程条件与两种身份形成12个实验组合，每个组合包含30次评分；这些记录分布到8个任务场景中，并进一步汇总为96个场景×身份×过程条件单元。

### [研究B：机器主体决策过程归因](https://sherlock0717.github.io/llm-attribution-behavior-evaluation/machine-decision-process-attribution/)

研究B固定机器主体，把过程信息拆成只给出决定、展示备选、给出理由、加入反馈、反馈后维持和反馈后改变六种条件，共形成96条材料、四个主要评价维度、六项预设比较以及离线分析协议。

## 主要发现

研究A中最清楚的三个结果是：

1. **高结构过程写法对应更高的能动性评分。** 在1—7分量尺上，包含理由、反思、反馈与后续行动的成套写法，比只包含较长背景和最终选择的写法平均高1.263分；16个场景×身份配对单元方向一致。
2. **人类标签对应更高的自由意志归因。** 在1—7分量尺上，任务场景和过程写法相同时，人类标签下的自由意志归因平均比AI标签高0.760分；48个场景×过程条件身份配对单元方向一致。
3. **变化幅度随任务场景而变。** 过程差异在八个场景中的平均范围为0.67至1.92，留一场景分析中保持同号。

这里的360表示模型评分输出次数；16和48表示材料组合的配对数量。文本长度与过程条件共同变化，因此过程结果按两种完整写法的差异理解。

## 为什么这个问题重要

### 1. 结果、过程和主体归因需要分开

当前模型与Agent评测越来越重视推理步骤、工具调用和执行轨迹。过程监督研究表明，逐步评价可以提供不同于最终答案的训练与测量信号；与此同时，推理文本忠实性研究也提醒，模型写出的理由不一定等同于真实内部决策依据。本项目提供了一个受控例子：即使任务结果相同，过程写法本身也会改变评价者对行动者的理解。因此，评测应分别记录任务结果、可观察过程和主体归因。

### 2. Agent评测需要检查反馈之后发生了什么

真实Agent不会只提交一次答案，还会接收反馈、修改计划、调用工具、恢复错误并产生可逆或不可逆的后果。近期轨迹评测已经开始同时记录成功、重复操作、副作用、工具选择、参数正确性和依赖顺序。研究B把“收到反馈”“维持决定”“改变决定”拆开，为构建反馈响应、计划更新和实际执行变化的Rubric提供了最小材料结构。

### 3. 产品界面会塑造信任、授权和责任判断

“助手”“代理”“同事”等身份名称、第一人称表达、解释详细程度和自动执行范围，都会影响用户如何理解系统。现实产品可进一步测量用户何时接受、复核、覆盖、中止或回退系统建议，以及成功和失败后如何分配功劳、过错与责任。该问题直接关系到客服、办公Copilot、决策支持、内容工具和工作流自动化中的信任校准。

### 4. 部署评价必须回到具体场景和人机角色

研究A显示差异幅度随场景变化。NIST AI RMF等风险框架也强调，应在具体使用情境中界定系统、用户、审批者和组织的角色，再决定测量与管理方式。对高风险系统而言，仅报告平均能力不足以回答谁能覆盖建议、谁能中止执行、失败如何发现以及责任如何追踪。

完整论述与前沿研究对应关系见[结果与延伸问题](docs/RESULTS_AND_PRACTICAL_IMPLICATIONS.md)。

## 在线浏览与本地复现

只阅读项目时，直接使用上方三个在线入口。

本地预览需要Python 3.12与[uv](https://docs.astral.sh/uv/)：

```bash
uv sync --frozen
python scripts/assemble_pages.py --output _site
python -m http.server 8000 --directory _site
```

上述命令只组装本地页面，不调用真实模型。完整开发验证：

```bash
uv run python scripts/build_site_data.py --check
uv run python scripts/build_showcase_data.py --check
uv run python scripts/build_study_b_protocol_package.py --check
uv run python scripts/check_research_a_robustness_outputs.py
uv run python scripts/audit_study_b_materials.py --check
uv run python scripts/check_public_json.py
uv run pytest -q
```

## 项目结构

```text
src/freewill_attribution/   任务运行、解析、计分与记录
configs/                    任务、Prompt、模型和指标配置
tasks/                      研究B协议、材料、评价与分析资产
outputs/                    研究A历史分析产物
research_packages/study_b/  研究B离线协议与外部记录格式
runs/study_b_offline_demo/  固定数据分析示例
scripts/                    数据构建、分析、检查与Pages组装脚本
site/                       项目总览页面
docs/                       研究页面、来源与复现文档
tests/                      单元、集成和站点测试
```

## 建议阅读

1. [结果与延伸问题](docs/RESULTS_AND_PRACTICAL_IMPLICATIONS.md)
2. [研究A说明](docs/STUDY_CARD.md)
3. [研究B说明](docs/STUDY_B_CARD.md)
4. [评测与产品检查清单](docs/EVALUATION_DESIGN_CHECKLIST.md)

技术资料包括[总体研究计划](docs/RESEARCH_PROGRAM.md)、[统一数据来源字典](docs/data_provenance.yaml)和[公开页面表达规范](docs/PUBLIC_PRESENTATION_GUIDE.md)。

## 权利与使用

仓库代码、材料、数据和文档由作者保留权利。引用时请注明“LLM行动者归因评测”与仓库地址；来源题项按照对应来源文档记录的许可状态使用。
