#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", required=True)
    a = ap.parse_args()
    if a.role in ("researcher", "researcher_r"):
        c = APEX / "CLASS-13.json"
        if not c.exists():
            print("[refused] no CLASS-13.json"); return 1
        d = json.loads(c.read_text())
        if d.get("verdict") != "CLASS_13_ESTABLISHED":
            print(f"[refused] Class 13: {d.get('verdict')}"); return 1
        print(f"[established] reader={d.get('reader')}"); return 0
    dec = APEX / "DECISION.json"
    if not dec.exists():
        print("[refused] no DECISION.json"); return 1
    d = json.loads(dec.read_text())
    if d.get("decision") not in ("ship", "hold"):
        print(f"[refused] decision={d.get('decision')!r}"); return 1
    print(f"[bound] {a.role}: {d['decision']} by {d.get('by')}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
