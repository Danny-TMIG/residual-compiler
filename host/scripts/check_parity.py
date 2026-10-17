#!/usr/bin/env python3
"""Assert cross-platform parity: all legs must share identical subject digests."""

import json
import sys
from pathlib import Path


def load(path: Path) -> dict[str, str]:
    f = path / "attestation.json"
    if not f.exists():
        raise SystemExit(f"::error::{path.name}: missing attestation.json")
    data = json.loads(f.read_text())
    subjects = data.get("subject", [])
    if not subjects:
        raise SystemExit(f"::error::{path.name}: no subjects")
    out = {}
    for s in subjects:
        name = s.get("name")
        sha = (s.get("digest") or {}).get("sha256")
        if not name or not sha:
            raise SystemExit(f"::error::{path.name}: bad subject {s}")
        out[name] = sha
    return out


def main(root: str) -> int:
    rootp = Path(root)
    legs = {p.name: load(p) for p in sorted(rootp.iterdir()) if p.is_dir()}
    if len(legs) < 2:
        print(f"::error::need >=2 legs, got {len(legs)}")
        return 1

    names = sorted(legs)
    print(f"comparing {len(legs)} legs: {', '.join(names)}")
    failed = False

    all_subjects = set().union(*(set(v.keys()) for v in legs.values()))
    for leg, subs in legs.items():
        missing = all_subjects - set(subs.keys())  # <-- the fix: set of keys
        if missing:
            print(f"::error::{leg} missing subjects: {sorted(missing)}")
            failed = True

    for subj in sorted(all_subjects):
        digests = {leg: legs[leg].get(subj) for leg in names}
        unique = set(digests.values())
        if len(unique) > 1:
            print(f"::error::digest mismatch for '{subj}': {digests}")
            failed = True
        else:
            print(f"  OK  {subj}: {digests[names[0]]}")

    if failed:
        print("::error::parity FAILED")
        return 1
    print("parity PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "attestations"))
