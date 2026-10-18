#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"

CANDIDATES = {
    "architect": ["interface: A→B", "interface: A→C", "interface: A→B→C"],
    "systems": ["protocol: request/response", "protocol: pub/sub", "protocol: stream"],
    "release": ["version: patch", "version: minor", "version: major"],
    "manager": ["cycle: weekly", "cycle: daily", "cycle: on-demand"],
    "dsl": ["grammar: BNF", "grammar: PEG", "grammar: EBNF"],
    "oracle": ["oracle: property", "oracle: model", "oracle: golden"],
    "redteam": [
        "counterexample: none",
        "counterexample: classification",
        "counterexample: report",
    ],
    "protocol": ["spec: TLA+", "spec: P", "spec: Alloy"],
    "auditor": ["report: pass", "report: pass-with-notes", "report: fail"],
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", required=True)
    ap.add_argument("--choice", default=None)
    a = ap.parse_args()
    cands = CANDIDATES.get(a.role)
    if not cands:
        print(f"[refused] no policy for {a.role}")
        return 1
    if a.choice:
        if a.choice not in cands:
            print(f"[refused] {a.choice!r} not in {cands}")
            return 1
        out = APEX / f"CHOICE-{a.role}.json"
        out.write_text(
            json.dumps(
                {"role": a.role, "choice": a.choice, "candidates": cands}, indent=2
            )
            + "\n"
        )
        print(f"[chosen] {a.role} -> {a.choice}")
        return 0
    print(f"[candidates] {a.role}: {cands}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
