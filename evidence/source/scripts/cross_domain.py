#!/usr/bin/env python3
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"

BOUNDARIES = [
    (0, 1, "physical->silicon", "E0"), (1, 2, "silicon->firmware", "E1"),
    (2, 3, "firmware->os", "E2"), (3, 4, "os->runtime", "E3"),
    (4, 5, "runtime->app", "E4"), (5, 6, "app->org", "E5"),
    (6, 7, "org->society", "E6"),
]

def test_boundary(lower, upper, name, ev_id):
    state_path = APEX / "MACHINE-STATE.json"
    if not state_path.exists():
        return {"boundary": name, "verdict": "no_state"}
    state = json.loads(state_path.read_text())
    ev = state.get("evidence", {}).get(ev_id)
    if not ev:
        return {"boundary": name, "verdict": "missing_evidence"}
    if not ev.get("invariant_passed"):
        return {"boundary": name, "verdict": "lower_failed"}
    if ev.get("falsify_fired"):
        return {"boundary": name, "verdict": "falsified"}
    return {"boundary": name, "verdict": "closed"}

def main():
    results = [test_boundary(*b) for b in BOUNDARIES]
    closed = sum(1 for r in results if r["verdict"] == "closed")
    out = {"boundaries": results, "closed": closed, "total": len(results),
           "verdict": "ALL_CLOSED" if closed == len(results) else "PARTIAL"}
    print(json.dumps(out, indent=2))
    (APEX / "CROSS-DOMAIN.json").write_text(json.dumps(out, indent=2) + "\n")
    return 0 if out["verdict"] == "ALL_CLOSED" else 1

if __name__ == "__main__":
    sys.exit(main())
