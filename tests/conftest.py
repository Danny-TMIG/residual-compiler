"""Shared fixtures. Each test module runs against a fresh state."""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def atlas_db():
    p = ROOT / "data/atlas/atlas.sqlite"
    if not p.exists():
        import subprocess

        subprocess.run(
            [sys.executable, "src/parse_atlas.py", "data/atlas/atlas.txt"],
            cwd=ROOT,
            check=True,
        )
    return p


@pytest.fixture(scope="session")
def skills_db(atlas_db):
    p = ROOT / "data/skills.sqlite"
    if not p.exists():
        import subprocess

        subprocess.run([sys.executable, "-m", "src.cli", "seed"], cwd=ROOT, check=True)
    return p
