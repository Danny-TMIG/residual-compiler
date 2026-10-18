#!/usr/bin/env python3
import hashlib, json, os
from pathlib import Path
ROOT = Path(os.environ.get("RESIDUAL_ROOT") or Path(__file__).resolve().parents[1])
def chain(p):
    if not p.exists(): return {"intact": True, "records": 0}
    prev, n = "", 0
    for i, line in enumerate(p.read_text().strip().splitlines()):
        e = json.loads(line); h = e.pop("hash", None)
        if e.get("prev_hash") != prev: return {"intact": False, "break_at": i, "records": n}
        if hashlib.sha256(json.dumps(e, sort_keys=True).encode()).hexdigest() != h:
            return {"intact": False, "break_at": i, "records": n}
        prev = h; n += 1
    return {"intact": True, "records": n}
rec = ROOT / "apex" / "RECORD.jsonl"
cp  = ROOT / "apex" / "CONFORMANCE.json"
conf = json.loads(cp.read_text()) if cp.exists() else {}
print(json.dumps({"chain": chain(rec), "conformance": conf,
                  "pass": conf.get("pass",0)==conf.get("total",0) and chain(rec)["intact"]}, indent=2))
