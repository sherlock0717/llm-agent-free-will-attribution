"""Shared browser-safe JSON serialization helpers for public artifacts."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

try:
    import numpy as np
except ImportError:  # pragma: no cover - helper also works without numpy
    np = None

try:
    import pandas as pd
except ImportError:  # pragma: no cover - helper also works without pandas
    pd = None


def json_safe(value: Any) -> Any:
    """Return a recursively JSON-compatible value with non-finite numbers as null."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if np is not None:
        if isinstance(value, np.integer):
            return int(value)
        if isinstance(value, np.floating):
            number = float(value)
            return number if math.isfinite(number) else None
        if isinstance(value, np.ndarray):
            return [json_safe(item) for item in value.tolist()]
    if pd is not None:
        try:
            if pd.isna(value):
                return None
        except (TypeError, ValueError):
            pass
    if isinstance(value, dict):
        return {str(key): json_safe(child) for key, child in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_safe(child) for child in value]
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except (TypeError, ValueError):
            pass
    return value


def dumps(value: Any, *, sort_keys: bool = True) -> str:
    """Serialize public JSON with RFC-compatible finite numeric values."""
    return json.dumps(
        json_safe(value),
        ensure_ascii=False,
        indent=2,
        sort_keys=sort_keys,
        allow_nan=False,
    ) + "\n"


def write(path: Path, value: Any, *, sort_keys: bool = True) -> None:
    """Write a UTF-8 public JSON file using :func:`dumps`."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(value, sort_keys=sort_keys), encoding="utf-8")
