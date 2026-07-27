# PA—Wu R1 Showcase (static interactive site)

A static, interactive showcase page **already exists** at `docs/pa-wu-r1-pilot/`
and is published via **GitHub Pages** at
`https://sherlock0717.github.io/llm-attribution-behavior-evaluation/pa-wu-r1-pilot/`.
The current design has **96 materials** (6 conditions × 8 scenarios × 2 directions ×
1 machine identity); each repeat produces **192 model–material responses** (2 judge
models × 96 materials). Five figures are shown on the page. All current numbers are
**synthetic_demo**. The page does **not** rank models and does **not** compare AI
vs. human subjects. This document maps each page section to its content source.

> Every figure is labeled **合成演示数据 / Synthetic demonstration data** and must
> never be presented as a real model result, capability claim or ranking.

| # | Section | Content source | Reusable output |
|---|---------|----------------|-----------------|
| 1 | Project question | `README.md`, `study_protocol.yaml` (research_question) | — |
| 2 | Theoretical sources | P0 instruments (PA 2024; Wu & Shen 2026) | — |
| 3 | Construct framework | `study_protocol.yaml` (IN/GO/MSI/IC + PA5/PA8) | — |
| 4 | Experimental design | `condition_matrix.csv`, `manipulation_blocks.yaml` | — |
| 5 | Six-condition interaction view | `analysis_plan.md` (C* model) | `figures/fig1_condition_construct_means.png` |
| 6 | 96-material coverage (192 responses per repeat) | `stimuli.jsonl`, `validate_pilot_core.py` balance | `outputs/demo_descriptives.csv` |
| 7 | Two-model evaluation method | `study_protocol.yaml` (judge_models) | `figures/fig3_model_profiles.png` |
| 8 | Results overview | `analyze_pilot.py` outputs | `figures/fig1_condition_construct_means.png` |
| 9 | Construct differences | scored construct tables | `figures/fig3_model_profiles.png` |
| 10 | Model-adjusted contrasts | estimated marginal contrasts P1–P6 | `figures/fig2_model_adjusted_contrasts.png` |
| 11 | Scenario heterogeneity | scenario × construct summary | `figures/fig4_scenario_construct_heatmap.png` |
| 12 | Stability & failure types | `demo_quality_summary.json` (parse/validation, repeats) | `demo_quality_summary.json` |
| 13 | Method boundaries | `analysis_plan.md` (pilot vs full B*, no D×U) | — |
| 14 | Reproducible pipeline | `README.md` pipeline; `scripts/` | — |
| 15 | Data & code entry points | this directory tree | `outputs/`, `reports/demo_report.md` |

## Directly reusable demo outputs

- `outputs/figures/fig1_condition_construct_means.png` — sections 5, 8
- `outputs/figures/fig2_model_adjusted_contrasts.png` — section 10 (model-adjusted)
- `outputs/figures/fig3_model_profiles.png` — sections 7, 9
- `outputs/figures/fig4_scenario_construct_heatmap.png` — section 11
- `outputs/figures/fig5_contrast_forest.png` — section 5 (raw planned contrasts)
- `outputs/demo_descriptives.csv`, `outputs/demo_contrasts.csv` — tables
- `reports/demo_report.md` — narrative scaffold

## Current status

- An interactive static front end already exists at `docs/pa-wu-r1-pilot/`
  (`index.html` + `styles.css` + `app.js` + `data/showcase_data.json` + five
  figures under `assets/figures/`), served by GitHub Pages.
- The page shows five figures and reads `data/showcase_data.json`.
- All showcase numbers remain **synthetic_demo** until a real, authorized run is
  executed; the page ranks no model and shows no AI/human comparison.
