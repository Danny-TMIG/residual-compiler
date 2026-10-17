"""
Append-only evidence log with per-record and chain hashes.

Each record: {ts, kind, payload, prev, hash}
- prev: the hash of the previous record (or "" for the first)
- hash: sha256(canonical_json({ts,kind,payload,prev}))

Audit trail can be verified end-to-end with verify_chain().
"""

import hashlib, json, time
from pathlib import Path

LOG = Path("evidence.log")
GENESIS = ""


def _canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(rec):
    return hashlib.sha256(
        _canon({k: rec[k] for k in ("ts", "kind", "payload", "prev")}).encode()
    ).hexdigest()


def _last_hash():
    if not LOG.exists():
        return GENESIS
    with LOG.open("r", encoding="utf-8") as f:
        last = None
        for line in f:
            line = line.strip()
            if line:
                last = line
    if not last:
        return GENESIS
    try:
        return json.loads(last)["hash"]
    except Exception:
        return GENESIS


def append(kind, payload):
    rec = {"ts": time.time(), "kind": kind, "payload": payload, "prev": _last_hash()}
    rec["hash"] = _hash(rec)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(_canon(rec) + "\n")
    return rec


def verify_chain(path=LOG):
    p = Path(path)
    if not p.exists():
        return {"ok": True, "records": 0}
    prev = GENESIS
    n = 0
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            n += 1
            if rec.get("prev") != prev:
                return {"ok": False, "at": n, "reason": "prev mismatch"}
            expect = _hash(rec)
            if rec.get("hash") != expect:
                return {"ok": False, "at": n, "reason": "hash mismatch"}
            prev = rec["hash"]
    return {"ok": True, "records": n}
