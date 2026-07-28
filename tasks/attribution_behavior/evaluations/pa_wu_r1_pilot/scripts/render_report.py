"""Render the demo report and >=5 figures from the scored / analyzed demo data.

MACHINE-ONLY R1: the target subject is an AI system. There is NO ai/human
comparison. All figures carry the label "Synthetic demonstration data" and
describe no real model result, capability, ranking or empirical theory support.

Figures:
  1. six conditions x four primary constructs mean plot
  2. model-adjusted estimated-marginal contrast forest (P1..P6, primary)
  3. two judge-model construct profile plot (not a ranking)
  4. scenario x construct heatmap
  5. raw descriptive planned-contrast forest (P1..P6, primary)
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib import font_manager  # noqa: E402


def _configure_chinese_font() -> str:
    """Select an installed CJK font for figure text. No font file is bundled or
    committed. If none is available we stop rather than emit tofu/garbled text."""
    preferred = [
        "Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Noto Sans CJK",
        "Source Han Sans SC", "Microsoft JhengHei", "SimSun",
    ]
    installed = {f.name for f in font_manager.fontManager.ttflist}
    chosen = next((name for name in preferred if name in installed), None)
    if chosen is None:
        raise SystemExit(
            "No installed CJK font found (tried: " + ", ".join(preferred) + "). "
            "Refusing to render garbled figures. Install a Chinese font first."
        )
    plt.rcParams["font.sans-serif"] = [chosen] + list(plt.rcParams.get("font.sans-serif", []))
    plt.rcParams["axes.unicode_minus"] = False
    return chosen


# Chinese display labels for figures (display text only; ids/data unchanged).
SCENARIO_LABELS_ZH = {
    "s1_scheduling": "会议排期",
    "s2_customer_issue": "客户问题处理",
    "s3_study_plan": "学习计划",
    "s4_routing": "路线与物流",
    "s5_task_allocation": "团队任务分配",
    "s6_content_recommendation": "内容推荐",
    "s7_game_strategy": "游戏策略",
    "s8_energy_plan": "节能方案",
}
SYNTH_ZH = "合成演示数据"

PKG_DIR = Path(__file__).resolve().parent.parent
CONSTRUCT_SCORES = PKG_DIR / "outputs" / "demo_construct_scores.csv"
DESCRIPTIVES = PKG_DIR / "outputs" / "demo_descriptives.csv"
CONTRASTS = PKG_DIR / "outputs" / "demo_contrasts.csv"
MODEL_CONTRASTS = PKG_DIR / "outputs" / "demo_model_contrasts.csv"
MODEL_FIT = PKG_DIR / "outputs" / "demo_model_fit_summary.csv"
QUALITY = PKG_DIR / "outputs" / "demo_quality_summary.json"
FIG_DIR = PKG_DIR / "outputs" / "figures"
REPORT_OUT = PKG_DIR / "reports" / "demo_report.md"
SHOWCASE_OUT = PKG_DIR / "outputs" / "showcase_data.json"

# static showcase site (docs/pa-wu-r1-pilot). Kept in sync so the page always
# reads the freshly regenerated data and figures.
REPO_ROOT = PKG_DIR.parents[3]
DOCS_DIR = REPO_ROOT / "docs" / "pa-wu-r1-pilot"
DOCS_DATA = DOCS_DIR / "data" / "showcase_data.json"
DOCS_FIGS = DOCS_DIR / "assets" / "figures"

CONDITIONS = ["C0", "C1", "C2", "C3", "C4", "C5"]
PRIMARY = ["IN", "GO", "MSI", "IC"]
ALL_CONSTRUCTS = ["IN", "GO", "MSI", "IC", "PA5", "PA8"]
MODELS = ["deepseek-v4-pro", "gpt-5.6-terra"]
SYNTH = "Synthetic demonstration data"

# --- controlled figure metadata (display labels + theoretical scale bounds) ---
# Chinese construct names for panel titles (display only; ids/data unchanged).
CONSTRUCT_LABELS_ZH = {
    "IN": "知觉独立性",
    "GO": "目标导向性",
    "MSI": "心理状态推断",
    "IC": "影响能力",
    "PA5": "感知能动性 PA5",
    "PA8": "感知能动性 PA8",
}

# Theoretical native-scale bounds per construct. Used to fix each panel's own
# axis and (fig4 only) to map to a 0–1 display position. These are the scale
# boundaries, NOT sample min/max, and never enter statistical inference.
NATIVE_SCALE_BOUNDS = {
    "IN": (1, 7),
    "GO": (1, 7),
    "MSI": (1, 5),
    "IC": (1, 7),
    "PA5": (1, 5),
    "PA8": (1, 5),
}

# Contrast short labels for forest-panel y-axes. Must match analysis_plan.md.
CONTRAST_LABELS_ZH = {
    "P1": "P1｜C1−C0 备选方案",
    "P2": "P2｜C2−C0 明确理由",
    "P3": "P3｜C3−C2 加入反馈",
    "P4": "P4｜C4−C2 反馈并维持",
    "P5": "P5｜C5−C2 反馈并改变",
    "P6": "P6｜C5−C4 改变与维持",
}

# Ordered P-ids for forest panels.
CONTRAST_ORDER = ["P1", "P2", "P3", "P4", "P5", "P6"]

# Short model tick labels for fig3 x-axis (full ids go in the shared legend).
MODEL_SHORT = {"deepseek-v4-pro": "DS", "gpt-5.6-terra": "GPT"}

# Neutral point colours / markers (no win/lose semantics).
NEUTRAL_POINT = "#1f66d1"     # neutral blue
NEUTRAL_LINE = "#7a869a"      # neutral grey
MODEL_MARKERS = {"deepseek-v4-pro": "o", "gpt-5.6-terra": "^"}
MODEL_COLORS = {"deepseek-v4-pro": "#1f66d1", "gpt-5.6-terra": "#6b57c7"}  # blue / purple


def _panel_title(construct: str) -> str:
    return f"{CONSTRUCT_LABELS_ZH.get(construct, construct)}（{construct}）"


def _mean_by(df: pd.DataFrame, *cols: str) -> pd.DataFrame:
    valid = df[df["construct_score"].notna()]
    return valid.groupby(list(cols))["construct_score"].mean().reset_index()


def fig1_condition_construct(df: pd.DataFrame) -> Path:
    """2×2 faceted line plot, one primary construct per panel, each panel fixed
    to its own theoretical native scale so cross-construct absolute heights are
    never comparable."""
    m = _mean_by(df, "construct", "condition_id")
    fig, axes = plt.subplots(2, 2, figsize=(9, 7))
    for ax, construct in zip(axes.flat, PRIMARY):
        sub = m[m["construct"] == construct].set_index("condition_id").reindex(CONDITIONS)
        ax.plot(CONDITIONS, sub["construct_score"].values,
                marker="o", color=NEUTRAL_POINT, linewidth=2)
        lo, hi = NATIVE_SCALE_BOUNDS[construct]
        ax.set_ylim(lo, hi)
        ax.set_title(f"{_panel_title(construct)}｜量尺 {lo}—{hi}", fontsize=11)
        ax.set_xlabel("实验条件 C0—C5", fontsize=9)
        ax.set_ylabel(f"原量尺 {lo}—{hi}", fontsize=9)
        ax.grid(True, axis="y", color="#e6edf6", linewidth=0.8)
    fig.suptitle(f"六个实验条件下的主要构念均值\n[{SYNTH_ZH}｜各面板使用自身原量尺]",
                 fontsize=13)
    fig.text(0.5, 0.01,
             "不同面板的纵轴量尺可能不同，不比较跨构念绝对高度。",
             ha="center", fontsize=9, color="#5d6b7d")
    fig.tight_layout(rect=(0, 0.04, 1, 0.93))
    out = FIG_DIR / "fig1_condition_construct_means.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def _forest_panels(data_by_construct, xlabel: str, suptitle: str, note: str,
                   out_name: str) -> Path:
    """Shared 2×2 forest layout: one primary construct per panel, own x-axis,
    x symmetric around 0, neutral colours, 0 reference line."""
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    for ax, construct in zip(axes.flat, PRIMARY):
        rows = data_by_construct.get(construct, {})
        ys = list(range(len(CONTRAST_ORDER)))
        max_abs = 0.0
        for i, pid in enumerate(CONTRAST_ORDER):
            entry = rows.get(pid)
            if not entry:
                continue
            est, lo, hi = entry
            if lo is not None and hi is not None:
                ax.plot([lo, hi], [i, i], color=NEUTRAL_LINE, linewidth=1.6)
                max_abs = max(max_abs, abs(lo), abs(hi))
            if est is not None:
                ax.plot(est, i, marker="o", color=NEUTRAL_POINT, markersize=6)
                max_abs = max(max_abs, abs(est))
        ax.axvline(0.0, color="#182230", linewidth=0.9, linestyle="--")
        ax.set_yticks(ys)
        ax.set_yticklabels([CONTRAST_LABELS_ZH[p] for p in CONTRAST_ORDER], fontsize=8)
        ax.invert_yaxis()
        span = (max_abs * 1.15) if max_abs > 0 else 1.0
        ax.set_xlim(-span, span)
        ax.set_title(_panel_title(construct), fontsize=11)
        ax.set_xlabel(xlabel, fontsize=9)
        ax.grid(True, axis="x", color="#e6edf6", linewidth=0.8)
    fig.suptitle(suptitle, fontsize=13)
    fig.text(0.5, 0.01, note, ha="center", fontsize=9, color="#5d6b7d")
    fig.tight_layout(rect=(0, 0.04, 1, 0.92))
    out = FIG_DIR / out_name
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def fig2_model_adjusted_forest(mcons: pd.DataFrame) -> Path:
    data: dict = {}
    for r in mcons[mcons["construct"].isin(PRIMARY)].itertuples():
        est = None if pd.isna(r.estimate) else float(r.estimate)
        lo = None if pd.isna(r.ci95_low) else float(r.ci95_low)
        hi = None if pd.isna(r.ci95_high) else float(r.ci95_high)
        data.setdefault(r.construct, {})[r.contrast_id] = (est, lo, hi)
    return _forest_panels(
        data,
        xlabel="模型调整后差值（该构念原量尺）",
        suptitle=f"模型调整后的预设对比\n[{SYNTH_ZH}｜按构念分面]",
        note="仅在同一构念内部读取方向、幅度与不确定性。",
        out_name="fig2_model_adjusted_contrasts.png")


def fig3_model_profiles(df: pd.DataFrame) -> Path:
    """2×3 small multiples, one construct per panel, two judge-model configuration
    means as separate points on that construct's own native scale. No cross-
    construct profile line; neutral markers; descriptive only, no ranking."""
    m = _mean_by(df, "construct", "judge_model_id")
    fig, axes = plt.subplots(2, 3, figsize=(11, 7))
    for ax, construct in zip(axes.flat, ALL_CONSTRUCTS):
        sub = m[m["construct"] == construct].set_index("judge_model_id")
        lo, hi = NATIVE_SCALE_BOUNDS[construct]
        for j, model in enumerate(MODELS):
            val = sub["construct_score"].get(model)
            if val is None or pd.isna(val):
                continue
            ax.plot(j, float(val), marker=MODEL_MARKERS[model],
                    color=MODEL_COLORS[model], markersize=11, linestyle="none")
        ax.set_ylim(lo, hi)
        ax.set_xlim(-0.6, len(MODELS) - 0.4)
        ax.set_xticks(range(len(MODELS)))
        ax.set_xticklabels([MODEL_SHORT[mo] for mo in MODELS], fontsize=9)
        ax.set_title(f"{_panel_title(construct)}｜量尺 {lo}—{hi}", fontsize=10)
        ax.set_ylabel(f"原量尺 {lo}—{hi}", fontsize=8)
        ax.grid(True, axis="y", color="#e6edf6", linewidth=0.8)
    handles = [
        plt.Line2D([0], [0], marker=MODEL_MARKERS[mo], color=MODEL_COLORS[mo],
                   linestyle="none", markersize=10, label=mo)
        for mo in MODELS
    ]
    fig.legend(handles=handles, title="评判模型配置",
               loc="lower center", ncol=2, fontsize=9)
    fig.suptitle(f"两个评判模型配置的构念均值\n[{SYNTH_ZH}｜描述性展示，不用于排名]",
                 fontsize=13)
    fig.tight_layout(rect=(0, 0.07, 1, 0.92))
    out = FIG_DIR / "fig3_model_profiles.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def fig4_scenario_heatmap(df: pd.DataFrame) -> Path:
    """Heatmap where each column is mapped to a 0–1 within-scale position using
    THEORETICAL scale bounds (not sample min/max). Display transform only; formal
    inference keeps native scales."""
    m = _mean_by(df, "scenario_id", "construct")
    pivot = m.pivot(index="scenario_id", columns="construct", values="construct_score")
    pivot = pivot.reindex(columns=ALL_CONSTRUCTS)

    display = pivot.copy()
    for construct in ALL_CONSTRUCTS:
        lo, hi = NATIVE_SCALE_BOUNDS[construct]
        # display_value = (score - scale_min) / (scale_max - scale_min), clipped 0–1
        display[construct] = ((pivot[construct] - lo) / (hi - lo)).clip(0.0, 1.0)

    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    im = ax.imshow(display.values, aspect="auto", cmap="cividis", vmin=0.0, vmax=1.0)
    ax.set_xticks(range(len(display.columns)))
    ax.set_xticklabels([f"{CONSTRUCT_LABELS_ZH.get(c, c)}\n({c})" for c in display.columns],
                       fontsize=9)
    ax.set_yticks(range(len(display.index)))
    ax.set_yticklabels([SCENARIO_LABELS_ZH.get(sid, sid) for sid in display.index], fontsize=9)
    for i in range(display.shape[0]):
        for j in range(display.shape[1]):
            val = display.values[i, j]
            if pd.notna(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        fontsize=8, color="#ffffff" if val < 0.55 else "#182230")
    ax.set_title(f"场景与构念的量尺内评分位置\n[{SYNTH_ZH}]", fontsize=13)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("量尺内位置（0—1，仅展示）")
    fig.text(0.5, 0.01,
             "每列根据该构念理论量尺转换为0—1；该转换不进入正式统计推断。",
             ha="center", fontsize=9, color="#5d6b7d")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    out = FIG_DIR / "fig4_scenario_construct_heatmap.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def fig5_contrast_forest(contrasts: pd.DataFrame) -> Path:
    sub = contrasts[(contrasts["split"] == "overall") & (contrasts["construct"].isin(PRIMARY))]
    data: dict = {}
    for r in sub.itertuples():
        d = None if pd.isna(r.difference) else float(r.difference)
        lo = None if pd.isna(r.ci95_low) else float(r.ci95_low)
        hi = None if pd.isna(r.ci95_high) else float(r.ci95_high)
        data.setdefault(r.construct, {})[r.contrast_id] = (d, lo, hi)
    return _forest_panels(
        data,
        xlabel="直接均值差（该构念原量尺）",
        suptitle=f"直接描述性预设对比\n[{SYNTH_ZH}｜按构念分面]",
        note="不同构念之间不比较绝对差值大小。",
        out_name="fig5_contrast_forest.png")


def _synth_banner() -> str:
    return f"> **{SYNTH}.** Not real model results; no model capability, no model " \
           "ranking, no empirical theory support."


def render_report(figs: list[Path]) -> None:
    desc = pd.read_csv(DESCRIPTIVES)
    mcons = pd.read_csv(MODEL_CONTRASTS)
    mfit = pd.read_csv(MODEL_FIT)
    quality = json.loads(QUALITY.read_text(encoding="utf-8"))
    cmean = desc.groupby(["construct", "condition_id"])["mean"].mean().reset_index()

    L: list[str] = []
    L.append("# PA—Wu R1 Pilot — Demo Report (machine-only)")
    L.append("")
    L.append(_synth_banner())
    L.append("")
    L.append("> **Target subject: machine-only.** The R1 pilot studies attribution to "
             "an AI system only. There is **no** ai/human comparison "
             "(see `identity_scope_decision.md`).")
    L.append("")

    # 1
    L.append("## 1. Research question")
    L.append("How do decision-process cues (D) and post-decision behavior (U) shape a "
             "large-language-model judge's attribution of agency, mental states and "
             "influential capacity to an **AI system** acting as the subject? Free will "
             "is only one MSI item (`wu_ms3`, exploratory), never the sole construct or a total.")
    L.append("")
    # 2
    L.append("## 2. Construct framework")
    L.append("Primary: IN (Perceptual Independence, 1–7), GO (Goal Orientation, 1–7), "
             "MSI (Mental-State Inference, 1–5), IC (Influential Capacity, 1–7). "
             "Supplementary: PA5, PA8 (Perceived Agency, 1–5). No cross-scale total. "
             "The four primary Wu & Shen 2026 constructs use machine-specific original items.")
    L.append("")
    # 3
    L.append("## 3. Six-condition design")
    L.append("C0 D0-U0; C1 D1-U0; C2 D2-U0; C3 D2-U1; C4 D2-U2; C5 D2-U3. "
             "D0 adds no process cue; D1 adds only explicit alternatives information; "
             "D2 adds only the explicit stated reason. Six-level condition factor; the "
             "pilot does NOT estimate a full D×U interaction.")
    L.append("")
    # 4
    L.append("## 4. Material coverage")
    bal = quality["balance"]
    L.append(f"- Total materials: {quality['n_materials']} (6 conditions × 8 scenarios × "
             "2 directions × 1 machine identity).")
    L.append(f"- Per condition: {bal['per_condition']}")
    L.append(f"- Per direction: {bal['per_direction']}; per scenario: {bal['per_scenario']}")
    L.append(f"- Demo responses: {quality['n_responses']} across "
             f"{quality['n_judge_models']} judge models (each model scores the same 96 materials).")
    L.append("")
    # 5
    L.append("## 5. Synthetic-data note")
    L.append(_synth_banner())
    L.append("Demo responses are deterministic (fixed seed) with a few baked-in condition "
             "differences purely to exercise scoring/analysis/figures. They imitate no "
             "real DeepSeek or GPT behavior.")
    L.append("")
    # 6
    L.append("## 6. Descriptive results — condition × primary construct means")
    L.append("")
    L.append("| construct | " + " | ".join(CONDITIONS) + " |")
    L.append("|" + "---|" * (len(CONDITIONS) + 1))
    for construct in PRIMARY:
        row = [construct]
        for cond in CONDITIONS:
            v = cmean[(cmean["construct"] == construct) & (cmean["condition_id"] == cond)]["mean"]
            row.append(f"{v.values[0]:.2f}" if len(v) else "-")
        L.append("| " + " | ".join(row) + " |")
    L.append("")
    # 7
    L.append("## 7. Mixed-effects model fit")
    L.append("")
    L.append("Model per construct: "
             "`construct_score ~ C(condition_id)*C(judge_model_id) + C(direction_version) "
             "+ C(scenario_id)`, **random intercept `material_id`** (each material is "
             "scored by both judge models, so its two responses are paired; scenarios "
             "are fixed blocks).")
    L.append("")
    L.append("| construct | converged | optimizer_used | material_var | residual_var | attempts |")
    L.append("|---|---|---|---|---|---|")
    for r in mfit.itertuples():
        L.append(f"| {r.construct} | {r.converged} | {r.optimizer_used or '-'} | "
                 f"{r.material_random_intercept_variance} | {r.residual_variance} | "
                 f"{r.optimizer_attempts} |")
    L.append("")
    # captured warnings
    warns = [(r.construct, r.captured_warnings) for r in mfit.itertuples() if str(r.captured_warnings)]
    if warns:
        L.append("Captured convergence/Hessian warnings (not discarded):")
        for c, w in warns:
            L.append(f"- **{c}**: {w}")
        L.append("")
    # 8
    L.append("## 8. Estimated marginal contrasts P1..P6 (model-adjusted, Holm within construct)")
    L.append("")
    L.append("Contrasts are computed on the balanced design grid (both judge models × A/B × "
             "8 scenarios); `estimate = Lβ`, `Var = L·Cov(β)·Lᵀ`. Holm is applied within each "
             "construct's six contrasts.")
    L.append("")
    L.append("| construct | id | contrast | estimate | SE | p | p(Holm) | raw |")
    L.append("|---|---|---|---|---|---|---|---|")
    for r in mcons[mcons["construct"].isin(PRIMARY)].itertuples():
        est = "-" if pd.isna(r.estimate) else f"{r.estimate:+.3f}"
        se = "-" if pd.isna(r.standard_error) else f"{r.standard_error:.3f}"
        p = "-" if pd.isna(r.p_value) else f"{r.p_value:.3f}"
        ph = "-" if pd.isna(r.p_value_holm) else f"{r.p_value_holm:.3f}"
        L.append(f"| {r.construct} | {r.contrast_id} | {r.contrast} | {est} | {se} | "
                 f"{p} | {ph} | {r.raw_descriptive_contrast:+.3f} |")
    L.append("")
    # 9
    L.append("## 9. Judge-model differences (descriptive, synthetic; NOT a ranking)")
    L.append("")
    mm = desc.groupby(["construct", "judge_model_id"])["mean"].mean().reset_index()
    L.append("| construct | deepseek-v4-pro | gpt-5.6-terra |")
    L.append("|---|---|---|")
    for construct in ALL_CONSTRUCTS:
        d = mm[(mm["construct"] == construct) & (mm["judge_model_id"] == "deepseek-v4-pro")]["mean"]
        g = mm[(mm["construct"] == construct) & (mm["judge_model_id"] == "gpt-5.6-terra")]["mean"]
        if len(d) and len(g):
            L.append(f"| {construct} | {d.values[0]:.2f} | {g.values[0]:.2f} |")
    L.append("")
    # 10
    L.append("## 10. Scenario heterogeneity (synthetic)")
    L.append("")
    L.append("| construct | scenario-mean min | max | range |")
    L.append("|---|---|---|---|")
    for construct, h in quality["scenario_heterogeneity"].items():
        L.append(f"| {construct} | {h['scenario_mean_min']} | {h['scenario_mean_max']} | "
                 f"{h['scenario_mean_range']} |")
    L.append("")
    # figures
    L.append("### Figures (synthetic)")
    L.append("")
    L.append("- Figures 1, 2, 3 and 5 are **faceted per construct** and each panel uses "
             "that construct's own **native scale**; cross-construct absolute heights / "
             "differences are not comparable.")
    L.append("- Figure 4 maps each column to a **0–1 within-scale position using the "
             "theoretical scale bounds** (display only), not sample min/max.")
    L.append("- Formal inference always uses the native scales.")
    L.append("")
    for f in figs:
        L.append(f"- `{f.relative_to(PKG_DIR).as_posix()}`")
    L.append("")
    # 11
    L.append("## 11. Interpretation boundaries")
    L.append("- **Machine-only**: attribution to an AI system; no ai/human comparison.")
    L.append("- Native-scale inference is primary; 0–1 standardization is display-only.")
    L.append("- No missing-value imputation; a construct requires all its items valid.")
    L.append("- Free-will item (`wu_ms3`) is exploratory; never a construct or total.")
    L.append("- Pilot uses a six-level condition factor; no full D×U causal interaction.")
    L.append("- No model ranking; no capability claim; no empirical theory support.")
    L.append("- Demo significance/effect values are pipeline checks, not findings.")
    L.append("")
    # 12
    L.append("## 12. Real-data replacement procedure")
    L.append("1. Run the authorized dual-model preflight to green (all gates).")
    L.append("2. Execute the real run producing records per `result_schema.json` "
             "(no `synthetic_demo` flag), machine-only, 96 materials × 2 models.")
    L.append("3. Replace `demo/demo_responses.jsonl` with the real responses.")
    L.append("4. Re-run `score_results.py` → `analyze_pilot.py` → `fit_mixed_models.py` "
             "→ `render_report.py` unchanged.")
    L.append("5. Report the Holm-adjusted planned contrasts within each construct family.")
    L.append("6. Only then interpret contrasts as findings; remove the synthetic banner.")
    L.append("")
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text("\n".join(L), encoding="utf-8")


def build_showcase_data(figs: list[Path]) -> None:
    desc = pd.read_csv(DESCRIPTIVES)
    mcons = pd.read_csv(MODEL_CONTRASTS)
    mfit = pd.read_csv(MODEL_FIT)
    raw_cons = pd.read_csv(CONTRASTS)
    quality = json.loads(QUALITY.read_text(encoding="utf-8"))
    with (PKG_DIR / "stimuli.jsonl").open(encoding="utf-8") as fh:
        stimuli = [json.loads(line) for line in fh if line.strip()]

    def _means(by: str) -> dict:
        g = desc.groupby(["construct", by])["mean"].mean().reset_index()
        out: dict = {}
        for r in g.itertuples():
            out.setdefault(r.construct, {})[getattr(r, by)] = round(float(r.mean), 4)
        return out

    # per-scenario materials for the scenario browser (machine-only cells).
    scenario_materials: dict = {}
    for m in stimuli:
        scenario_materials.setdefault(m["scenario_id"], []).append({
            "material_id": m["material_id"],
            "condition_id": m["condition_id"],
            "direction_version": m["direction_version"],
            "complete_stimulus_text": m["complete_stimulus_text"],
        })
    for sid in scenario_materials:
        scenario_materials[sid].sort(key=lambda r: (r["condition_id"], r["direction_version"]))

    data = {
        "data_status": "synthetic_demo",
        "target_subject": "machine",
        "project_summary": {
            "research_question": "How decision-process cues (D) and post-decision "
            "behavior (U) shape an LLM judge's attribution of agency, mental states "
            "and influential capacity to an AI system acting as the subject.",
            "free_will_role": "single exploratory MSI item (wu_ms3); never sole "
            "construct or total",
            "stage": "pilot",
            "identity_scope": "machine-only; no ai/human comparison in R1",
            "note": "All numbers are synthetic demonstration data.",
        },
        "constructs": {
            "primary": ["IN", "GO", "MSI", "IC"],
            "supplementary": ["PA5", "PA8"],
            "native_scales": {"IN": "1-7", "GO": "1-7", "MSI": "1-5", "IC": "1-7",
                              "PA5": "1-5", "PA8": "1-5"},
            "names": {"IN": "Perceptual Independence", "GO": "Goal Orientation",
                      "MSI": "Mental-State Inference", "IC": "Influential Capacity",
                      "PA5": "Perceived Agency (5-item)", "PA8": "Perceived Agency (8-item)"},
        },
        "conditions": {
            "C0": "D0-U0 direct decision",
            "C1": "D1-U0 explicit alternatives",
            "C2": "D2-U0 explicit reason",
            "C3": "D2-U1 reason + feedback",
            "C4": "D2-U2 feedback + keep",
            "C5": "D2-U3 feedback + change",
        },
        "judge_models": [
            {"id": "deepseek-v4-pro", "provider": "deepseek",
             "role": "co-primary judge model (configuration selected; empirical "
             "performance not evaluated)"},
            {"id": "gpt-5.6-terra", "provider": "openai",
             "role": "co-primary judge model (configuration selected; empirical "
             "performance not evaluated)"},
        ],
        "scenarios": sorted(quality["balance"]["per_scenario"].keys()),
        "scenario_materials": scenario_materials,
        "material_balance": quality["balance"],
        "descriptive_results": {
            "condition_means": _means("condition_id"),
            "model_means": _means("judge_model_id"),
        },
        "raw_planned_contrasts": raw_cons[raw_cons["split"] == "overall"].to_dict(orient="records"),
        "model_adjusted_results": {
            "fit_summary": mfit.to_dict(orient="records"),
            "contrasts": mcons.to_dict(orient="records"),
        },
        "quality_summary": {
            "n_materials": quality["n_materials"],
            "n_responses": quality["n_responses"],
            "item_valid_rate": quality["item_valid_rate"],
            "construct_scored_rate": quality["construct_scored_rate"],
            "scenario_heterogeneity": quality["scenario_heterogeneity"],
        },
        "method_boundaries": [
            "Machine-only target subject; no ai/human comparison in R1.",
            "Six-level condition factor; not a full D×U causal interaction.",
            "Native-scale inference; 0–1 standardization is display-only.",
            "No missing-value imputation; construct needs all items valid.",
            "Free-will item wu_ms3 is exploratory, never a construct or total.",
            "No model ranking; judge-model differences are descriptive only.",
        ],
        "real_data_replacement": [
            "Run authorized dual-model preflight to green.",
            "Execute real run (machine-only, 96 materials × 2 models), records per result_schema.json.",
            "Replace demo/demo_responses.jsonl with real responses.",
            "Re-run score → analyze → fit_mixed_models → render_report unchanged.",
            "Report Holm-adjusted planned contrasts within each construct family.",
            "Remove the synthetic banner only after the above.",
        ],
        "github_entry": {
            "repo_path": "tasks/attribution_behavior/evaluations/pa_wu_r1_pilot",
            "outputs": "outputs/", "report": "reports/demo_report.md",
        },
        "figure_paths": [f.name for f in figs],
    }
    SHOWCASE_OUT.parent.mkdir(parents=True, exist_ok=True)
    SHOWCASE_OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _sync_docs(figs: list[Path]) -> None:
    """Copy the freshly built showcase data and figures into the static site so
    docs/pa-wu-r1-pilot always reflects the current pipeline run."""
    import shutil
    if not DOCS_DIR.exists():
        return
    DOCS_DATA.parent.mkdir(parents=True, exist_ok=True)
    DOCS_FIGS.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SHOWCASE_OUT, DOCS_DATA)
    # remove stale figures then copy the current five.
    for old in DOCS_FIGS.glob("*.png"):
        old.unlink()
    for f in figs:
        shutil.copyfile(f, DOCS_FIGS / f.name)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    font = _configure_chinese_font()
    print(f"using CJK font: {font}")
    df = pd.read_csv(CONSTRUCT_SCORES)
    contrasts = pd.read_csv(CONTRASTS)
    mcons = pd.read_csv(MODEL_CONTRASTS)
    figs = [
        fig1_condition_construct(df),
        fig2_model_adjusted_forest(mcons),
        fig3_model_profiles(df),
        fig4_scenario_heatmap(df),
        fig5_contrast_forest(contrasts),
    ]
    render_report(figs)
    build_showcase_data(figs)
    _sync_docs(figs)
    for f in figs:
        print(f"wrote figure -> {f.relative_to(PKG_DIR.parent)}")
    print(f"wrote report -> {REPORT_OUT.relative_to(PKG_DIR.parent)}")
    print(f"wrote showcase data -> {SHOWCASE_OUT.relative_to(PKG_DIR.parent)}")
    print(f"synced static site -> {DOCS_DIR.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
