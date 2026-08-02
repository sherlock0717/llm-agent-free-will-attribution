"""Tests for the cross-platform Research A artifact checker."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

SPEC = importlib.util.spec_from_file_location(
    "check_research_a_robustness_outputs",
    SCRIPTS / "check_research_a_robustness_outputs.py",
)
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def test_json_comparison_accepts_only_float_tail_noise():
    checker.assert_equivalent(
        {"value": 1.0 + 5e-14, "nested": [2, "same", True, None]},
        {"value": 1.0, "nested": [2, "same", True, None]},
    )
    with pytest.raises(checker.ArtifactMismatch):
        checker.assert_equivalent({"value": 1.0 + 1e-8}, {"value": 1.0})


def test_json_comparison_keeps_structure_and_text_strict():
    with pytest.raises(checker.ArtifactMismatch):
        checker.assert_equivalent({"a": 1, "b": 2}, {"b": 2, "a": 1})
    with pytest.raises(checker.ArtifactMismatch):
        checker.assert_equivalent({"label": "changed"}, {"label": "original"})


def test_text_normalization_accepts_tail_noise_but_not_real_change():
    left = "estimate=3.2672415862233615; label=A4"
    right = "estimate=3.267241586223374; label=A4"
    assert checker.canonicalize_float_tokens(left) == checker.canonicalize_float_tokens(right)

    changed = "estimate=3.26724159; label=A4"
    assert checker.canonicalize_float_tokens(left) != checker.canonicalize_float_tokens(changed)


def test_current_committed_outputs_are_cross_platform_equivalent():
    assert checker.check_outputs(checker.analysis.DEFAULT_SCORES) == []
