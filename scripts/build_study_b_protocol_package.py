#!/usr/bin/env python
"""Build the Study B offline research package.

This script freezes the Study B offline research protocol into a set of
deterministic, network-free artefacts under ``research_packages/study_b/``:

* ``protocol_manifest.yaml`` — protocol scope, counts, construct/contrast ids
  and source paths (no API/token/cost fields).
* ``asset_hashes.json`` — SHA-256 hashes of frozen research assets.
* ``material_matrix.csv`` — one row per Study B material (96 rows).
* ``scoring_matrix_template.csv`` — one row per material × judge slot
  (192 rows); a *template* with no real scores.

The script never contacts a network, never reads API keys and never generates
model scores. It is fully deterministic: the same repository state produces
byte-identical output. ``--check`` compares freshly built content with the
committed files and fails on any drift without modifying tracked files.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "tasks" / "attribution_behavior" / "evaluations" / "pa_wu_r1_pilot"
P0 = ROOT / "tasks" / "attribution_behavior" / "measurement_candidates" / "pa_wu_p0"
PACKAGE = ROOT / "research_packages" / "study_b"

SOURCE_COMMIT = "9cb4aae1e3010f90b2a9c34ae87111b5e373de59"

# Judge models are retained as analysis-protocol metadata only. They are never
# used to originate a call in this package.
JUDGE_MODELS = ["deepseek-v4-pro", "gpt-5.6-terra"]

CONSTRUCT_IDS = ["IN", "GO", "MSI", "IC"]
SUPPLEMENTARY_SCORE_IDS = ["PA5", "PA8"]
CONTRAST_IDS = ["P1", "P2", "P3", "P4", "P5", "P6"]

ANALYSIS_FORMULA = (
    "construct_score ~ C(condition_id) * C(judge_model_id) "
    "+ C(direction_version) + C(scenario_id); random intercept: material_id"
)

# Frozen research assets. Paths are relative to the repository root and are
# sorted deterministically before hashing.
HASH_TARGETS = [
    "tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/stimuli.jsonl",
    "tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/stimulus_book.md",
    "tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/condition_matrix.csv",
    "tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/scoring_spec.yaml",
    "tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/study_protocol.yaml",
    "tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/analysis_plan.md",
    "tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/result_schema.json",
    "tasks/attribution_behavior/measurement_candidates/pa_wu_p0/items_wu_shen_2026.yaml",
    "tasks/attribution_behavior/measurement_candidates/pa_wu_p0/items_pa_2024.yaml",
    "tasks/attribution_behavior/measurement_candidates/pa_wu_p0/forms.yaml",
    "docs/pa-wu-r1-pilot/data/showcase_data.json",
    "scripts/build_showcase_data.py",
    "scripts/build_study_b_protocol_package.py",
]

MATERIAL_MATRIX_COLUMNS = [
    "material_id",
    "condition_id",
    "scenario_id",
    "direction_version",
    "decision_information_level",
    "feedback_state",
    "second_decision_state",
    "source_path",
    "content_sha256",
]

SCORING_TEMPLATE_COLUMNS = [
    "record_id",
    "material_id",
    "judge_slot",
    "judge_model_id",
    "response_source",
    "response_file",
    "imported_at",
    "validation_status",
    "parse_status",
    "item_score_status",
    "notes",
]

CONDITION_META = {
    "C0": {"decision": "direct_decision", "feedback": "none", "second_decision": "none"},
    "C1": {"decision": "shows_alternatives", "feedback": "none", "second_decision": "none"},
    "C2": {"decision": "shows_reasons", "feedback": "none", "second_decision": "none"},
    "C3": {"decision": "shows_reasons", "feedback": "given", "second_decision": "none"},
    "C4": {"decision": "shows_reasons", "feedback": "given", "second_decision": "keep"},
    "C5": {"decision": "shows_reasons", "feedback": "given", "second_decision": "change"},
}

MATERIAL_SOURCE_PATH = (
    "tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/stimuli.jsonl"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text_normalized(text: str) -> str:
    """Hash normalized text: strip a UTF-8 BOM and normalize line endings."""
    if text.startswith("\ufeff"):
        text = text[1:]
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return sha256_bytes(normalized.encode("utf-8"))


def load_materials() -> list[dict]:
    path = ROOT / MATERIAL_SOURCE_PATH
    materials: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            materials.append(json.loads(line))
    materials.sort(key=lambda row: row["material_id"])
    return materials


def build_material_matrix_rows(materials: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for material in materials:
        condition = material["condition_id"]
        meta = CONDITION_META[condition]
        canonical = json.dumps(material, sort_keys=True, ensure_ascii=False)
        rows.append(
            {
                "material_id": material["material_id"],
                "condition_id": condition,
                "scenario_id": material["scenario_id"],
                "direction_version": material["direction_version"],
                "decision_information_level": meta["decision"],
                "feedback_state": meta["feedback"],
                "second_decision_state": meta["second_decision"],
                "source_path": MATERIAL_SOURCE_PATH,
                "content_sha256": sha256_text_normalized(canonical),
            }
        )
    return rows


def build_scoring_template_rows(materials: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for material in materials:
        for slot_index, judge_model in enumerate(JUDGE_MODELS, start=1):
            judge_slot = f"judge_{slot_index}"
            rows.append(
                {
                    "record_id": f"{material['material_id']}__{judge_slot}",
                    "material_id": material["material_id"],
                    "judge_slot": judge_slot,
                    "judge_model_id": judge_model,
                    "response_source": "external_offline_file",
                    "response_file": "",
                    "imported_at": "",
                    "validation_status": "awaiting_input",
                    "parse_status": "not_started",
                    "item_score_status": "not_started",
                    "notes": "",
                }
            )
    return rows


def rows_to_csv(columns: list[str], rows: list[dict]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


def build_asset_hashes() -> str:
    entries = {}
    for rel in sorted(HASH_TARGETS):
        path = ROOT / rel
        entries[rel] = {
            "sha256": sha256_bytes(path.read_bytes()),
            "normalized_sha256": sha256_text_normalized(path.read_text(encoding="utf-8")),
        }
    materials = load_materials()
    material_content = {
        material["material_id"]: sha256_text_normalized(
            json.dumps(material, sort_keys=True, ensure_ascii=False)
        )
        for material in materials
    }
    payload = {
        "asset_hashes_id": "study_b.asset_hashes.v1",
        "source_commit": SOURCE_COMMIT,
        "hash_algorithm": "sha256",
        "file_count": len(entries),
        "material_count": len(material_content),
        "files": entries,
        "material_content_sha256": dict(sorted(material_content.items())),
    }
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def build_protocol_manifest(materials: list[dict]) -> str:
    scenarios = sorted({m["scenario_id"] for m in materials})
    conditions = sorted({m["condition_id"] for m in materials})
    directions = sorted({m["direction_version"] for m in materials})
    lines: list[str] = []
    lines.append("# Study B offline research protocol manifest.")
    lines.append("#")
    lines.append("# This manifest freezes the offline research scope. It records protocol")
    lines.append("# metadata and source paths only. It contains no API URL, no API key field,")
    lines.append("# no token budget, no cost, no concurrency, no timeout, no retry policy and")
    lines.append("# no online model state. Judge model ids are protocol metadata only and")
    lines.append("# must never be used to originate a call.")
    lines.append("")
    lines.append("program_name: LLM行动者归因评测")
    lines.append("study_name: 机器主体决策过程归因")
    lines.append(f"source_commit: {SOURCE_COMMIT}")
    lines.append("protocol_date: 2026-07-30")
    lines.append("protocol_scope: offline_protocol_and_import")
    lines.append(f"material_count: {len(materials)}")
    lines.append(f"condition_count: {len(conditions)}")
    lines.append(f"scenario_count: {len(scenarios)}")
    lines.append(f"direction_count: {len(directions)}")
    lines.append("construct_ids: [" + ", ".join(CONSTRUCT_IDS) + "]")
    lines.append(
        "supplementary_score_ids: [" + ", ".join(SUPPLEMENTARY_SCORE_IDS) + "]"
    )
    lines.append("contrast_ids: [" + ", ".join(CONTRAST_IDS) + "]")
    lines.append(f"analysis_formula: >-\n  {ANALYSIS_FORMULA}")
    lines.append("")
    lines.append("judge_models:")
    lines.append("  protocol_metadata_only: true")
    lines.append("  models:")
    for model in JUDGE_MODELS:
        lines.append(f"    - {model}")
    lines.append("")
    lines.append("material_source_paths:")
    lines.append(f"  - {MATERIAL_SOURCE_PATH}")
    lines.append(
        "  - tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/condition_matrix.csv"
    )
    lines.append("item_source_paths:")
    lines.append(
        "  - tasks/attribution_behavior/measurement_candidates/pa_wu_p0/items_wu_shen_2026.yaml"
    )
    lines.append(
        "  - tasks/attribution_behavior/measurement_candidates/pa_wu_p0/items_pa_2024.yaml"
    )
    lines.append(
        "  - tasks/attribution_behavior/measurement_candidates/pa_wu_p0/forms.yaml"
    )
    lines.append("scoring_spec_paths:")
    lines.append(
        "  - tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/scoring_spec.yaml"
    )
    lines.append("analysis_plan_paths:")
    lines.append(
        "  - tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/analysis_plan.md"
    )
    lines.append(
        "  - tasks/attribution_behavior/evaluations/pa_wu_r1_pilot/study_protocol.yaml"
    )
    lines.append("example_data_paths:")
    lines.append("  - docs/pa-wu-r1-pilot/data/showcase_data.json")
    lines.append("  - research_packages/study_b/external_result_example.jsonl")
    lines.append("public_page_paths:")
    lines.append("  - docs/pa-wu-r1-pilot/index.html")
    lines.append("  - /machine-decision-process-attribution/")
    lines.append("")
    return "\n".join(lines) + "\n"


def artefacts() -> dict[str, str]:
    materials = load_materials()
    material_rows = build_material_matrix_rows(materials)
    scoring_rows = build_scoring_template_rows(materials)
    return {
        "protocol_manifest.yaml": build_protocol_manifest(materials),
        "asset_hashes.json": build_asset_hashes(),
        "material_matrix.csv": rows_to_csv(MATERIAL_MATRIX_COLUMNS, material_rows),
        "scoring_matrix_template.csv": rows_to_csv(SCORING_TEMPLATE_COLUMNS, scoring_rows),
    }


def write_artefacts(target: Path) -> list[str]:
    target.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for name, content in artefacts().items():
        (target / name).write_text(content, encoding="utf-8", newline="")
        written.append(name)
    return written


def check_artefacts(target: Path) -> list[str]:
    mismatches: list[str] = []
    for name, content in artefacts().items():
        path = target / name
        if not path.is_file():
            mismatches.append(f"missing: {name}")
            continue
        current = path.read_text(encoding="utf-8")
        if current != content:
            mismatches.append(f"drift: {name}")
    return mismatches


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Study B offline research package.")
    parser.add_argument(
        "--output",
        default=str(PACKAGE),
        help="Output directory (defaults to research_packages/study_b).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify committed artefacts match freshly built content; do not write.",
    )
    args = parser.parse_args(argv)
    target = Path(args.output).resolve()

    if args.check:
        mismatches = check_artefacts(target)
        if mismatches:
            for item in mismatches:
                print(f"build_study_b_protocol_package: ERROR: {item}", file=sys.stderr)
            return 1
        print("study B protocol package is up to date (4 artefacts)")
        return 0

    written = write_artefacts(target)
    print(f"study B protocol package written: {len(written)} artefacts -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
