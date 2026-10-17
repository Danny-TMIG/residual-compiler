#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"

class Engine:
    def __init__(self):
        self.seen = {}
        self.log = []
    def tx_id(self, node, op, inputs):
        h = hashlib.sha256((node + op + "".join(sorted(inputs))).encode()).hexdigest()
        return f"tx:{h[:16]}"
    def apply(self, tx_id, fn):
        if tx_id in self.seen:
            self.log.append({"tx": tx_id, "kind": "dedup"})
            return {"status": "dedup", "result": self.seen[tx_id]}
        try:
            result = fn()
            self.seen[tx_id] = result
            self.log.append({"tx": tx_id, "kind": "applied"})
            return {"status": "applied", "result": result}
        except Exception as e:
            self.log.append({"tx": tx_id, "kind": "failed", "error": str(e)})
            return {"status": "failed", "error": str(e)}
    def report(self):
        return {"applied": sum(1 for x in self.log if x["kind"]=="applied"),
                "dedup": sum(1 for x in self.log if x["kind"]=="dedup"),
                "failed": sum(1 for x in self.log if x["kind"]=="failed"),
                "total": len(self.log)}

def main():
    e = Engine()
    tx1 = e.tx_id("node-1","RUN",["a","b"])
    tx2 = e.tx_id("node-1","RUN",["b","a"])
    assert tx1 == tx2, "tx_id not deterministic"
    r1 = e.apply(tx1, lambda: {"value": 42})
    r2 = e.apply(tx2, lambda: {"value": 99})
    assert r1["status"] == "applied"
    assert r2["status"] == "dedup"
    assert r2["result"] == {"value": 42}
    out = {"tx_deterministic": True, "report": e.report(), "log": e.log}
    print(json.dumps(out, indent=2))
    (APEX / "IDEMPOTENCY.json").write_text(json.dumps(out, indent=2) + "\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
