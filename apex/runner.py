#!/usr/bin/env python3
"""apex/runner.py — invoke the apex from hooks and CI.

Runs all 7 levels. Emits apex/APEX-LATEST.json with:
    - per-level verdict
    - artifact hash (of the repo tree at HEAD)
    - timestamp
    - refusals (named)
    - final verdict

Exit 0 iff all 7 levels VERIFIED. Exit 1 otherwise.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX_DIR = ROOT / "apex"
OUT = APEX_DIR / "APEX-LATEST.json"

LEVELS = [
    "level1_determinism.py",
    "level2_reproducibility.py",
    "level3_parity.py",
    "level4_falsifiability.py",
    "level5_observer.py",
    "level7_satisfiability.py",
    "level6_tapeout.py",
]


def hash_tree(root: Path) -> str:
    """Stable hash of the repo tree (excluding apex/, .git/, .venv/)."""
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if any(part in {".git", ".venv", "__pycache__", "apex", ".loop"}
               for part in rel.parts):
            continue
        if not p.is_file():
            continue
        h.update(str(rel).replace("\\", "/").encode())
        h.update(b"\0")
        h.update(p.read_bytes())
    return h.hexdigest()


def run_level(level: str) -> tuple[int, str]:
    r = subprocess.run(
        [sys.executable, str(APEX_DIR / level)],
        cwd=str(APEX_DIR),
        capture_output=True, text=True,
    )
    return r.returncode, (r.stdout + r.stderr)


def main() -> int:
    print("=" * 64)
    print("APEX RUNNER")
    print("=" * 64)

    artifact_hash = hash_tree(ROOT)
    print(f"[artifact] sha256={artifact_hash[:16]}...")

    results = {}
    refusals = []
    for level in LEVELS:
        rc, output = run_level(level)
        verdict = "VERIFIED" if rc == 0 else "REFUTED"
        results[level] = {"verdict": verdict, "exit_code": rc}
        mark = "ok" if rc == 0 else "FAIL"
        print(f"  [{mark:4}] {level}: {verdict}")
        if rc != 0:
            tail = output.strip().splitlines()[-5:] if output.strip() else []
            refusals.append({
                "level": level,
                "exit_code": rc,
                "tail": tail,
            })

    final = "VERIFIED" if all(r["verdict"] == "VERIFIED"
                              for r in results.values()) else "REFUTED"

    record = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "artifact_hash": artifact_hash,
        "levels": results,
        "refusals": refusals,
        "final": final,
    }
    APEX_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True))
    print(f"\n[written] {OUT.relative_to(ROOT)}")
    print(f"[final] {final}")
    return 0 if final == "VERIFIED" else 1


if __name__ == "__main__":
    sys.exit(main())
