#!/usr/bin/env python
"""Assemble the combined static Pages artifact for local preview and CI deploy.

Public routes:

- ``/``: research-program overview from ``site/``;
- ``/identity-process-attribution-baseline/``: Research A;
- ``/machine-decision-process-attribution/``: Research B;
- ``/pa-wu-r1-pilot/``: lightweight compatibility redirect to Research B.

Local preview and CI deploy use the same assembled output.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "site"
STUDY_A_SOURCE = ROOT / "docs" / "identity-process-attribution-baseline"
STUDY_B_SOURCE = ROOT / "docs" / "pa-wu-r1-pilot"
STUDY_A_ROUTE = "identity-process-attribution-baseline"
STUDY_B_ROUTE = "machine-decision-process-attribution"
LEGACY_B_ROUTE = "pa-wu-r1-pilot"

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

ROOT_JSON = [
    "site_summary.json",
    "showcase_story.json",
    "measurement_summary.json",
    "analysis_results.json",
    "historical_results.json",
    "engineering_status.json",
    "evidence_matrix.json",
    "reproducibility_summary.json",
]
ROOT_FIGURES = [
    "mean_agency.png",
    "mean_free_will_attribution.png",
    "mean_subjective_process_completeness.png",
]
STUDY_B_FIGURES = [
    "fig1_condition_construct_means.png",
    "fig2_model_adjusted_contrasts.png",
    "fig3_model_profiles.png",
    "fig4_scenario_construct_heatmap.png",
    "fig5_contrast_forest.png",
]


class AssembleError(RuntimeError):
    """Raised when a required source or assembled asset is missing."""


def _require_dir(path: Path) -> Path:
    if not path.is_dir():
        raise AssembleError(f"required source directory missing: {path}")
    return path


def assemble(output: Path) -> None:
    _require_dir(SITE_DIR)
    _require_dir(STUDY_A_SOURCE)
    _require_dir(STUDY_B_SOURCE)

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    shutil.copytree(SITE_DIR, output, dirs_exist_ok=True)
    shutil.copytree(STUDY_A_SOURCE, output / STUDY_A_ROUTE)
    shutil.copytree(STUDY_B_SOURCE, output / STUDY_B_ROUTE)

    legacy_dir = output / LEGACY_B_ROUTE
    legacy_dir.mkdir(parents=True, exist_ok=True)
    (legacy_dir / "index.html").write_text(REDIRECT_HTML, encoding="utf-8")

    _verify(output)


def _verify(output: Path) -> None:
    required = [
        output / "index.html",
        output / "assets" / "css" / "site.css",
        output / "assets" / "js" / "site.js",
        output / STUDY_A_ROUTE / "index.html",
        output / STUDY_A_ROUTE / "app.js",
        output / STUDY_A_ROUTE / "styles.css",
        output / STUDY_B_ROUTE / "index.html",
        output / STUDY_B_ROUTE / "app.js",
        output / STUDY_B_ROUTE / "styles.css",
        output / STUDY_B_ROUTE / "data" / "showcase_data.json",
        output / LEGACY_B_ROUTE / "index.html",
    ]
    required.extend(output / "data" / name for name in ROOT_JSON)
    required.extend(output / "assets" / "figures" / name for name in ROOT_FIGURES)
    required.extend(output / STUDY_B_ROUTE / "assets" / "figures" / name for name in STUDY_B_FIGURES)

    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise AssembleError("assembled output missing: " + ", ".join(missing))

    legacy_html = (output / LEGACY_B_ROUTE / "index.html").read_text(encoding="utf-8")
    if f"../{STUDY_B_ROUTE}/" not in legacy_html:
        raise AssembleError("legacy Research B route does not target the canonical route")

    study_a_html = (output / STUDY_A_ROUTE / "index.html").read_text(encoding="utf-8")
    if "身份与决策过程归因基线" not in study_a_html:
        raise AssembleError("Research A page title missing from assembled output")

    study_b_html = (output / STUDY_B_ROUTE / "index.html").read_text(encoding="utf-8")
    if "机器主体决策过程归因评测" not in study_b_html:
        raise AssembleError("Research B page title missing from assembled output")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assemble the combined Pages artifact.")
    parser.add_argument("--output", default="_site", help="Output directory (default: _site)")
    args = parser.parse_args(argv)
    output_arg = Path(args.output)
    output = (ROOT / output_arg).resolve() if not output_arg.is_absolute() else output_arg

    try:
        assemble(output)
    except AssembleError as exc:
        print(f"assemble_pages: ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"assembled Pages artifact at {output}")
    print(f"  overview:             {output / 'index.html'}")
    print(f"  Research A:           {output / STUDY_A_ROUTE / 'index.html'}")
    print(f"  Research B:           {output / STUDY_B_ROUTE / 'index.html'}")
    print(f"  Research B legacy:    {output / LEGACY_B_ROUTE / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
