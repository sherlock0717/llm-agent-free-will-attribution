#!/usr/bin/env python
"""Assemble the combined static Pages artifact for local preview and CI deploy.

The root project overview lives in ``site/``. Research B's standalone page source
stays under ``docs/pa-wu-r1-pilot/`` for now, and is published at the canonical
public route ``/machine-decision-process-attribution/``. The legacy
``/pa-wu-r1-pilot/`` route is kept as a lightweight redirect for compatibility.

Local preview and CI deploy use the same assembled output, so the study-B page
resolves identically in both places.

Usage:
    python scripts/assemble_pages.py --output _site
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "site"
STUDY_B_SOURCE = ROOT / "docs" / "pa-wu-r1-pilot"
CANONICAL_ROUTE = "machine-decision-process-attribution"
LEGACY_ROUTE = "pa-wu-r1-pilot"

REDIRECT_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta http-equiv="refresh" content="0; url=../machine-decision-process-attribution/" />
  <link rel="canonical" href="../machine-decision-process-attribution/" />
  <title>研究B页面已迁移</title>
</head>
<body>
  <p>研究B页面已迁移至“机器主体决策过程归因评测”。</p>
  <p><a href="../machine-decision-process-attribution/">前往机器主体决策过程归因评测</a></p>
</body>
</html>
"""


class AssembleError(RuntimeError):
    """Raised when a required source path is missing."""


def _require_dir(path: Path) -> Path:
    if not path.is_dir():
        raise AssembleError(f"required source directory missing: {path}")
    return path


def assemble(output: Path) -> None:
    _require_dir(SITE_DIR)
    _require_dir(STUDY_B_SOURCE)

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    # Root project overview at the artifact root.
    shutil.copytree(SITE_DIR, output, dirs_exist_ok=True)

    # Research B at the canonical public route.
    canonical_dir = output / CANONICAL_ROUTE
    shutil.copytree(STUDY_B_SOURCE, canonical_dir)

    # Legacy route: lightweight redirect page only (no full copy).
    legacy_dir = output / LEGACY_ROUTE
    legacy_dir.mkdir(parents=True, exist_ok=True)
    (legacy_dir / "index.html").write_text(REDIRECT_HTML, encoding="utf-8")

    _verify(output)


def _verify(output: Path) -> None:
    required = [
        output / "index.html",
        output / CANONICAL_ROUTE / "index.html",
        output / CANONICAL_ROUTE / "app.js",
        output / CANONICAL_ROUTE / "styles.css",
        output / LEGACY_ROUTE / "index.html",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise AssembleError("assembled output missing: " + ", ".join(missing))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assemble the combined Pages artifact.")
    parser.add_argument("--output", default="_site", help="Output directory (default: _site)")
    args = parser.parse_args(argv)

    output = (ROOT / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)
    try:
        assemble(output)
    except AssembleError as exc:
        print(f"assemble_pages: ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"assembled Pages artifact at {output}")
    print(f"  root overview:        {output / 'index.html'}")
    print(f"  study B (canonical):  {output / CANONICAL_ROUTE / 'index.html'}")
    print(f"  study B (legacy):     {output / LEGACY_ROUTE / 'index.html'} (redirect)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
