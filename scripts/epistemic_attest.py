#!/usr/bin/env python3
"""scripts/epistemic_attest.py — Family E + F."""

from __future__ import annotations

import argparse
import itertools
import json
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CI, PRE = ROOT / ".github/workflows/ci.yml", ROOT / ".pre-commit-config.yaml"
APEX = ROOT / "apex"
EPI, C13, DEC = APEX / "EPISTEMIC.json", APEX / "CLASS-13.json", APEX / "DECISION.json"

DECLARED = {
    "A": ["A0", "A1", "A2", "A3", "A4"],
    "B": ["B0", "B1", "B2", "B3", "B4", "B5", "B6"],
    "C": ["C0", "C1", "C2", "C3", "C4"],
    "D": ["D0", "D1", "D2", "D3"],
    "E": ["E0", "E1", "E2", "E3", "E4", "D4"],
    "F": ["F0", "F1", "F2"],
}


def git(*a):
    return subprocess.run(
        ["git", *a], cwd=str(ROOT), capture_output=True, text=True, check=True
    ).stdout.strip()


def jobs():
    d = yaml.safe_load(CI.read_text()).get("jobs", {})
    out = []
    for name, spec in d.items():
        m = (spec.get("strategy") or {}).get("matrix") or {}
        if m:
            keys = list(m.keys())
            for combo in itertools.product(*(m[k] for k in keys)):
                out.append(
                    f"{name} ({', '.join(f'{k}={v}' for k, v in zip(keys, combo))})"
                )
        else:
            out.append(name)
    return sorted(out)


def hooks():
    return sorted(
        h["id"]
        for r in yaml.safe_load(PRE.read_text()).get("repos", [])
        for h in r.get("hooks", [])
        if h.get("id")
    )


def enumerate_(a):
    commit = a.commit or git("rev-parse", "HEAD")
    snap = (
        a.snapshot
        or subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    )
    reader = json.loads(C13.read_text()) if C13.exists() else None
    epi = json.loads(EPI.read_text()) if EPI.exists() else {}
    epi.update(
        {
            "schema": "epistemic/v1",
            "generated_by": "scripts/epistemic_attest.py",
            "snapshot": snap,
            "commit": commit,
            "families": {
                f: {
                    "kind": "mechanical"
                    if f in "ABCD"
                    else "oracle"
                    if f == "E"
                    else "terminal",
                    "classes": cs,
                }
                for f, cs in DECLARED.items()
            },
        }
    )
    seen = set(jobs()) | set(hooks())
    fam_obs = {
        "A": ["install", "smoke-compile", "sbom"],
        "B": ["quality", "test", "coverage", "pre-commit"],
        "C": ["verify-chain", "attest", "guard — no skipped gates", "policy-validate"],
        "D": ["version-check", "parity", "sbom"],
    }
    closed, open_ = [], []
    for f, need in fam_obs.items():
        miss = [n for n in need if n not in seen]
        if miss:
            open_.append({"family": f, "missing": miss})
        else:
            closed.append(f)
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
            "residual": []
            if (reader and reader.get("verdict") == "CLASS_13_ESTABLISHED")
            else ["E0-E4"],
        },
        "terminal": epi.get("verification", {}).get(
            "terminal", {"decision": None, "by": None, "bound_at": None}
        ),
    }
    not_made = []
    if open_:
        not_made.append({"family": "A-D", "reason": open_})
    if not reader or reader.get("verdict") != "CLASS_13_ESTABLISHED":
        not_made.append({"family": "E", "reason": "no reader attestation"})
    if not epi["verification"]["terminal"]["decision"]:
        not_made.append({"family": "F", "reason": "no terminal decision"})
    epi["claims_not_made"] = not_made
    EPI.write_text(json.dumps(epi, indent=2, sort_keys=True) + "\n")
    print(f"[written] {EPI}")
    print(f"[snapshot] {snap} @ {commit[:7]}")
    print(
        f"[mechanical] {epi['verification']['mechanical']['verdict']} ({len(closed)}/4)"
    )
    print(f"[oracle] {epi['verification']['oracle']['verdict'] or 'UNATTESTED'}")
    print(f"[terminal] {epi['verification']['terminal']['decision'] or 'UNBOUND'}")
    return 0


def bind(a):
    if a.decision not in ("ship", "hold") or not a.by:
        print("[REFUTED] need --decision ship|hold and --by NAME")
        return 1
    epi = json.loads(EPI.read_text())
    dec = {
        "schema": "terminal/v1",
        "snapshot": epi["snapshot"],
        "commit": epi["commit"],
        "decision": a.decision,
        "by": a.by,
        "reason": a.reason or "",
        "bound_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    DEC.write_text(json.dumps(dec, indent=2, sort_keys=True) + "\n")
    epi["verification"]["terminal"] = {
        "decision": dec["decision"],
        "by": dec["by"],
        "bound_at": dec["bound_at"],
    }
    epi["claims_not_made"] = [
        c for c in epi["claims_not_made"] if c.get("family") != "F"
    ]
    EPI.write_text(json.dumps(epi, indent=2, sort_keys=True) + "\n")
    print(f"[written] {DEC}")
    print(f"[bound] {dec['snapshot']} -> {dec['decision']} by {dec['by']}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="m", required=True)
    e = sub.add_parser("enumerate")
    e.add_argument("--snapshot", default=None)
    e.add_argument("--commit", default=None)
    b = sub.add_parser("bind")
    b.add_argument("--decision", required=True)
    b.add_argument("--by", required=True)
    b.add_argument("--reason", default="")
    a = ap.parse_args()
    return enumerate_(a) if a.m == "enumerate" else bind(a)


if __name__ == "__main__":
    sys.exit(main())
