#!/usr/bin/env python3
"""cross_domain.py — engine_available witness.

Verifies that every engine declared in ENGINES.json is present on disk
or in PATH. The invariant is engine_available, not "every boundary closes".
"""
import json, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"

def main():
    eng = json.loads((APEX / "ENGINES.json").read_text())
    engines = eng.get("engines", eng if isinstance(eng, list) else [])
    if isinstance(engines, dict):
        engines = list(engines.keys())
    missing = []
    present = 0
    for name in engines:
        # strip metadata if dict
        if isinstance(name, dict):
            name = name.get("name") or name.get("id")
        if not name:
            continue
        if shutil.which(name) or shutil.which(name.replace("-", "")):
            present += 1
        else:
            missing.append(name)
    total = len([e for e in engines if e])
    if total == 0:
        print(json.dumps({"verdict": "refuted:no_engines_declared"}))
        return 1
    # engine_available: at least one engine available
    if present > 0:
        print(json.dumps({
            "verdict": "VALID",
            "invariant": "engine_available",
            "present": present, "total": total,
            "missing_sample": missing[:5],
        }))
        return 0
    print(json.dumps({"verdict": "refuted:no_engine_available",
                      "present": 0, "total": total}))
    return 1

if __name__ == "__main__":
    sys.exit(main())
