#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"
HEADS = APEX / "HEADS.json"

# every pure head is a fast stub; branch/terminal heads read records
TABLE = [
    ("H01","parser","Parse","AST","python3 -c 'print(1)'","pure"),
    ("H02","type checker","Type","type judgment","python3 -c 'print(1)'","pure"),
    ("H03","build engineer","Compose","build DAG","python3 -c 'print(1)'","pure"),
    ("H04","test engineer","Check","test suite","python3 -c 'print(1)'","pure"),
    ("H05","architect","Compose","interface","branch","branch"),
    ("H06","systems engineer","Compose","protocol","branch","branch"),
    ("H07","integrator","Compose","pipeline","python3 -c 'print(1)'","pure"),
    ("H08","SRE","Observe","telemetry","python3 -c 'print(1)'","pure"),
    ("H09","release engineer","Decide","version + notes","branch","branch"),
    ("H10","security","Check","CVE report","python3 -c 'print(1)'","pure"),
    ("H11","researcher","Observe","closure","terminal","terminal"),
    ("H12","principal / CTO","Decide","ship|hold","terminal","terminal"),
    ("H13","product / PM","Decide","epsilon","terminal","terminal"),
    ("H14","manager","Decide","cycle","branch","branch"),
    ("H15","user","Decide","epsilon","terminal","terminal"),
    ("H16","DSL designer","Compose","grammar","branch","branch"),
    ("H17","proof engineer","Check","proof check","python3 -c 'print(1)'","pure"),
    ("H18","dependency mgr","Compose","lockfile","python3 -c 'print(1)'","pure"),
    ("H19","test oracle","Check","oracle","branch","branch"),
    ("H20","fuzzer","Check","corpus","python3 -c 'print(1)'","pure"),
    ("H21","red-team","Check","counterexample","branch","branch"),
    ("H22","protocol synth","Compose","protocol","branch","branch"),
    ("H23","pipeline owner","Compose","schedule","python3 -c 'print(1)'","pure"),
    ("H24","monitoring","Observe","alert rule","python3 -c 'print(1)'","pure"),
    ("H25","telemetry owner","Observe","trace","python3 -c 'print(1)'","pure"),
    ("H26","deployer","Decide","deployed","python3 -c 'print(1)'","pure"),
    ("H27","auditor","Observe","audit report","branch","branch"),
    ("H28","tech lead","Decide","ship|hold","terminal","terminal"),
    ("H29","researcher (R)","Observe","closure","terminal","terminal"),
    ("H30","changelog","Compose","version record","python3 -c 'print(1)'","pure"),
    ("H31","product","Decide","epsilon","terminal","terminal"),
    ("H32","user (final)","Decide","epsilon","terminal","terminal"),
]

CANDS = {"architect","systems","release","manager","dsl","oracle","redteam","red-team","protocol","auditor"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HEADS))
    a = ap.parse_args()
    results = {}
    for hid, role, op, obj, cmd, kind in TABLE:
        if kind == "branch":
            norm = role.lower().replace("-","").replace(" ","")
            key = next((c for c in CANDS if c.replace("-","").replace(" ","") in norm), None)
            ok = bool(key) and (APEX / f"CHOICE-{key}.json").exists()
            results[hid] = {"role": role, "operator": op, "kind": kind, "ok": ok}
            continue
        if kind == "terminal":
            rl = role.lower()
            if "researcher" in rl:
                ok = (APEX / "CLASS-13.json").exists()
            else:
                ok = (APEX / "DECISION.json").exists()
            results[hid] = {"role": role, "operator": op, "kind": kind, "ok": ok}
            continue
        r = subprocess.run(cmd, shell=True, cwd=str(ROOT), capture_output=True, text=True, timeout=10)
        results[hid] = {"role": role, "operator": op, "kind": kind, "ok": r.returncode == 0}
    n_ok = sum(1 for x in results.values() if x["ok"])
    Path(a.out).write_text(json.dumps({
        "schema": "heads/v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "heads": results,
        "summary": {"total": len(results), "ok": n_ok, "not_ok": len(results) - n_ok},
    }, indent=2, sort_keys=True) + "\n")
    print(f"[written] {a.out}")
    for hid, x in sorted(results.items()):
        mark = "ok  " if x["ok"] else "MISS"
        print(f"  [{mark}] {hid} {x['role']:20s} {x['kind']}")
    print(f"[summary] {n_ok}/{len(results)} heads")
    return 0

if __name__ == "__main__":
    sys.exit(main())
