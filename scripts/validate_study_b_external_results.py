#!/usr/bin/env python
"""Validate an external, offline Study B scoring file.

This tool reads a JSONL or CSV file of externally produced offline scores and
validates it against ``research_packages/study_b/external_result_schema.json``
and the frozen ``material_matrix.csv``. It is strictly offline and read-only:

* it never opens a network connection;
* it never reads an API key or any environment variable;
* it never imports a model SDK;
* it never modifies the input file;
* it never infers, imputes or repairs missing scores.

On completion it prints a summary and, with ``--report``, writes a JSON report.
The process exit code is non-zero when any record fails validation.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research_packages" / "study_b"
SCHEMA_PATH = PACKAGE / "external_result_schema.json"
MATERIAL_MATRIX_PATH = PACKAGE / "material_matrix.csv"

ALLOWED_JUDGE_SLOTS = {"judge_1", "judge_2"}
ALLOWED_JUDGE_MODELS = {"deepseek-v4-pro", "gpt-5.6-terra"}
REQUIRED_FIELDS = [
    "material_id",
    "judge_slot",
    "judge_model_id",
    "item_responses",
    "source_record_id",
    "source_file_hash",
]


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"), parse_constant=_reject_constant)


def load_material_ids() -> set[str]:
    ids: set[str] = set()
    with MATERIAL_MATRIX_PATH.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            ids.add(row["material_id"])
    return ids


def read_records(path: Path) -> list[dict[str, Any]]:
    """Read records from a JSONL (default) or CSV file. No network access."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open(encoding="utf-8", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    records: list[dict[str, Any]] = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line, parse_constant=_reject_constant))
    return records


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(
        float(value)
    )


def validate_records(
    records: list[dict[str, Any]],
    schema: dict[str, Any],
    material_ids: set[str],
) -> dict[str, Any]:
    ranges = schema["item_scale_ranges"]
    required_items = set(ranges)
    errors: list[dict[str, Any]] = []
    seen_keys: dict[tuple[str, str], int] = {}

    for index, record in enumerate(records):
        loc = f"record[{index}]"

        unknown = sorted(set(record) - set(REQUIRED_FIELDS))
        if unknown:
            errors.append({"loc": loc, "code": "unknown_field", "detail": unknown})
        missing = [field for field in REQUIRED_FIELDS if field not in record]
        if missing:
            errors.append({"loc": loc, "code": "missing_field", "detail": missing})
            continue

        material_id = record["material_id"]
        judge_slot = record["judge_slot"]

        if material_id not in material_ids:
            errors.append({"loc": loc, "code": "unknown_material_id", "detail": material_id})
        if judge_slot not in ALLOWED_JUDGE_SLOTS:
            errors.append({"loc": loc, "code": "bad_judge_slot", "detail": judge_slot})
        if record["judge_model_id"] not in ALLOWED_JUDGE_MODELS:
            errors.append(
                {"loc": loc, "code": "bad_judge_model_id", "detail": record["judge_model_id"]}
            )

        key = (material_id, judge_slot)
        if key in seen_keys:
            errors.append(
                {
                    "loc": loc,
                    "code": "duplicate_key",
                    "detail": {"material_id": material_id, "judge_slot": judge_slot,
                               "first_seen": seen_keys[key]},
                }
            )
        else:
            seen_keys[key] = index

        items = record["item_responses"]
        if not isinstance(items, dict):
            errors.append({"loc": loc, "code": "item_responses_not_object", "detail": type(items).__name__})
            continue

        unknown_items = sorted(set(items) - required_items)
        if unknown_items:
            errors.append({"loc": loc, "code": "unknown_item", "detail": unknown_items})
        missing_items = sorted(required_items - set(items))
        if missing_items:
            errors.append({"loc": loc, "code": "missing_item", "detail": missing_items})

        for item_id, value in items.items():
            if item_id not in ranges:
                continue
            if not _is_finite_number(value):
                errors.append(
                    {"loc": loc, "code": "non_finite_or_non_numeric",
                     "detail": {"item_id": item_id, "value": repr(value)}}
                )
                continue
            bounds = ranges[item_id]
            if not (bounds["min"] <= float(value) <= bounds["max"]):
                errors.append(
                    {"loc": loc, "code": "out_of_range",
                     "detail": {"item_id": item_id, "value": value,
                                "min": bounds["min"], "max": bounds["max"]}}
                )

    return {
        "schema_id": schema["schema_id"],
        "record_count": len(records),
        "valid": len(errors) == 0,
        "error_count": len(errors),
        "errors": errors,
        "network_operations": "none",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an external offline Study B scoring file (read-only, offline)."
    )
    parser.add_argument("--input", required=True, help="Path to a JSONL or CSV scoring file.")
    parser.add_argument("--report", help="Optional path to write a JSON validation report.")
    args = parser.parse_args(argv)

    input_path = Path(args.input).resolve()
    if not input_path.is_file():
        print(f"validate_study_b_external_results: ERROR: input not found: {input_path}")
        return 2

    schema = load_schema()
    material_ids = load_material_ids()
    records = read_records(input_path)
    report = validate_records(records, schema, material_ids)
    report["input_file"] = str(input_path)

    if args.report:
        report_path = Path(args.report).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    if report["valid"]:
        print(f"validation passed: {report['record_count']} records, 0 errors")
        return 0
    print(f"validation failed: {report['error_count']} errors over {report['record_count']} records")
    for error in report["errors"][:10]:
        print(f"  {error['loc']} {error['code']}: {error['detail']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
