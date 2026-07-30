#!/usr/bin/env python
"""Internal compatibility entry point.

The canonical builder is ``scripts/build_research_a_scenario_results.py``. This
module re-exports it under the older name so existing tooling keeps working. The
public site, README and research documents reference the scenario builder.
"""

from __future__ import annotations

from build_research_a_scenario_results import main

if __name__ == "__main__":
    raise SystemExit(main())
