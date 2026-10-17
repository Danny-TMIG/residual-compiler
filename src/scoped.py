"""
Scope manifest: the ONLY skills this build executes.
Anything not in BOUND is dispatched as NOT_RUN, regardless of any other file.
This is the contract of the build.

BOUND is auto-derived at seed-time from tools.REG. It is materialized here as
a JSON file (data/scope.json) so it can be reviewed, diffed, and audited.
"""

import json
from pathlib import Path

SCOPE_PATH = Path("data/scope.json")


def write_scope(tools_reg):
    bound = sorted(tools_reg.keys())
    SCOPE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCOPE_PATH.write_text(
        json.dumps(
            {
                "bound_tools": bound,
                "count": len(bound),
                "note": "skills not in bound_tools are dispatched as NOT_RUN",
            },
            indent=2,
        )
    )
    return bound


def load_scope():
    if not SCOPE_PATH.exists():
        return set()
    return set(json.loads(SCOPE_PATH.read_text())["bound_tools"])
