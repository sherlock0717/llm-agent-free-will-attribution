#!/usr/bin/env python
"""Validate public JSON assets with browser-compatible strict parsing.

Python's default ``json.loads`` accepts NaN and Infinity, while browsers reject
those tokens. This script rejects non-standard constants and verifies that all
numeric values are finite. It is designed for CI and local Pages checks.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATHS = (
    ROOT / "site" / "data",
    ROOT / "docs" / "pa-wu-r1-pilot" / "data" / "showcase_data.json",
    ROOT
    / "tasks"
    / "attribution_behavior"
    / "evaluations"
    / "pa_wu_r1_pilot"
    / "outputs"
    / "showcase_data.json",
)


class PublicJsonError(RuntimeError):
    """Raised when a public JSON asset is missing or browser-incompatible."""


def _reject_constant(value: str) -> None:
    raise PublicJsonError(f"non-standard JSON constant: {value}")


def _walk_finite(value: Any, path: str = "$") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise PublicJsonError(f"non-finite number at {path}: {value!r}")
    if isinstance(value, dict):
        for key, child in value.items():
            _walk_finite(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_finite(child, f"{path}[{index}]")


def _iter_json_files(paths: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix.lower() == ".json":
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(path.rglob("*.json")))
    return sorted(set(files))


def validate_file(path: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PublicJsonError(f"cannot read {path}: {exc}") from exc
    if text.startswith("\ufeff"):
        raise PublicJsonError(f"UTF-8 BOM is not allowed: {path}")
    try:
        payload = json.loads(text, parse_constant=_reject_constant)
    except (json.JSONDecodeError, PublicJsonError) as exc:
        raise PublicJsonError(f"invalid strict JSON in {path}: {exc}") from exc
    _walk_finite(payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate public JSON assets.")
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to scan. Defaults to the published data assets.",
    )
    args = parser.parse_args(argv)

    paths = [Path(value).resolve() for value in args.paths] if args.paths else list(DEFAULT_PATHS)
    missing_paths = [str(path) for path in paths if not path.exists()]
    if missing_paths:
        print("check_public_json: ERROR: public paths missing: " + ", ".join(missing_paths), file=sys.stderr)
        return 2

    files = _iter_json_files(paths)
    if not files:
        print("check_public_json: ERROR: no JSON files found", file=sys.stderr)
        return 2

    failures: list[str] = []
    for path in files:
        try:
            validate_file(path)
        except PublicJsonError as exc:
            failures.append(str(exc))

    if failures:
        for failure in failures:
            print(f"check_public_json: ERROR: {failure}", file=sys.stderr)
        return 1

    print(f"strict public JSON validated: {len(files)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
