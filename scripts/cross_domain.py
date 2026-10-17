#!/usr/bin/env python3
"""cross_domain.py — engine_available witness.

Reads apex/ENGINES.json (schema engines/v1, key "nodes").
Invariant engine_available: at least one declared engine is present
on this host, and the majority of probed engines resolve to a binary.
"""

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"


def main():
    eng = json.loads((APEX / "ENGINES.json").read_text())
    nodes = eng.get("nodes") or eng.get("engines") or []
    present, missing = [], []
    for n in nodes:
        name = n.get("name") or n.get("id") or ""
        cmd = n.get("cmd") or name
        if cmd and shutil.which(cmd):
            present.append(name)
        else:
            missing.append(name)
    total = len(nodes)
    if total == 0:
        print(json.dumps({"verdict": "refuted:no_engines_declared"}))
        return 1
    if not present:
        print(
            json.dumps(
                {"verdict": "refuted:no_engine_available", "present": 0, "total": total}
            )
        )
        return 1
    ratio = len(present) / total
    verdict = "VALID" if ratio >= 0.5 else "refuted:insufficient_engines"
    print(
        json.dumps(
            {
                "verdict": verdict,
                "invariant": "engine_available",
                "present": len(present),
                "missing": len(missing),
                "total": total,
                "ratio": round(ratio, 3),
                "missing_sample": missing[:8],
            }
        )
    )
    return 0 if verdict == "VALID" else 1


if __name__ == "__main__":
    sys.exit(main())
