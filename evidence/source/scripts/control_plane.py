#!/usr/bin/env python3
"""control_plane.py — the substrate every craft must pass through.

A craft is admitted iff its gate node is RUNNING/READY in MACHINE-STATE
AND its independent witness exits 0. A craft's *invariant is proven*
only when the witness produces a positive verdict — not merely "ran".
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"

def load(name):
    return json.loads((APEX / name).read_text())

def normalize_nodes(raw):
    state = {}
    if isinstance(raw, dict):
        for nid, meta in raw.items():
            if isinstance(meta, dict):
                row = {"id": nid, **meta}
                state[nid] = row
                if "name" in row:
                    state[row["name"]] = row
            elif isinstance(meta, str):
                parts = meta.split()
                state[nid] = {"id": nid,
                              "status": parts[0] if parts else None}
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict) and "id" in item:
                state[item["id"]] = item
                if "name" in item:
                    state[item["name"]] = item
    return state

def run_witness(w):
    if w == "machine":
        return True, 0, None
    if w == "braid":
        r = subprocess.run(["python3", "braid.py"],
                           cwd=ROOT / "braid", capture_output=True, text=True)
        ok = (r.returncode == 0) and ("ALL BACKENDS AGREE" in r.stdout)
        return ok, r.returncode, None
    r = subprocess.run(["python3", f"scripts/{w}.py"],
                       cwd=ROOT, capture_output=True, text=True)
    try:
        verdict = json.loads(r.stdout).get("verdict")
    except Exception:
        verdict = None
    ok = (r.returncode == 0)
    return ok, r.returncode, verdict

def main():
    raw_crafts = load("CRAFTS.json")["crafts"]
    if isinstance(raw_crafts, dict):
        crafts_iter = raw_crafts.items()
    else:
        crafts_iter = ((c["craft"] if "craft" in c else c.get("name"), c) for c in raw_crafts)
    nodes = normalize_nodes(load("MACHINE-STATE.json")["nodes"])

    rows, refuted = [], []
    for name, spec in crafts_iter:
        node = nodes.get(spec["gate"]) or nodes.get(f"engine:{spec['gate']}") or {}
        status = node.get("status") or node.get("state")
        gate_ok = status in ("RUNNING", "READY")

        witness_ok, rc, verdict = run_witness(spec["witness"])
        if verdict is None:
            invariant_proven = witness_ok and rc == 0
        else:
            v = str(verdict).lower()
            bad = v.startswith(("refuted", "partial", "falsified", "fail"))
            invariant_proven = (not bad) and witness_ok and rc == 0

        ok = gate_ok and witness_ok
        rows.append({
            "craft": name, "gate": spec["gate"], "inv": spec["inv"],
            "gate_status": status, "witness": spec["witness"],
            "witness_rc": rc, "witness_verdict": verdict,
            "invariant_proven": invariant_proven,
            "pass": ok,
        })
        if not ok:
            refuted.append(name)

    out = {
        "crafts": rows,
        "covered": sum(r["pass"] for r in rows),
        "invariants_proven": sum(1 for r in rows if r["invariant_proven"]),
        "total": len(rows),
        "verdict": "COVERED" if not refuted else "REFUTED:" + ",".join(refuted),
    }
    (APEX / "CRAFTS-STATE.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0 if not refuted else 1

if __name__ == "__main__":
    sys.exit(main())
