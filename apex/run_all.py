"""run_all.py — run every level. Exit 0 iff all pass."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
levels = [
    "level1_determinism.py",
    "level2_reproducibility.py",
    "level3_parity.py",
    "level4_falsifiability.py",
    "level5_observer.py",
    "level7_satisfiability.py",
    "level6_tapeout.py",
]

print("=" * 64)
print(f"APEX — {len(levels)} levels, minimal to absolute")
print("=" * 64)
failed = []
for level in levels:
    r = subprocess.run([sys.executable, level], cwd=str(ROOT))
    if r.returncode != 0:
        failed.append(level)

print()
if failed:
    print(f"[gap] {len(failed)} level(s) failed: {failed}")
    sys.exit(1)
print(f"[apex] all {len(levels)} levels pass")
print("  L1 determinism — emit(x) == emit(x)")
print("  L2 reproducibility — build(x) == build(x)")
print("  L3 parity — build(x) same on every OS")
print("  L4 falsifiability — every claim has a counterexample")
print("  L5 observer — UNDECIDED and REJECTED block")
print("  L6 tapeout — all layers combine into one verdict")
