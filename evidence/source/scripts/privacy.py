#!/usr/bin/env python3
"""privacy.py — minimal GDPR/ISO 27701 posture.

Commands:
  records   -> write apex/PRIVACY-RECORDS.json (Art. 30)
  retention -> report candidate records older than --days N
  export    -> sha256-based export stub for a subject id
"""
import hashlib, json, sys, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"

RECORDS = {
    "controller": "local operator (unnamed)",
    "purposes": [
        {"purpose": "model inference on local prompts",
         "lawful_basis": "legitimate interest (Art. 6(1)(f)) — UNVERIFIED"},
        {"purpose": "audit log of resolutions",
         "lawful_basis": "legitimate interest — UNVERIFIED"},
    ],
    "categories_of_data": ["prompt text", "timestamps", "model outputs"],
    "recipients": ["none (local)"],
    "transfers": "none (no cross-border)",
    "retention": "NOT IMPLEMENTED — see `retention`",
    "security_measures": ["local-only", "software hash chain"],
    "dsr_contact": "not configured",
    "standard": ["GDPR Art. 30", "ISO/IEC 27554"],
    "ring": 2,
    "note": "Declared, not verified. Retention and DSR endpoints are absent.",
}

def write_records():
    out = APEX / "PRIVACY-RECORDS.json"
    out.write_text(json.dumps(RECORDS, indent=2) + "\n")
    print(json.dumps({"path": str(out.relative_to(ROOT)), "ring": 2}, indent=2))

def retention(days):
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    chain = APEX / "PROVENANCE.json"
    if not chain.exists():
        print(json.dumps({"chain": "absent"}, indent=2)); return
    data = json.loads(chain.read_text())
    old = [r for r in data.get("chain", data.get("records", []))
           if r.get("ts") and r["ts"] < cutoff.isoformat()]
    print(json.dumps({"candidates": len(old), "cutoff": cutoff.isoformat(),
                      "note": "purge not implemented — report only"}, indent=2))

def export(subject):
    print(json.dumps({
        "subject_sha256": hashlib.sha256(subject.encode()).hexdigest(),
        "status": "stub", "note": "not implemented",
    }, indent=2))

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "records"
    if cmd == "records": write_records()
    elif cmd == "retention":
        days = int(sys.argv[sys.argv.index("--days")+1]) if "--days" in sys.argv else 30
        retention(days)
    elif cmd == "export":
        export(sys.argv[2] if len(sys.argv) > 2 else "unknown")
    else:
        print("usage: privacy.py {records|retention --days N|export SUBJECT}")
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
