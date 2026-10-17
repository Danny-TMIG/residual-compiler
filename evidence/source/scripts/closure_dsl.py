#!/usr/bin/env python3
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"

def parse(text):
    m = re.search(r"closure\s+(\w+)\s*\{", text)
    if not m:
        return {"error": "no closure block"}
    name = m.group(1)
    obls = re.findall(
        r"\{\s*id:\s*\"([^\"]+)\",\s*check:\s*\"([^\"]+)\",\s*falsify:\s*\"([^\"]+)\"\s*\}",
        text,
    )
    obligations = [{"id": i, "check": c, "falsify": f} for i, c, f in obls]
    strat_m = re.search(r"strategy:\s*\"([^\"]+)\"", text)
    strategy = strat_m.group(1) if strat_m else None
    ev_m = re.search(r"evidence_required:\s*\[([^\]]*)\]", text)
    evidence = re.findall(r"\"([^\"]+)\"", ev_m.group(1)) if ev_m else []
    age_m = re.search(r"max_age:\s*\"([^\"]+)\"", text)
    max_age = age_m.group(1) if age_m else None
    errors = []
    if not obligations: errors.append("no obligations")
    if not strategy: errors.append("no strategy")
    elif not re.match(r"^(ALL|ANY|N_OF_M\(\d+\))$", strategy):
        errors.append(f"invalid strategy: {strategy}")
    if not evidence: errors.append("no evidence_required")
    if not max_age: errors.append("no max_age")
    for o in obligations:
        if not o.get("falsify"):
            errors.append(f"obligation {o['id']} missing falsify")
    return {"name": name, "obligations": obligations, "strategy": strategy,
            "evidence_required": evidence, "max_age": max_age,
            "errors": errors, "valid": len(errors) == 0}

def evaluate(profile, evidence_present):
    if not profile.get("valid"):
        return {"verdict": "invalid", "errors": profile.get("errors")}
    missing = [e for e in profile["evidence_required"] if e not in evidence_present]
    if missing:
        return {"verdict": "missing_evidence", "missing": missing}
    n = len(profile["obligations"])
    return {"verdict": "closed", "total": n}

def main():
    sample = (
        'closure SoftwareClosure {\n'
        '  obligations: [\n'
        '    { id: "tests", check: "pytest -q exit 0", falsify: "pytest exit != 0" },\n'
        '    { id: "mypy", check: "mypy exit 0", falsify: "mypy exit != 0" },\n'
        '    { id: "apex", check: "final == VERIFIED", falsify: "final == REFUTED" }\n'
        '  ]\n'
        '  strategy: "ALL"\n'
        '  evidence_required: ["apex", "class13", "decision"]\n'
        '  max_age: "24h"\n'
        '}\n'
    )
    p = parse(sample)
    r = evaluate(p, {"apex", "class13", "decision"})
    out = {"parsed": p, "evaluated": r}
    print(json.dumps(out, indent=2))
    (APEX / "CLOSURE-PARSED.json").write_text(json.dumps(out, indent=2) + "\n")
    return 0 if p["valid"] and r["verdict"] == "closed" else 1

if __name__ == "__main__":
    sys.exit(main())
