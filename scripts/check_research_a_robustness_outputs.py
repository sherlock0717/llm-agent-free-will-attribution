#!/usr/bin/env python
"""Check committed Research A robustness outputs across operating systems.

The statistical payload can differ in the last floating-point bits across BLAS,
NumPy, and operating-system combinations. This checker keeps the artifact gate
strict for structure and text while allowing only numerical tail noise:

- JSON keys, list lengths, strings, booleans, integers, and nulls are exact;
- floating-point values use a 1e-12 absolute/relative tolerance;
- Markdown and SVG text remain exact after canonicalizing floating tokens to
  12 significant digits;
- larger numerical or any non-numerical change still fails.

It never writes files and never calls a model or the network.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import analyze_research_a_robustness as analysis

FLOAT_REL_TOL = 1e-12
FLOAT_ABS_TOL = 1e-12
FLOAT_TOKEN = re.compile(
    r"(?<![\w.])[-+]?(?:(?:\d+\.\d*|\.\d+)(?:[eE][-+]?\d+)?|\d+[eE][-+]?\d+)(?![\w.])"
)


class ArtifactMismatch(AssertionError):
    """Raised when a committed artifact differs beyond numerical tail noise."""


def assert_equivalent(actual: Any, expected: Any, path: str = "$") -> None:
    """Recursively compare JSON-compatible values with strict structure."""
    if isinstance(actual, bool) or isinstance(expected, bool):
        if type(actual) is not type(expected) or actual != expected:
            raise ArtifactMismatch(f"{path}: {actual!r} != {expected!r}")
        return

    if isinstance(actual, dict) and isinstance(expected, dict):
        if list(actual) != list(expected):
            raise ArtifactMismatch(
                f"{path}: key order/set differs: {list(actual)!r} != {list(expected)!r}"
            )
        for key in actual:
            assert_equivalent(actual[key], expected[key], f"{path}.{key}")
        return

    if isinstance(actual, list) and isinstance(expected, list):
        if len(actual) != len(expected):
            raise ArtifactMismatch(f"{path}: list length {len(actual)} != {len(expected)}")
        for index, (actual_item, expected_item) in enumerate(zip(actual, expected, strict=True)):
            assert_equivalent(actual_item, expected_item, f"{path}[{index}]")
        return

    number_types = (int, float)
    if isinstance(actual, number_types) and isinstance(expected, number_types):
        if isinstance(actual, int) and isinstance(expected, int):
            if actual != expected:
                raise ArtifactMismatch(f"{path}: {actual!r} != {expected!r}")
            return
        actual_float = float(actual)
        expected_float = float(expected)
        if not math.isfinite(actual_float) or not math.isfinite(expected_float):
            raise ArtifactMismatch(f"{path}: non-finite value")
        if not math.isclose(
            actual_float,
            expected_float,
            rel_tol=FLOAT_REL_TOL,
            abs_tol=FLOAT_ABS_TOL,
        ):
            raise ArtifactMismatch(f"{path}: {actual_float!r} != {expected_float!r}")
        return

    if type(actual) is not type(expected) or actual != expected:
        raise ArtifactMismatch(f"{path}: {actual!r} != {expected!r}")


def canonicalize_float_tokens(text: str) -> str:
    """Normalize only standalone decimal/scientific tokens in text artifacts."""

    def replace(match: re.Match[str]) -> str:
        value = float(match.group(0))
        if abs(value) <= FLOAT_ABS_TOL:
            value = 0.0
        return format(value, ".12g")

    return FLOAT_TOKEN.sub(replace, text)


def _compare_json(path: Path, payload: dict) -> str | None:
    if not path.is_file():
        return f"{path}: missing"
    try:
        committed = json.loads(path.read_text(encoding="utf-8"))
        generated = json.loads(analysis.public_dumps(payload))
        assert_equivalent(generated, committed)
    except (json.JSONDecodeError, ArtifactMismatch) as exc:
        return f"{path}: {exc}"
    return None


def _compare_text(path: Path, generated: str) -> str | None:
    if not path.is_file():
        return f"{path}: missing"
    committed = path.read_text(encoding="utf-8")
    if canonicalize_float_tokens(generated) != canonicalize_float_tokens(committed):
        return f"{path}: non-numerical or material numerical drift"
    return None


def check_outputs(scores_path: Path) -> list[str]:
    """Return mismatch descriptions without writing repository files."""
    payload = analysis.run(scores_path.resolve(), analysis.DEFAULT_OUTPUT)
    mismatches: list[str] = []

    json_error = _compare_json(analysis.PUBLIC_JSON, payload)
    if json_error:
        mismatches.append(json_error)

    report_error = _compare_text(analysis.REPORT_MD, analysis.build_report(payload))
    if report_error:
        mismatches.append(report_error)

    figures = {
        analysis.FIG_IDENTITY: analysis._render_identity_process_svg(
            payload["identity_by_process"]
        ),
        analysis.FIG_INFLUENCE: analysis._render_scenario_influence_svg(
            payload["scenario_influence"]
        ),
        analysis.FIG_LENGTH: analysis._render_length_sensitivity_svg(
            payload["length_sensitivity"]
        ),
    }
    for path, generated in figures.items():
        figure_error = _compare_text(path, generated)
        if figure_error:
            mismatches.append(figure_error)

    return mismatches


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Cross-platform check for committed Research A robustness outputs."
    )
    parser.add_argument("--scores", default=str(analysis.DEFAULT_SCORES))
    args = parser.parse_args(argv)

    try:
        mismatches = check_outputs(Path(args.scores))
    except analysis.RobustnessError as exc:
        print(f"check_research_a_robustness_outputs: ERROR: {exc}", file=sys.stderr)
        return 2

    if mismatches:
        print("research A robustness outputs are OUT OF DATE:", file=sys.stderr)
        for mismatch in mismatches:
            print(f"- {mismatch}", file=sys.stderr)
        return 1

    print("research A robustness outputs are cross-platform equivalent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
