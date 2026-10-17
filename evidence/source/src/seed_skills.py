"""seed_skills: deterministic skill database. Contract:
- writes data/skills.sqlite with a fixed schema and fixed rows
- writes data/skills.sqlite.sha256 = sha256(db bytes)
- byte-identical on every run (sorted keys, no timestamps)
"""

import hashlib
import sqlite3
from pathlib import Path

DATA = Path("data")
DB = DATA / "skills.sqlite"
SIDECAR = DATA / "skills.sqlite.sha256"

SKILLS = [
    (1, "audit", "scan items for duplicates/missing ids"),
    (2, "bundle", "deterministic JSON serialization"),
    (3, "compile", "task spec -> residual descriptor"),
    (4, "dispatch", "apply handler to each item"),
    (5, "policy", "match ids against allowed set"),
    (6, "scoped", "namespace-bound handler execution"),
    (7, "flow", "chain items through steps"),
    (8, "bind_all", "bind handlers by item id"),
    (9, "contracts", "skill contract validation"),
    (10, "telemetry", "prometheus-style counters"),
]


def build(db_path: Path) -> bytes:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    with sqlite3.connect(db_path) as c:
        c.execute(
            "CREATE TABLE skills (id INTEGER PRIMARY KEY, name TEXT NOT NULL, purpose TEXT NOT NULL)"
        )
        c.executemany("INSERT INTO skills VALUES (?,?,?)", SKILLS)
        c.commit()
    return db_path.read_bytes()


def main() -> int:
    data = build(DB)
    SIDECAR.write_text(hashlib.sha256(data).hexdigest())
    print(f"seeded {len(SKILLS)} skills -> {DB} sha256={SIDECAR.read_text()[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
