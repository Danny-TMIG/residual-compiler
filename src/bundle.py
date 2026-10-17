"""
A bundle is the full, verifiable artifact of one run: config, trace, evidence
records touched, plus a top-level sha256 over the canonical serialization.

Bundles are written to bundles/<run_id>.json and never modified in place.
"""

import hashlib, json, time, uuid
from pathlib import Path

DIR = Path("bundles")


def _canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def seal(kind, config, trace, evidence_records):
    DIR.mkdir(exist_ok=True)
    run_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + uuid.uuid4().hex[:8]
    body = {
        "run_id": run_id,
        "kind": kind,
        "config": config,
        "trace": trace,
        "evidence": evidence_records,
    }
    digest = hashlib.sha256(_canon(body).encode()).hexdigest()
    out = {**body, "sha256": digest}
    p = DIR / f"{run_id}.json"
    p.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    return {"run_id": run_id, "path": str(p), "sha256": digest}


def verify(path):
    d = json.loads(Path(path).read_text())
    digest = d.pop("sha256")
    return hashlib.sha256(_canon(d).encode()).hexdigest() == digest
