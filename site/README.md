# LLM行动者归因评测静态展示页

`site/` 是项目级总览页，呈现总体研究问题、研究A与研究B入口、证据组成、共享方法和跨主体扩展路线。页面使用原生HTML、CSS、JavaScript和静态JSON，仅依赖仓库内资源。

研究A与研究B拥有同层独立页面：

- 研究A：`/identity-process-attribution-baseline/`
- 研究B：`/machine-decision-process-attribution/`

两项研究分别保存材料、题项、数据和分析结果。根页面只承担研究计划总览和导航职责。

## 页面结构与部署组装

- `site/`：项目级总览页与共享公开数据；
- `docs/identity-process-attribution-baseline/`：研究A独立展示页；
- `docs/pa-wu-r1-pilot/`：研究B独立展示页源目录；
- `/pa-wu-r1-pilot/`：研究B兼容跳转页；
- `scripts/assemble_pages.py`：组装根页面、研究A、研究B和兼容路径到临时目录`_site/`。

公开位置：

- 项目总览：https://sherlock0717.github.io/llm-attribution-behavior-evaluation/
- 研究A：https://sherlock0717.github.io/llm-attribution-behavior-evaluation/identity-process-attribution-baseline/
- 研究B：https://sherlock0717.github.io/llm-attribution-behavior-evaluation/machine-decision-process-attribution/

## 本地预览

```bash
python scripts/assemble_pages.py --output _site
python -m http.server 8000 --directory _site
```

组装后可访问：

- 项目总览：http://localhost:8000/
- 研究A：http://localhost:8000/identity-process-attribution-baseline/
- 研究B：http://localhost:8000/machine-decision-process-attribution/
- 研究B旧路径跳转：http://localhost:8000/pa-wu-r1-pilot/

## 页面数据与发布检查

```bash
uv run python scripts/build_site_data.py --check
uv run python scripts/build_showcase_data.py --check
uv run python scripts/check_public_json.py
uv run pytest -q tests/site
python scripts/assemble_pages.py --output _site
```

`site/data/`保存项目总览与研究A公开数据。研究A独立页从该目录分组读取场景、构念和分析结果；每组数据拥有独立加载状态。研究B独立页使用自己的`data/showcase_data.json`。

严格JSON检查器使用浏览器兼容解析规则，拒绝`NaN`、`Infinity`和`-Infinity`。Pages工作流在部署前执行数据检查、站点测试、严格JSON检查和组装资源验证。

## 数据口径

- 研究A：DeepSeek API模型模拟问卷响应；
- 研究A mock：确定性工程验证数据；
- 研究B示例：分析界面示例数据；
- 研究B离线导入：外部离线评分文件（通过验证后进入分析流程）。

完整定义见：

- [`docs/PUBLIC_PRESENTATION_GUIDE.md`](../docs/PUBLIC_PRESENTATION_GUIDE.md)
- [`docs/data_provenance.yaml`](../docs/data_provenance.yaml)

## 文档入口

- [项目研究计划](../docs/RESEARCH_PROGRAM.md)
- [研究A说明](../docs/STUDY_CARD.md)
- [研究A研究与测量来源](../docs/research_and_measurement_sources.md)
- [研究A题项来源映射](../docs/scale_source_mapping.md)
- [研究B说明](../docs/STUDY_B_CARD.md)
- [研究B研究与测量来源](../docs/STUDY_B_RESEARCH_AND_MEASUREMENT_SOURCES.md)

## 部署

`.github/workflows/pages.yml`在主分支更新或手动触发时运行发布门禁，随后上传经过验证的`_site/`产物。部署过程只使用静态资源。
