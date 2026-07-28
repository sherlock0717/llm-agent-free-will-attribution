# LLM行动者归因评测静态展示页

`site/` 是项目级根展示页，呈现总体研究问题、研究A“身份与决策过程归因基线”、研究B“机器主体决策过程归因评测”、共享方法层与下一步研究。页面使用原生 HTML、CSS、JavaScript 和静态 JSON，仅依赖本地资源。

研究A与研究B在根页面处于同一层级，并分别保存各自的材料、题项、数据和分析结果。研究A的已有结果、图表和分析由根页面展示；研究B的独立展示页发布在规范路径 `/machine-decision-process-attribution/`，其数据当前为 `synthetic_demo` 流程演示。

## 页面结构与部署组装

- `site/`：项目级根展示页，以及研究A详细结果与复现区域；
- `docs/pa-wu-r1-pilot/`：研究B独立展示页的源目录（内部路径暂时保留）；
- 研究B规范公开路径：`/machine-decision-process-attribution/`；
- `/pa-wu-r1-pilot/`：兼容跳转页，指向规范路径；
- `scripts/assemble_pages.py` 把上述内容组装到临时目录 `_site/`，本地预览与线上部署使用同一组装产物；`_site/` 为临时目录，不提交仓库。

研究B公开位置：
https://sherlock0717.github.io/llm-attribution-behavior-evaluation/machine-decision-process-attribution/

## 本地预览

根页面和研究B页面通过组装后的 `_site` 预览：

```bash
python scripts/assemble_pages.py --output _site
python -m http.server 8000 --directory _site
```

组装后可访问：

- 根页面 http://localhost:8000/
- 研究B http://localhost:8000/machine-decision-process-attribution/
- 旧路径跳转 http://localhost:8000/pa-wu-r1-pilot/

直接以 `site/` 为根启动服务器只能查看根页面源，研究B相对路径需要组装后的 `_site`。页面通过 `fetch` 读取本地 JSON，请使用静态服务器访问。附加 `?diagnostics=1` 后，页面会写入渲染完成状态和布局诊断属性。

## 生成页面数据

```bash
uv run python scripts/build_site_data.py
uv run python scripts/build_public_report.py
uv run python scripts/build_showcase_data.py
```

生成结果写入 `site/data/`。可计算的研究数字由脚本从源文件生成。`showcase_story.json` 的 `research_program` 提供项目级事实，并分别保存研究A与研究B的设计和证据状态。

## 图表、材料与文档

研究A结果图来自仓库已有分析产物，构建过程检查对应文件与哈希。研究结构示意图只解释输入、模型判断和归因输出之间的关系。

- [项目研究计划](../docs/RESEARCH_PROGRAM.md)
- [研究A说明](../docs/STUDY_CARD.md)
- [研究A的研究与测量来源](../docs/research_and_measurement_sources.md)
- [研究A题项来源映射](../docs/scale_source_mapping.md)
- [研究B说明](../docs/CURRENT_STUDY_CARD.md)
- [研究B的研究与测量来源](../docs/CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md)

## 解释范围

页面展示的是模型在给定材料和评分任务下的归因反应。研究A提供单模型输出，测量来源与运行溯源仍在完善；研究B完成了材料与合成流程演示，真实双模型运行列为下一步。两项研究均记录模型的归因反应，跨主体测量可比性列入后续验证。

## 部署

在线地址：https://sherlock0717.github.io/llm-attribution-behavior-evaluation/

`.github/workflows/pages.yml` 在主分支更新或手动触发时运行 `scripts/assemble_pages.py` 组装并发布根页面与研究B页面。部署过程仅使用静态资源。
