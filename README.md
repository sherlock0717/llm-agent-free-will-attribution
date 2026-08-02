# LLM行动者归因评测

当同一个决定由不同主体作出，或以不同方式呈现理由、反馈与后续行动时，语言模型会怎样理解这个行动者？

本项目通过两项研究考察身份标签和决策过程写法如何进入模型对能动性、自由意志、心智、影响能力与责任的判断。

- [项目总览](https://sherlock0717.github.io/llm-attribution-behavior-evaluation/)
- [研究A：身份与决策过程](https://sherlock0717.github.io/llm-attribution-behavior-evaluation/identity-process-attribution-baseline/)
- [研究B：机器主体决策过程](https://sherlock0717.github.io/llm-attribution-behavior-evaluation/machine-decision-process-attribution/)

## 两项研究

### [研究A：身份与决策过程归因](https://sherlock0717.github.io/llm-attribution-behavior-evaluation/identity-process-attribution-baseline/)

研究A交叉六种决策过程写法与AI／人类身份标签，分析360条DeepSeek模型问卷响应。

- 8个任务场景
- 6种过程条件
- 2种身份标签
- 条件差异、身份差异与场景变化
- 主要图表、稳健性分析与复现入口

### [研究B：机器主体决策过程归因](https://sherlock0717.github.io/llm-attribution-behavior-evaluation/machine-decision-process-attribution/)

研究B固定机器主体，将过程信息拆为只给出决定、展示备选、给出理由、加入反馈、反馈后维持和反馈后改变六种条件。

- 6种条件 × 8个场景 × 2个方向，共96条材料
- 四个主要评价维度与两个补充指标
- 六项预设比较
- 材料结构审计与离线分析方案
- 材料、题项和分析界面

## 主要发现

研究A中最清楚的三个结果是：

1. **高结构过程写法对应更高的能动性评分。** 包含理由、反思、反馈与后续行动的成套写法，比只包含较长背景和最终选择的写法平均高出1.263分；16个场景×身份配对单元方向一致。
2. **人类标签对应更高的自由意志归因。** 任务场景和过程写法相同时，人类标签下的自由意志归因平均比AI标签高0.760分；48个场景×过程条件身份配对单元方向一致。
3. **变化幅度随任务场景而变。** 过程差异在八个场景中的平均范围为0.67至1.92，留一场景分析中保持同号。

研究A使用单一DeepSeek API配置的历史响应。文本长度与过程条件在材料中共同变化，因此过程比较按两种完整写法理解。研究B聚焦材料、评价规则和离线分析方案。

## 从结果继续追问

### 测量的究竟是哪一层

同一项系统表现可以拆成三个对象：

- 任务是否完成、约束是否满足；
- 系统是否比较备选、说明理由、处理反馈并更新行动；
- 观察者是否据此认为行动者更自主、更有意图或更应负责。

把三类指标分别记录，有助于解释模型为何获得某种评价。

### Agent是否真正改变了后续行为

反馈后的行为可以继续拆成接收信息、更新计划和改变执行。除最终成功率外，轨迹还可以记录恢复时间、重复操作、副作用、回退能力和可逆性。

### 产品如何影响用户判断

“AI助手”“代理”“同事”等名称，以及头像、第一人称表达、解释方式和自动化范围，会进入用户的信任、授权、覆盖行为与责任判断。产品研究可以进一步观察用户何时接受、复核、中止或回退系统建议，以及成功和失败后如何分配功劳与责任。

完整讨论见[`docs/RESULTS_AND_PRACTICAL_IMPLICATIONS.md`](docs/RESULTS_AND_PRACTICAL_IMPLICATIONS.md)。

## 数据与复现

```bash
uv sync --frozen
uv run python scripts/build_site_data.py --check
uv run python scripts/build_showcase_data.py --check
uv run python scripts/build_study_b_protocol_package.py --check
uv run python scripts/check_research_a_robustness_outputs.py
uv run python scripts/audit_study_b_materials.py --check
uv run python scripts/check_public_json.py
uv run pytest -q
python scripts/assemble_pages.py --output _site
python -m http.server 8000 --directory _site
```

本地入口：

- 项目总览：`http://localhost:8000/`
- 研究A：`http://localhost:8000/identity-process-attribution-baseline/`
- 研究B：`http://localhost:8000/machine-decision-process-attribution/`

## 项目结构

```text
src/freewill_attribution/   研究A任务运行、解析、计分与记录
configs/                    研究A任务、Prompt、模型和指标配置
tasks/                      研究B协议、材料、评价与分析资产
outputs/                    研究A已有分析产物
research_packages/study_b/  研究B离线协议与外部记录格式
runs/study_b_offline_demo/  固定数据分析示例
scripts/                    数据构建、分析、检查与Pages组装脚本
site/                       项目总览页面
docs/                       研究页面、来源与复现文档
tests/                      单元、集成和站点测试
```

## 文档入口

1. [结果与延伸问题](docs/RESULTS_AND_PRACTICAL_IMPLICATIONS.md)
2. [总体研究计划](docs/RESEARCH_PROGRAM.md)
3. [评测设计检查清单](docs/EVALUATION_DESIGN_CHECKLIST.md)
4. [统一数据来源字典](docs/data_provenance.yaml)
5. [研究A说明](docs/STUDY_CARD.md)
6. [研究B说明](docs/STUDY_B_CARD.md)
7. [公开页面表达规范](docs/PUBLIC_PRESENTATION_GUIDE.md)

## 权利与使用

仓库代码、材料、数据和文档由作者保留权利。引用时请注明“LLM行动者归因评测”与仓库地址；来源题项按照对应来源文档记录的许可状态使用。
