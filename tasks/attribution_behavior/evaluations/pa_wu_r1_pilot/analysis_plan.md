# Study B — Machine Decision-Process Attribution — Analysis Plan

> The pipeline currently contains **workflow-demonstration data**.
> This plan specifies the analysis for the dual-judge-model run and demonstrates
> the same analysis and figure path end to end. Internal IDs and repository paths
> are retained for compatibility.

## Pilot C* and future full B*

The pilot uses a **six-level condition factor** (`C0..C5`). The six levels are
selected combinations from the D×U design space:

- C0 = D0-U0
- C1 = D1-U0
- C2 = D2-U0
- C3 = D2-U1
- C4 = D2-U2
- C5 = D2-U3

The pilot estimates differences between these six named conditions. A future full
**B\*** study will cross the D and U levels factorially and estimate the complete
D×U interaction.

## Identity scope

The target subject is fixed as a machine (`target_identity = machine`; see
`identity_scope_decision.md`). Identity therefore remains constant across all
materials, while condition, scenario, direction and judge-model configuration
provide the modeled variation.

## Primary analysis model

For each construct score on its native scale, the primary model is:

```
construct_score ~ C(condition_id) * C(judge_model_id)
                  + C(direction_version)
                  + C(scenario_id)
random intercept: material_id
```

- `condition_id`: six-level categorical factor (C0..C5).
- `judge_model_id`: deepseek-v4-pro / gpt-5.6-terra (co-primary).
- `direction_version`: fixed **block** factor (A / B).
- `scenario_id`: fixed **block** factor (8 pre-selected scenarios).
- `material_id`: **random intercept**.

### Why `material_id` is random and `scenario_id` is fixed

- Each material is scored by **both** judge models. The `material_id` random
  intercept represents this paired structure and allows the two scores of one
  material to share a material-level offset.
- The 8 scenarios are pre-selected fixed blocks. Entering them as fixed effects
  controls average differences among the eight task contexts.
- The primary construct-score model operates on aggregated construct scores. An
  item-level sensitivity analysis may add an item effect.
- When repeated runs exist, `repeat_index` is used as a stability factor for
  within-material variance.

IN, GO, MSI, IC, PA5 and PA8 are modeled separately on their native scales. PA5
and PA8 are overlapping scoring versions of the same perceived-agency source
tool and are interpreted as a scoring-version sensitivity pair.

## Planned contrasts

All contrasts are specified in advance on the `condition` factor:

| id | contrast | interpretation |
|----|----------|----------------|
| P1 | C1 − C0 | explicit alternatives information |
| P2 | C2 − C0 | explicit stated-reason information |
| P3 | C3 − C2 | feedback only |
| P4 | C4 − C2 | feedback + keeping the decision |
| P5 | C5 − C2 | feedback + changing the decision |
| P6 | C5 − C4 | changing vs. keeping the decision |

Each contrast is also examined for interaction with `judge_model_id`. The
condition × model contribution is reported as
`judge_model_interaction_estimate`. Identity is fixed as a machine and therefore
does not enter the contrast model.

## Reported quantities

For each construct and contrast the analysis reports:

- means and standard deviations on the native scale;
- 95% confidence intervals;
- display-only theoretical-scale positions for cross-panel visualization;
- raw and model-adjusted P1—P6 estimates;
- scenario-level spread;
- descriptive differences between the two judge-model configurations.

## Analysis scope

- Native-scale inference is primary; 0—1 positions serve the multi-construct
  heatmap and related display views.
- A construct score is computed when all member items are valid; item and
  construct missingness are retained in the quality summary.
- MSI retains the complete source-tool item set. `wu_ms3` also receives a
  separate exploratory single-item report, while the MSI composite remains one
  of the six primary/secondary construct outcomes.
- The pilot estimates the six selected D/U combinations. The full D×U
  interaction belongs to the factorial extension.
- Judge-model differences are presented as sensitivity results alongside the
  shared condition analysis.

---

