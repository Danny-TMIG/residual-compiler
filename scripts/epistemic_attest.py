#!/usr/bin/env python3
"""scripts/epistemic_attest.py — Family E + F attestation."""
from __future__ import annotations
import argparse, itertools, json, re, subprocess, sys, time
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
CI   = ROOT / ".github/workflows/ci.yml"
PRE  = ROOT / ".pre-commit-config.yaml"
APEX = ROOT / "apex"
EPI  = APEX / "EPISTEMIC.json"
C13  = APEX / "CLASS-13.json"
DEC  = APEX / "DECISION.json"

DECLARED = {
    "A": ["A0","A1","A2","A3","A4"],
    "B": ["B0","B1","B2","B3","B4","B5","B6"],
    "C": ["C0","C1","C2","C3","C4"],
    "D": ["D0","D1","D2","D3"],
    "E": ["E0","E1","E2","E3","E4","D4"],
    "F": ["F0","F1","F2"],
}
MECH = {"A","B","C","D"}
ORACLE = {"E"}
TERM = {"F"}

def git(*a: str) -> str:
    return subprocess.run(["git", *a], cwd=str(ROOT),
                          capture_output=True, text=True, check=True).stdout.strip()

def enumerate_ci_jobs() -> list[str]:
    jobs = yaml.safe_load(CI.read_text()).get("jobs", {})
    names: list[str] = []
    for name, spec in jobs.items():
        matrix = (spec.get("strategy") or {}).get("matrix") or {}
        if matrix:
            keys = list(matrix.keys())
            for combo in itertools.product(*(matrix[k] for k in keys)):
                suffix = ", ".join(f"{k}={v}" for k, v in zip(keys, combo))
                names.append(f"{name} ({suffix})")
        else:
            names.append(name)
    return sorted(names)

def enumerate_hooks() -> list[str]:
    ids = []
    for repo in yaml.safe_load(PRE.read_text()).get("repos", []):
        for h in repo.get("hooks", []):
            if h.get("id"):
                ids.append(h["id"])
    return sorted(ids)

def enumerate_apex_levels() -> list[str]:
    return sorted(p.stem for p in APEX.glob("level*.py"))

def check_completeness() -> dict:
    epi = json.loads(EPI.read_text()) if EPI.exists() else {"families": {}}
    declared = {c for cs in DECLARED.values() for c in cs}
    enumerated = {c for s in epi.get("families", {}).values() for c in s.get("classes", [])}
    return {
        "missing": sorted(declared - enumerated),
        "extra": sorted(enumerated - declared),
        "complete": declared == enumerated,
    }

def mode_enumerate(args) -> int:
    commit = args.commit or git("rev-parse", "HEAD")
    snapshot = args.snapshot or subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        cwd=str(ROOT), capture_output=True, text=True, check=True
    ).stdout.strip()
    reader = json.loads(C13.read_text()) if C13.exists() else None
    epi = json.loads(EPI.read_text()) if EPI.exists() else {}
    epi["schema"] = "epistemic/v1"
    epi["generated_by"] = "scripts/epistemic_attest.py"
    epi["snapshot"] = snapshot
    epi["commit"] = commit
    epi["families"] = {
        fam: {
            "kind": "mechanical" if fam in MECH else
                    "oracle" if fam in ORACLE else "terminal",
            "classes": classes,
        }
        for fam, classes in DECLARED.items()
    }
    jobs = set(enumerate_ci_jobs()) | set(enumerate_hooks())
    fam_obs = {
        "A": ["install", "smoke-compile", "sbom"],
        "B": ["quality", "test", "coverage", "pre-commit"],
        "C": ["verify-chain", "attest", "guard — no skipped gates", "policy-validate"],
        "D": ["version-check", "parity", "sbom"],
    }
    closed, open_ = [], []
    for fam, needed in fam_obs.items():
        present = [n for n in needed if any(n in j for j in jobs) or n in jobs]
        missing = [n for n in needed if n not in present]
        if not missing:
            closed.append(fam)
        else:
            open_.append({"family": fam, "missing": missing})
    epi["verification"] = {
        "mechanical": {
            "closed": closed,
            "open": open_,
            "verdict": "VERIFIED" if not open_ else "REFUTED",
        },
        "oracle": {
            "reader": reader.get("reader") if reader else None,
            "verdict": reader.get("verdict") if reader else None,
            "attested_at": reader.get("timestamp") if reader else None,
            "residual": [] if (reader and reader.get("verdict") == "CLASS_13_ESTABLISHED") else ["E0-E4"],
        },
        "terminal": epi.get("verification", {}).get("terminal",
            {"decision": None, "by": None, "bound_at": None}),
    }
    not_made = []
    if open_:
        not_made.append({"family": "A-D", "reason": open_})
    if not reader or reader.get("verdict") != "CLASS_13_ESTABLISHED":
        not_made.append({"family": "E", "reason": "no reader attestation"})
    if not epi["verification"]["terminal"]["decision"]:
        not_made.append({"family": "F", "reason": "no terminal decision bound"})
    epi["claims_not_made"] = not_made

    comp = check_completeness()
    if not comp["complete"]:
        print(f"[REFUTED] E2 — missing {comp['missing']}, extra {comp['extra']}")
        return 1

    EPI.write_text(json.dumps(epi, indent=2, sort_keys=True) + "\n")
    print(f"[written] {EPI}")
    print(f"[snapshot] {snapshot} @ {commit[:7]}")
    print(f"[mechanical] {epi['verification']['mechanical']['verdict']} ({len(closed)}/4)")
    print(f"[oracle] {epi['verification']['oracle']['verdict'] or 'UNATTESTED'}")
    print(f"[terminal] {epi['verification']['terminal']['decision'] or 'UNBOUND'}")
    print(f"[E2] complete: {comp['complete']}")
    return 0

def mode_bind(args) -> int:
    if args.decision not in ("ship", "hold"):
        print(f"[REFUTED] decision must be ship|hold")
        return 1
    if not args.by:
        print("[REFUTED] --by required")
        return 1
    epi = json.loads(EPI.read_text())
    dec = {
        "schema": "terminal/v1",
        "snapshot": epi["snapshot"],
        "commit": epi["commit"],
        "decision": args.decision,
        "by": args.by,
        "reason": args.reason or "",
        "bound_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    DEC.write_text(json.dumps(dec, indent=2, sort_keys=True) + "\n")
    epi["verification"]["terminal"] = {
        "decision": dec["decision"],
        "by": dec["by"],
        "bound_at": dec["bound_at"],
    }
    epi["claims_not_made"] = [c for c in epi["claims_not_made"] if c.get("family") != "F"]
    EPI.write_text(json.dumps(epi, indent=2, sort_keys=True) + "\n")
    print(f"[written] {DEC}")
    print(f"[bound] {dec['snapshot']} -> {dec['decision']} by {dec['by']}")
    return 0

def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    e = sub.add_parser("enumerate"); e.add_argument("--snapshot", default=None); e.add_argument("--commit", default=None)
    b = sub.add_parser("bind"); b.add_argument("--decision", required=True); b.add_argument("--by", required=True); b.add_argument("--reason", default="")
    args = ap.parse_args()
    return mode_enumerate(args) if args.mode == "enumerate" else mode_bind(args)

if __name__ == "__main__":
    sys.exit(main())
