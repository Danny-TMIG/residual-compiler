#!/usr/bin/env python3
"""constitution.py — 160-class constitutional state machine.

  new       : emit an empty canonical record with all 160 classes present
  validate  : check that a record uses only declared fields / statuses
  status    : print the 15-value first-class status enum

Every class is a dict. Every field is a key. Every class carries a
first-class `status` drawn from the enum in class 159. Absence of a
class on a record means "not applicable"; presence with empty fields
means "declared, not populated" — i.e. a gap, not silence.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"
CONST = json.loads((APEX / "CONSTITUTION.json").read_text())

STATUS = CONST["status_enum"]
BY_SLUG = {c["slug"]: c for c in CONST["classes"]}

def empty_record():
    rec = {}
    for c in CONST["classes"]:
        if c.get("meta"):
            continue
        slug = c["slug"]
        if c.get("enum"):
            rec[slug] = {"_enum": c["enum"], "status": "UNKNOWN"}
        else:
            rec[slug] = {f: None for f in c["fields"]}
            rec[slug]["status"] = "UNKNOWN"
    return rec

def validate(rec):
    errs = []
    for cls, body in rec.items():
        if cls not in BY_SLUG:
            errs.append(f"unknown class: {cls}")
            continue
        spec = BY_SLUG[cls]
        if not isinstance(body, dict):
            errs.append(f"{cls}: not a dict"); continue
        st = body.get("status")
        if st is not None and st not in STATUS:
            errs.append(f"{cls}: bad status {st!r}")
        if not spec.get("enum"):
            allowed = set(spec["fields"]) | {"status"}
            for k in body:
                if k not in allowed:
                    errs.append(f"{cls}: unknown field {k!r}")
    return errs

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        print(json.dumps(STATUS, indent=2)); return 0
    if cmd == "new":
        out = APEX / "RECORD.template.json"
        out.write_text(json.dumps(empty_record(), indent=2) + "\n")
        print(json.dumps({"path": str(out.relative_to(ROOT)),
                          "classes": len(BY_SLUG)}, indent=2)); return 0
    if cmd == "validate":
        p = Path(sys.argv[2]) if len(sys.argv) > 2 else APEX / "RECORD.template.json"
        if not p.exists():
            # create then validate
            p.write_text(json.dumps(empty_record(), indent=2) + "\n")
        rec = json.loads(p.read_text())
        errs = validate(rec)
        print(json.dumps({"path": str(p), "errors": errs,
                          "valid": not errs}, indent=2))
        return 0 if not errs else 1
    print("usage: constitution.py {new|validate [file]|status}"); return 2

if __name__ == "__main__":
    sys.exit(main())
