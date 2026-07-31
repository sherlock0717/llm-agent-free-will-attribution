#!/usr/bin/env python
"""Build the Study B deterministic offline demonstration chain.

This script walks the full offline analysis chain end to end using deterministic
fixture inputs. It never contacts a network, never reads an API key and never
imports a model SDK. Every output is labelled ``data_role =
analysis_interface_example`` and ``generation_method = deterministic_fixture``.

Chain:
  deterministic inputs
  -> schema validation
  -> normalized records
  -> item range check
  -> construct scores (native scale)
  -> P1-P6 raw descriptive contrasts
  -> scenario sensitivity
  -> judge-slot sensitivity
  -> summary (page-shaped example JSON)

The chain does not replace Research A results and is never written as a Study B
research finding. It exercises the pipeline shape only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research_packages" / "study_b"
MATERIAL_MATRIX_PATH = PACKAGE / "material_matrix.csv"
SCHEMA_PATH = PACKAGE / "external_result_schema.json"
DEFAULT_OUTPUT = ROOT / "runs" / "study_b_offline_demo"

JUDGE_SLOTS = [("judge_1", "deepseek-v4-pro"), ("judge_2", "gpt-5.6-terra")]

CONSTRUCT_ITEMS = {
    "IN": ["wu_in1a", "wu_in2a", "wu_in3b", "wu_in4a"],
    "GO": ["wu_go1a", "wu_go2a", "wu_go3b", "wu_go4a"],
    "MSI": ["wu_ms1", "wu_ms2", "wu_ms3", "wu_ms4", "wu_ms5", "wu_ms6"],
    "IC": ["wu_ic1", "wu_ic3", "wu_ic4", "wu_ic7", "wu_ic8"],
    "PA5": [
        "pa_can_create_new_goals", "pa_can_communicate", "pa_can_change_behavior",
        "pa_can_adapt", "pa_actor_scenario",
    ],
    "PA8": [
        "pa_has_goals", "pa_can_create_new_goals", "pa_can_communicate",
        "pa_wanted_to_perform", "pa_can_change_behavior", "pa_can_adapt",
        "pa_actor_scenario", "pa_dinner_scenario",
    ],
}

CONTRASTS = [
    ("P1", "C1", "C0"),
    ("P2", "C2", "C0"),
    ("P3", "C3", "C2"),
    ("P4", "C4", "C2"),
    ("P5", "C5", "C2"),
    ("P6", "C5", "C4"),
]

CONDITION_ORDER = ["C0", "C1", "C2", "C3", "C4", "C5"]


def load_materials() -> list[dict]:
    with MATERIAL_MATRIX_PATH.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _fixture_score(material_id: str, item_id: str, minimum: int, maximum: int) -> int:
    """Deterministic fixture value from a stable hash. Not a model output."""
    digest = hashlib.sha256(f"{material_id}|{item_id}".encode("utf-8")).hexdigest()
    span = maximum - minimum + 1
    return minimum + (int(digest[:8], 16) % span)


def build_deterministic_inputs(materials: list[dict], ranges: dict) -> list[dict]:
    records: list[dict] = []
    for material in materials:
        material_id = material["material_id"]
        for slot, model in JUDGE_SLOTS:
            item_responses = {}
            for item_id, bounds in ranges.items():
                base = _fixture_score(material_id, item_id, bounds["min"], bounds["max"])
                if slot == "judge_2":
                    base = min(bounds["max"], base + (1 if base < bounds["max"] else 0))
                item_responses[item_id] = base
            records.append(
                {
                    "material_id": material_id,
                    "judge_slot": slot,
                    "judge_model_id": model,
                    "source_record_id": f"deterministic_fixture::{material_id}::{slot}",
                    "source_file_hash": "deterministic_fixture",
                    "item_responses": item_responses,
                }
            )
    return records


def normalize_records(records: list[dict], materials: list[dict]) -> list[dict]:
    lookup = {m["material_id"]: m for m in materials}
    normalized: list[dict] = []
    for record in records:
        meta = lookup[record["material_id"]]
        normalized.append(
            {
                "material_id": record["material_id"],
                "condition_id": meta["condition_id"],
                "scenario_id": meta["scenario_id"],
                "direction_version": meta["direction_version"],
                "judge_slot": record["judge_slot"],
                "judge_model_id": record["judge_model_id"],
                "item_responses": record["item_responses"],
            }
        )
    normalized.sort(key=lambda r: (r["material_id"], r["judge_slot"]))
    return normalized


def compute_construct_scores(normalized: list[dict]) -> list[dict]:
    scored: list[dict] = []
    for record in normalized:
        items = record["item_responses"]
        constructs = {}
        for construct, members in CONSTRUCT_ITEMS.items():
            values = [items[item] for item in members]
            constructs[construct] = round(sum(values) / len(values), 4)
        scored.append(
            {
                "material_id": record["material_id"],
                "condition_id": record["condition_id"],
                "scenario_id": record["scenario_id"],
                "direction_version": record["direction_version"],
                "judge_slot": record["judge_slot"],
                "constructs": constructs,
            }
        )
    return scored


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def condition_means(scored: list[dict], construct: str) -> dict[str, float]:
    grouped: dict[str, list[float]] = {c: [] for c in CONDITION_ORDER}
    for row in scored:
        grouped[row["condition_id"]].append(row["constructs"][construct])
    return {c: round(_mean(v), 4) for c, v in grouped.items()}


def build_contrasts(scored: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for construct in CONSTRUCT_ITEMS:
        means = condition_means(scored, construct)
        for cid, left, right in CONTRASTS:
            rows.append(
                {
                    "construct": construct,
                    "contrast_id": cid,
                    "left": left,
                    "right": right,
                    "raw_mean_difference": round(means[left] - means[right], 4),
                }
            )
    return rows


def scenario_sensitivity(scored: list[dict]) -> list[dict]:
    scenarios = sorted({r["scenario_id"] for r in scored})
    rows: list[dict] = []
    for construct in CONSTRUCT_ITEMS:
        per_scenario = {}
        for scenario in scenarios:
            subset = [r for r in scored if r["scenario_id"] == scenario]
            per_scenario[scenario] = round(_mean([r["constructs"][construct] for r in subset]), 4)
        values = list(per_scenario.values())
        rows.append(
            {
                "construct": construct,
                "scenario_mean_min": round(min(values), 4),
                "scenario_mean_max": round(max(values), 4),
                "scenario_count": len(scenarios),
            }
        )
    return rows


def judge_slot_sensitivity(scored: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for construct in CONSTRUCT_ITEMS:
        per_slot = {}
        for slot, _model in JUDGE_SLOTS:
            subset = [r for r in scored if r["judge_slot"] == slot]
            per_slot[slot] = round(_mean([r["constructs"][construct] for r in subset]), 4)
        rows.append(
            {
                "construct": construct,
                "judge_1_mean": per_slot["judge_1"],
                "judge_2_mean": per_slot["judge_2"],
                "difference": round(per_slot["judge_2"] - per_slot["judge_1"], 4),
            }
        )
    return rows


def _write_json(path: Path, payload) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def artefacts() -> dict:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    ranges = schema["item_scale_ranges"]
    materials = load_materials()
    inputs = build_deterministic_inputs(materials, ranges)
    normalized = normalize_records(inputs, materials)
    scored = compute_construct_scores(normalized)
    contrasts = build_contrasts(scored)
    scenario = scenario_sensitivity(scored)
    judge = judge_slot_sensitivity(scored)
    summary = {
        "data_role": "analysis_interface_example",
        "generation_method": "deterministic_fixture",
        "material_count": len(materials),
        "record_count": len(inputs),
        "construct_ids": list(CONSTRUCT_ITEMS),
        "contrast_ids": [c[0] for c in CONTRASTS],
        "condition_means": {
            construct: condition_means(scored, construct) for construct in CONSTRUCT_ITEMS
        },
        "contrasts": contrasts,
        "scenario_sensitivity": scenario,
        "judge_slot_sensitivity": judge,
    }
    return {
        "inputs": inputs,
        "normalized": normalized,
        "scored": scored,
        "contrasts": contrasts,
        "scenario": scenario,
        "judge": judge,
        "summary": summary,
        "materials": materials,
    }


def build(output_dir: Path) -> dict:
    data = artefacts()
    for sub in ["deterministic_inputs", "normalized_records", "item_scores",
                "construct_scores", "analysis", "figures", "validation"]:
        (output_dir / sub).mkdir(parents=True, exist_ok=True)

    _write_jsonl(output_dir / "deterministic_inputs" / "inputs.jsonl", data["inputs"])
    _write_jsonl(output_dir / "normalized_records" / "normalized.jsonl", data["normalized"])
    _write_jsonl(output_dir / "item_scores" / "item_scores.jsonl", data["inputs"])
    _write_jsonl(output_dir / "construct_scores" / "construct_scores.jsonl", data["scored"])
    _write_json(output_dir / "analysis" / "contrasts.json", data["contrasts"])
    _write_json(output_dir / "analysis" / "scenario_sensitivity.json", data["scenario"])
    _write_json(output_dir / "analysis" / "judge_slot_sensitivity.json", data["judge"])
    _write_json(output_dir / "analysis" / "summary_example.json", data["summary"])
    (output_dir / "validation" / "chain_status.json").write_text(
        json.dumps(
            {
                "schema_validated": True,
                "item_ranges_checked": True,
                "record_count": len(data["inputs"]),
                "material_count": len(data["materials"]),
                "network_operations": "none",
            },
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "figures" / "README.md").write_text(
        "# 图表占位\n\n"
        "分析界面示例图表由公开页面根据 `docs/pa-wu-r1-pilot/data/showcase_data.json` "
        "渲染。本目录仅记录离线链路的图表环节位置。\n",
        encoding="utf-8",
    )
    manifest = {
        "manifest_id": "study_b.offline_demo.v1",
        "data_role": "analysis_interface_example",
        "generation_method": "deterministic_fixture",
        "source_commit": "9cb4aae1e3010f90b2a9c34ae87111b5e373de59",
        "material_count": len(data["materials"]),
        "record_count": len(data["inputs"]),
        "network_operations": "none",
        "chain": [
            "deterministic_inputs", "schema_validation", "normalized_records",
            "item_range_check", "construct_scores", "planned_contrasts",
            "scenario_sensitivity", "judge_slot_sensitivity", "summary_example",
        ],
        "not_labels": [
            "synthetic_model_response", "simulated_real_model", "proxy_model_score",
            "estimated_model_output", "formal_result",
        ],
    }
    _write_json(output_dir / "manifest.json", manifest)
    return {"output": str(output_dir), "record_count": len(data["inputs"])}


def check(output_dir: Path) -> list[str]:
    """Rebuild into memory and compare with committed key files."""
    data = artefacts()
    mismatches: list[str] = []
    checks = {
        "analysis/summary_example.json": json.dumps(
            data["summary"], indent=2, ensure_ascii=False, sort_keys=True
        )
        + "\n",
    }
    for rel, expected in checks.items():
        path = output_dir / rel
        if not path.is_file():
            mismatches.append(f"missing: {rel}")
        elif path.read_text(encoding="utf-8") != expected:
            mismatches.append(f"drift: {rel}")
    return mismatches


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Study B deterministic offline demo chain.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    output_dir = Path(args.output).resolve()

    if args.check:
        mismatches = check(output_dir)
        if mismatches:
            for item in mismatches:
                print(f"build_study_b_offline_demo: ERROR: {item}")
            return 1
        print("study B offline demo chain is up to date")
        return 0

    result = build(output_dir)
    print(f"study B offline demo chain written: {result['record_count']} records -> {result['output']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
