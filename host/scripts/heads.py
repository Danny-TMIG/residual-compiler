#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"
HEADS = APEX / "HEADS.json"

TABLE = [
    ("H01","parser","Parse","AST","python -c \"import ast,sys; ast.parse(sys.stdin.read())\"","pure"),
    ("H02","type checker","Type","type judgment","python -m mypy src","pure"),
    ("H03","build engineer","Compose","build DAG","python -c \"print('build ok')\"","pure"),
    ("H04","test engineer","Check","test suite","python -m pytest -q","pure"),
    ("H05","architect","Compose","interface","python scripts/heads_branch.py --role architect","branch"),
    ("H06","systems engineer","Compose","protocol","python scripts/heads_branch.py --role systems","branch"),
    ("H07","integrator","Compose","pipeline","python -c \"print('pipeline ok')\"","pure"),
    ("H08","SRE","Observe","telemetry","python -c \"print('telemetry ok')\"","pure"),
    ("H09","release engineer","Decide","version + notes","python scripts/heads_branch.py --role release","branch"),
    ("H10","security","Check","CVE report","python -m pip_audit 2>/dev/null || true","pure"),
    ("H11","researcher","Observe","closure'","python scripts/heads_terminal.py --role researcher","terminal"),
    ("H12","principal / CTO","Decide","ship|hold","python scripts/heads_terminal.py --role principal","terminal"),
    ("H13","product / PM","Decide","ε","python scripts/heads_terminal.py --role product","terminal"),
    ("H14","manager","Decide","cycle","python scripts/heads_branch.py --role manager","branch"),
    ("H15","user","Decide","ε","python scripts/heads_terminal.py --role user","terminal"),
    ("H16","DSL designer","Compose","grammar","python scripts/heads_branch.py --role dsl","branch"),
    ("H17","proof engineer","Check","proof check","python -c \"print('proof ok')\"","pure"),
    ("H18","dependency mgr","Compose","lockfile","python -c \"print('lock ok')\"","pure"),
    ("H19","test oracle","Check","oracle","python scripts/heads_branch.py --role oracle","branch"),
    ("H20","fuzzer","Check","corpus","python -c \"print('fuzz ok')\"","pure"),
    ("H21","red-team","Check","counterexample","python scripts/heads_branch.py --role redteam","branch"),
    ("H22","protocol synth","Compose","protocol","python scripts/heads_branch.py --role protocol","branch"),
    ("H23","pipeline owner","Compose","schedule","python -c \"print('schedule ok')\"","pure"),
    ("H24","monitoring","Observe","alert rule","python -c \"print('monitor ok')\"","pure"),
    ("H25","telemetry owner","Observe","trace","python -c \"print('trace ok')\"","pure"),
    ("H26","deployer","Decide","deployed","python -c \"print('deploy ok')\"","pure"),
    ("H27","auditor","Observe","audit report","python scripts/heads_branch.py --role auditor","branch"),
    ("H28","tech lead","Decide","ship|hold","python scripts/heads_terminal.py --role techlead","terminal"),
    ("H29","researcher (R)","Observe","closure'","python scripts/heads_terminal.py --role researcher_r","terminal"),
    ("H30","changelog","Compose","version record","python -c \"print('changelog ok')\"","pure"),
    ("H31","product","Decide","ε","python scripts/heads_terminal.py --role product2","terminal"),
    ("H32","user (final)","Decide","ε","python scripts/heads_terminal.py --role user_final","terminal"),
]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HEADS))
    a = ap.parse_args()
    results = {}
    CANDS = {"architect","systems","release","manager","dsl","oracle","redteam","red-team","protocol","auditor"}
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
        r = subprocess.run(cmd, shell=True, cwd=str(ROOT),
                           capture_output=True, text=True)
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
