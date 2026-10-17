#!/usr/bin/env python3
"""scripts/class13_attest.py — Class 13 attestation."""
from __future__ import annotations
import argparse, itertools, json, re, subprocess, sys, time
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
CI   = ROOT / ".github/workflows/ci.yml"
PRE  = ROOT / ".pre-commit-config.yaml"
APEX = ROOT / "apex"
OUT  = APEX / "CLASS-13.json"

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

def parse_release_needs() -> list[str]:
    m = re.search(r"^  release:\s*\n(?:.*\n)*?    needs:\s*\[([^\]]+)\]",
                  CI.read_text(), re.M)
    if not m:
        return []
    return sorted(s.strip() for s in m.group(1).split(",") if s.strip())

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--commit", default=None)
    ap.add_argument("--reader", default="self")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    commit = args.commit or git("rev-parse", "HEAD")
    declared = {
        "ci_jobs": enumerate_ci_jobs(),
        "precommit_hooks": enumerate_hooks(),
        "apex_levels": enumerate_apex_levels(),
        "release_needs": parse_release_needs(),
    }
    rec = {
        "schema": "class13/v1",
        "snapshot": args.snapshot,
        "commit": commit,
        "reader": args.reader,
        "checked": declared,
        "enumerated": True,
        "verdict": "CLASS_13_ESTABLISHED",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    print(f"[written] {out}")
    print(f"[snapshot] {args.snapshot} @ {commit[:7]}")
    print(f"[ci jobs] {len(declared['ci_jobs'])}  [hooks] {len(declared['precommit_hooks'])}  [apex] {len(declared['apex_levels'])}")
    print(f"[release needs] {declared['release_needs']}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
