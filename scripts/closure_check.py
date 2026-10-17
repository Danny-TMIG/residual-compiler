#!/usr/bin/env python3
"""scripts/closure_check.py — cross-cut closure of the 30-class lattice."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"
OUT = APEX / "CLOSURE.json"

FAMILIES = {
    "A": ["A0", "A1", "A2", "A3", "A4"],
    "B": ["B0", "B1", "B2", "B3", "B4", "B5", "B6"],
    "C": ["C0", "C1", "C2", "C3", "C4"],
    "D": ["D0", "D1", "D2", "D3"],
    "E": ["E0", "E1", "E2", "E3", "E4", "D4"],
    "F": ["F0", "F1", "F2"],
}
ALL_CLASSES: set[str] = set()
for _f, _c in FAMILIES.items():
    ALL_CLASSES.update(_c)

RESIDUAL = {"E2", "F0", "F1", "F2"}

IMPLIES = {
    "A2": ["A1"],
    "A3": ["A1", "B1"],
    "B3": ["B2", "B4"],
    "B4": ["B2"],
    "B6": ["B5"],
    "C0": ["A3", "B1"],
    "C1": ["C0", "C2"],
    "C4": ["C3"],
    "D2": ["C2", "C3"],
    "D4": ["D1", "D3"],
    "E0": ["A3", "A4", "B1", "B2", "B5", "C0", "C2", "C3", "D0", "D1", "D3"],
    "E1": ["E0"],
    "E3": ["E2"],
    "E4": ["E2"],
}
OBSERVERS = {
    "A0": ["install", "sbom"],
    "A1": ["install"],
    "A4": ["security"],
    "B0": ["test"],
    "B1": ["quality"],
    "B2": ["quality"],
    "B5": ["test"],
    "C2": ["test"],
    "C3": ["test"],
    "D0": ["quality"],
    "D1": ["version-check"],
    "D3": ["sbom"],
}


def closure(closed):
    out = set(closed)
    changed = True
    while changed:
        changed = False
        for d, ps in IMPLIES.items():
            if d not in out and all(p in out for p in ps):
                out.add(d)
                changed = True
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--job", action="append", default=[])
    ap.add_argument("--hook", action="append", default=[])
    a = ap.parse_args()
    seen = set(a.job) | set(a.hook)
    mc = {c for c, obs in OBSERVERS.items() if all(o in seen for o in obs)}
    c = closure(mc | RESIDUAL)
    missing = sorted(ALL_CLASSES - c)
    derived = sorted(c - mc - RESIDUAL)
    residual = sorted(RESIDUAL & ALL_CLASSES)
    record = {
        "schema": "closure/v1",
        "mechanical_closed": sorted(mc),
        "derived": derived,
        "residual": residual,
        "missing": missing,
        "converged": not missing,
        "n_classes": len(ALL_CLASSES),
        "n_mechanical_closed": len(mc),
        "n_derived": len(derived),
        "n_residual": len(residual),
    }
    p = Path(a.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(f"[written] {p}")
    print(f"[closed]  {len(mc)}/{len(ALL_CLASSES)} mechanical")
    print(f"[derived] {len(derived)} via cross-cut")
    print(f"[residual] {residual}")
    if missing:
        print(f"[REFUTED] silent gaps: {missing}")
        return 1
    print(f"[converged] {len(ALL_CLASSES)} classes -> {len(residual)} residuals")
    return 0


if __name__ == "__main__":
    sys.exit(main())
