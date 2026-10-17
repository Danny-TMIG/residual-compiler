import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path


class SovereignTriadNode:
    def __init__(self, db_path="sovereign/triad.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as c:
            c.execute(
                "CREATE TABLE IF NOT EXISTS manifold_states (id INTEGER PRIMARY KEY AUTOINCREMENT, tick INTEGER, node_name TEXT, status TEXT, payload TEXT, timestamp TEXT)"
            )
            c.commit()

    def write_state(self, tick, node_name, status, payload):
        with sqlite3.connect(self.db_path) as c:
            c.execute(
                "INSERT INTO manifold_states (tick,node_name,status,payload,timestamp) VALUES (?,?,?,?,?)",
                (
                    tick,
                    node_name,
                    status,
                    json.dumps(payload),
                    datetime.now(UTC).isoformat(),
                ),
            )
            c.commit()

    def run_codeql_invariant_check(self):
        with sqlite3.connect(self.db_path) as c:
            return (
                c.execute(
                    "SELECT COUNT(*) FROM manifold_states WHERE status='ERROR'"
                ).fetchone()[0]
                == 0
            )
