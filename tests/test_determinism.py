"""Determinism: seeding twice produces byte-identical artifacts."""

import hashlib
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _fresh_seed() -> str:
    db = ROOT / "data" / "skills.sqlite"
    if db.exists():
        db.unlink()
    env = dict(os.environ, PYTHONHASHSEED="0")
    subprocess.run(
        [sys.executable, "-c", "import src.seed_skills as s; s.main()"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
    )
    return _sha(db)


def test_skills_db_deterministic():
    a = _fresh_seed()
    b = _fresh_seed()
    assert a == b, f"skills.sqlite not deterministic: {a} != {b}"


def test_skills_sidecar_matches():
    db = ROOT / "data" / "skills.sqlite"
    sidecar = ROOT / "data" / "skills.sqlite.sha256"
    if sidecar.exists():
        assert sidecar.read_text().strip() == _sha(db)
