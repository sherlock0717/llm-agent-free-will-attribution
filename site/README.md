# LLM行动者归因评测静态展示页

`site/` 是项目级根展示页，呈现总体研究问题、研究A“身份与决策过程归因基线”、研究B“机器主体决策过程归因评测”、共享方法层与研究C候选路线。页面使用原生 HTML、CSS、JavaScript 和静态 JSON，不依赖外部字体、CDN、第三方脚本或后端服务。

研究A与研究B在根页面处于同一层级，但材料、题项、数据和结论不混合。研究A已有结果、图表和分析继续由根页面展示；研究B的独立展示页继续沿用 `/pa-wu-r1-pilot/` 路径，并明确其数据仅为 `synthetic_demo`。

## 页面结构与部署组装

- `site/`：项目级根展示页，以及研究A详细结果与复现区域；
- `docs/pa-wu-r1-pilot/`：研究B独立展示页；
- Pages workflow 在部署时把两者组装到临时目录 `_site/`，研究B页面位于 `_site/pa-wu-r1-pilot/`；
- `_site/` 仅为部署临时目录，不提交仓库。

研究B公开位置：
https://sherlock0717.github.io/llm-attribution-behavior-evaluation/pa-wu-r1-pilot/

## 本地预览

只预览根页面：

```bash
python -m http.server 8000 --directory site
```

要预览完整 Pages 结果（含研究B独立展示页），需先按 Pages workflow 的目录结构组装临时目录。页面通过 `fetch` 读取本地 JSON，因此不能直接双击 HTML。附加 `?diagnostics=1` 后，页面会写入渲染完成状态和布局诊断属性。

## 生成页面数据

```bash
uv run python scripts/build_site_data.py
uv run python scripts/build_public_report.py
uv run python scripts/build_showcase_data.py
```

生成结果写入 `site/data/`。可计算的研究数字不直接维护在 HTML 中。`showcase_story.json` 的 `research_program` 提供项目级事实，并分别保存研究A与研究B的设计和证据状态。

## 图表、材料与文档

研究A结果图来自仓库已有分析产物，构建过程检查对应文件与哈希。研究结构示意图只解释输入、模型判断和归因输出之间的关系，不承载统计结果。

- [项目研究计划](../docs/RESEARCH_PROGRAM.md)
- [研究A说明](../docs/STUDY_CARD.md)
- [研究A的研究与测量来源](../docs/research_and_measurement_sources.md)
- [研究A题项来源映射](../docs/scale_source_mapping.md)
- [研究B说明](../docs/CURRENT_STUDY_CARD.md)
- [研究B的研究与测量来源](../docs/CURRENT_RESEARCH_AND_MEASUREMENT_SOURCES.md)

## 解释范围

页面展示的是模型在给定材料和评分任务下的归因反应。研究A有单模型输出，但测量成熟度与运行溯源有限；研究B只有合成管线数据，尚无真实模型实证结果。两项研究均不判断行动者真实拥有相应心理属性，也不声称机器和人类测量等值。

## 部署

在线地址：https://sherlock0717.github.io/llm-attribution-behavior-evaluation/

`.github/workflows/pages.yml` 在主分支更新或手动触发时组装并发布根页面与研究B独立展示页。部署过程不调用模型接口，也不读取 API 密钥。