## Formal-run analysis specification

The authorized dual-model run will use the same estimation, contrast, reporting
and figure pipeline demonstrated by the current workflow data.

### Estimation method

- Linear mixed-effects model per construct (`statsmodels` `MixedLM`), REML
  estimation, native-scale outcome.
- A random intercept for `material_id`; `scenario_id` and `direction_version`
  enter as fixed blocks.
- Optimizer robustness uses `lbfgs` → `cg` → `powell` → `nm`. The first fit that
  converges and yields a usable coefficient covariance is selected. Convergence
  and Hessian warnings are written to `captured_warnings` in the fit summary.

### Categorical reference levels (Treatment coding)

- `condition_id`: reference = **C0**.
- `judge_model_id`: reference = **deepseek-v4-pro**.
- `direction_version`: reference = **A**.

These reference levels are fixed in advance so contrast signs remain stable.

### Planned-contrast matrix and estimated marginal means

Contrasts are linear combinations of the model's fixed-effect coefficients:

| id | L (+1) | R (−1) |
|----|--------|--------|
| P1 | C1 | C0 |
| P2 | C2 | C0 |
| P3 | C3 | C2 |
| P4 | C4 | C2 |
| P5 | C5 | C2 |
| P6 | C5 | C4 |

The **model-adjusted** contrast is an estimated marginal contrast:

1. build the fixed-effect design matrix `X`;
2. for each condition, average the design rows over the balanced grid (both judge
   models × A/B direction × all 8 scenarios) to obtain `x̄(condition)`;
3. define `L = x̄(left) − x̄(right)`;
4. calculate `estimate = L @ β`;
5. calculate `variance = L @ Cov(β) @ Lᵀ` from the fixed-effect covariance block;
6. calculate `SE = √variance`, the z statistic, two-sided p-value and 95% CI.

Each contrast is also reported as a raw descriptive difference of observed cell
means. The condition × judge-model interaction contribution is reported as
`judge_model_interaction_estimate`.

### Multiple-comparison handling across constructs

- Six constructs × six planned contrasts are specified in advance in this
  analysis plan.
- Family-wise control is applied within each construct's six contrasts using
  Holm–Bonferroni; constructs are treated as separate outcome families.
- The `wu_ms3` single-item report and post-hoc interaction probes are presented as
  exploratory analyses. MSI retains its complete composite score in the main
  construct family.
- PA5 and PA8 are reported as overlapping scoring versions; interpretation
  focuses on agreement and sensitivity across the two versions.

### Non-convergence handling

- When all optimizers fail for a construct, record `converged = false`, the
  failure reason and the optimizers tried.
- Keep the `material_id` random intercept in the primary specification.
- Downstream tables preserve the raw descriptive contrast and leave the
  model-adjusted field null for that construct.

### Random-effect and fixed-block interpretation

- The `material_id` random intercept captures the paired structure: the two judge
  models score the same material and share a material-level offset. Its variance
  is reported as `material_random_intercept_variance` together with the residual
  variance.
- `scenario_id` is a fixed block. Scenario baseline shifts are represented by
  fixed effects, and condition/model results are estimated within the eight
  selected contexts.

### Stability analysis with repeated runs

- When `repeat_index` has more than one level, add a nested repeat random effect
  for repeats within material.
- Report the repeat intraclass correlation as a stability diagnostic.

### Missing responses, parse failures and item completeness

- A missing material×model×repeat response is recorded in the quality summary,
  together with its effect on cell balance.
- A `parse_error` record retains the raw response and contributes to failure
  summaries.
- A construct score is computed when all member items are valid. The same response
  can still contribute to other constructs whose items are complete.

### Descriptive statistics and model inference

- Descriptive statistics summarize observed cells directly: means, SDs and raw
  contrasts.
- Model inference uses the mixed-effects specification, the `material_id` random
  intercept and `scenario_id` fixed block.
- Both layers are reported side by side so readers can compare the observed and
  model-adjusted patterns.
