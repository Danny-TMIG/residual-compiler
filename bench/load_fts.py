"""Benchmark residuals.for_task scaling. Not a load generator.

Usage: python bench/load_fts.py [max_tokens]
"""

import statistics
import sys
import time

import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src import residuals

SIZES = [10, 100, 1_000, 10_000]
REPEATS = 5
BUDGET_MS = 2_000  # fail if median at max size exceeds this


def bench(n_tokens: int) -> tuple[float, int]:
    query = " ".join(["terminates"] * n_tokens)
    samples, last_hits = [], 0
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        hits = residuals.for_task(query)
        samples.append(time.perf_counter() - t0)
        last_hits = len(hits)
    return statistics.median(samples), last_hits


def main(argv):
    sizes = SIZES
    if len(argv) > 1:
        sizes = [int(argv[1])]
    worst = 0.0
    for n in sizes:
        med, hits = bench(n)
        worst = max(worst, med)
        print(f"tokens={n:>6}  median={med*1000:8.2f} ms  hits={hits}")
    if worst * 1000 > BUDGET_MS:
        print(
            f"FAIL: worst median {worst*1000:.1f} ms > {BUDGET_MS} ms", file=sys.stderr
        )
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
