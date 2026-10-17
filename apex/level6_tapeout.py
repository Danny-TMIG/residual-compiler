"""Level 6 — tapeout: combine all layers into one verdict."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from level1_determinism import verify_determinism
from level2_reproducibility import build_tarball, verify_reproducible
from level3_parity import verify_parity
from level4_falsifiability import Claim, Exhaustive, Refutation, verify
from level5_observer import observe


def tapeout(
    files: dict[str, bytes], observer, observer_id: str, log_path: Path
) -> tuple[str, str]:
    # Level 1: determinism
    for name, content in files.items():
        if not verify_determinism({"name": name, "size": len(content)}):
            return "REFUTED", f"level1 determinism: {name}"

    # Level 2: reproducibility
    if not verify_reproducible(files):
        return "REFUTED", "level2 reproducibility"

    # Level 3: parity
    if not verify_parity(files):
        return "REFUTED", "level3 parity"

    # Level 4: falsifiability of the spec
    claims = (
        Claim("determinism", lambda x: x[0] == x[1], (("a", "a"), ("a", "b")), "L1"),
        Claim(
            "reproducibility",
            lambda x: x[0] == x[1],
            ((b"x", b"x"), (b"x", b"y")),
            "L2",
        ),
        Claim("parity", lambda x: len(x) == 1, (("a",), ("a", "b")), "L3"),
    )
    results = verify(claims, Exhaustive(domain=(0, 1)))
    # Level 4 was verified separately. Here we only need the claims to be
    # falsifiable (they have counterexamples) — not VERIFIED. The artifact
    # is what gets verified by the observer at the next level.
    if not all(r == Refutation.REFUTED for r in results.values()):
        return "REFUTED", "level4: some claim is unfalsifiable"

    # Level 5: observer
    artifact = {
        "files": sorted(files),
        "tarball_sha256": __import__("hashlib")
        .sha256(build_tarball(files))
        .hexdigest(),
        "levels_verified": ["L1", "L2", "L3", "L4"],
    }
    try:
        disp = observe(artifact, observer, observer_id, log_path)
        disp.require_accepted()
        return "VERIFIED", "all levels + observer ACCEPTED"
    except PermissionError as e:
        return "REFUTED", str(e)


if __name__ == "__main__":
    files = {
        "src/__init__.py": b"__version__ = '1.0.0'\n",
        "src/main.py": b"def main():\n    return 42\n",
        "pyproject.toml": b"[project]\nname = 'demo'\n",
    }

    with tempfile.TemporaryDirectory() as td:
        td: Path = Path(td)

        # ACCEPTED
        status, reason = tapeout(
            files, lambda a: "ACCEPTED", "obs-1", Path(td) / "log1.jsonl"
        )
        print(
            f"  [{'ok' if status == 'VERIFIED' else 'FAIL'}] tapeout ACCEPTED -> {status}: {reason}"
        )
        if status != "VERIFIED":
            sys.exit(1)

        # REJECTED
        status, reason = tapeout(
            files, lambda a: "REJECTED", "obs-1", Path(td) / "log2.jsonl"
        )
        print(
            f"  [{'ok' if status == 'REFUTED' else 'FAIL'}] tapeout REJECTED -> {status}: {reason}"
        )
        if status != "REFUTED":
            sys.exit(1)

        # UNDECIDED
        status, reason = tapeout(
            files, lambda a: "UNDECIDED", "obs-1", Path(td) / "log3.jsonl"
        )
        print(
            f"  [{'ok' if status == 'REFUTED' else 'FAIL'}] tapeout UNDECIDED -> {status}: {reason}"
        )
        if status != "REFUTED":
            sys.exit(1)

    print("[level 6] tapeout: ok")
