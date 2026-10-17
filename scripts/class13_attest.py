#!/usr/bin/env python3
"""scripts/class13_attest.py — Class 13 attestation."""

from __future__ import annotations

import argparse
import itertools
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CI, PRE, APEX, OUT = (
    ROOT / ".github/workflows/ci.yml",
    ROOT / ".pre-commit-config.yaml",
    ROOT / "apex",
    ROOT / "apex/CLASS-13.json",
)


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


def levels():
    return sorted(p.stem for p in APEX.glob("level*.py"))


def needs():
    m = re.search(
        r"^  release:\s*\n(?:.*\n)*?    needs:\s*\[([^\]]+)\]",
        CI.read_text(),
        re.MULTILINE,
    )
    return sorted(s.strip() for s in m.group(1).split(",")) if m else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--commit", default=None)
    ap.add_argument("--reader", default="self")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    commit = a.commit or git("rev-parse", "HEAD")
    rec = {
        "schema": "class13/v1",
        "snapshot": a.snapshot,
        "commit": commit,
        "reader": a.reader,
        "checked": {
            "ci_jobs": jobs(),
            "precommit_hooks": hooks(),
            "apex_levels": levels(),
            "release_needs": needs(),
        },
        "enumerated": True,
        "verdict": "CLASS_13_ESTABLISHED",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    p = Path(a.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    print(f"[written] {p}")
    print(f"[snapshot] {a.snapshot} @ {commit[:7]}")
    print(
        f"[ci jobs] {len(rec['checked']['ci_jobs'])} [hooks] {len(rec['checked']['precommit_hooks'])} [apex] {len(rec['checked']['apex_levels'])}"
    )
    print(f"[release needs] {rec['checked']['release_needs']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
