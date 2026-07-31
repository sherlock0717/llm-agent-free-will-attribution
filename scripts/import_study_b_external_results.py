#!/usr/bin/env python
"""Import an external, offline Study B scoring file into an offline run directory.

Import only proceeds when the input first passes
``validate_study_b_external_results``. The tool copies the validated file into a
new offline run directory, records the source SHA-256, the import timestamp and
the validation report, and writes standardized records. It is strictly offline
and read-only with respect to the input:

* it never opens a network connection;
* it never reads an API key or any environment variable;
* it never imports a model SDK;
* it never overwrites an existing import directory;
* it never infers, imputes or repairs missing scores.

Modes:
  --validate-only : run validation and print the result; write nothing.
  --dry-run       : run validation and report the planned actions; write nothing.
  (default)       : validate, then materialize the import directory.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
from pathlib import Path

from validate_study_b_external_results import (
    load_material_ids,
    load_schema,
    read_records,
    validate_records,
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_standardized_records(records: list[dict]) -> list[dict]:
    standardized: list[dict] = []
    for record in records:
        standardized.append(
            {
                "material_id": record["material_id"],
                "judge_slot": record["judge_slot"],
                "judge_model_id": record["judge_model_id"],
                "item_responses": record["item_responses"],
                "source_record_id": record["source_record_id"],
                "source_file_hash": record["source_file_hash"],
                "response_source": "external_offline_file",
            }
        )
    standardized.sort(key=lambda row: (row["material_id"], row["judge_slot"]))
    return standardized


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Import a validated external offline Study B scoring file (offline, read-only input)."
    )
    parser.add_argument("--input", required=True, help="Path to a JSONL or CSV scoring file.")
    parser.add_argument("--output", help="Target offline import directory (required unless validate-only).")
    parser.add_argument("--validate-only", action="store_true", help="Validate and exit; write nothing.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and report planned actions; write nothing.")
    args = parser.parse_args(argv)

    input_path = Path(args.input).resolve()
    if not input_path.is_file():
        print(f"import_study_b_external_results: ERROR: input not found: {input_path}")
        return 2

    schema = load_schema()
    material_ids = load_material_ids()
    records = read_records(input_path)
    report = validate_records(records, schema, material_ids)
    report["input_file"] = str(input_path)

    if not report["valid"]:
        print(f"import blocked: validation failed with {report['error_count']} errors")
        for error in report["errors"][:10]:
            print(f"  {error['loc']} {error['code']}: {error['detail']}")
        return 1

    if args.validate_only:
        print(f"validate-only: {report['record_count']} records valid; no output written")
        return 0

    if not args.output:
        print("import_study_b_external_results: ERROR: --output is required unless --validate-only")
        return 2

    output_dir = Path(args.output).resolve()
    if args.dry_run:
        print(f"dry-run: {report['record_count']} records valid")
        print(f"dry-run: would create import directory {output_dir}")
        print("dry-run: no output written")
        return 0

    if output_dir.exists():
        print(f"import_study_b_external_results: ERROR: output already exists (refusing to overwrite): {output_dir}")
        return 3

    output_dir.mkdir(parents=True)
    source_hash = sha256_file(input_path)
    imported_at = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    (output_dir / input_path.name).write_bytes(input_path.read_bytes())
    (output_dir / "validation_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "standardized_records.jsonl").write_text(
        "\n".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True)
            for row in build_standardized_records(records)
        )
        + "\n",
        encoding="utf-8",
    )
    manifest = {
        "import_id": "study_b.external_import.v1",
        "source_file": input_path.name,
        "source_file_sha256": source_hash,
        "imported_at": imported_at,
        "record_count": report["record_count"],
        "validation_status": "valid",
        "response_source": "external_offline_file",
        "network_operations": "none",
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"import complete: {report['record_count']} records -> {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
