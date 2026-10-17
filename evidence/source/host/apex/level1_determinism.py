"""Level 1 — determinism: emit(x) == emit(x), byte-for-byte."""

from __future__ import annotations

import hashlib
import json
import sys


def canonical_bytes(obj) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def hash_canonical(obj) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def verify_determinism(obj, trials: int = 100) -> bool:
    first = canonical_bytes(obj)
    for _ in range(trials - 1):
        if canonical_bytes(obj) != first:
            return False
    return True


if __name__ == "__main__":
    tests = [
        {"a": 1, "b": 2},
        {"nested": {"x": [3, 1, 2], "y": {"z": 4}}},
        {"unicode": "héllo"},
        {"empty": {}},
    ]
    ok = all(verify_determinism(t) for t in tests)
    print(f"[level 1] determinism: {'ok' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)
