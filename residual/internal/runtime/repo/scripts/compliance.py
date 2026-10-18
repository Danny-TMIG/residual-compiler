#!/usr/bin/env python3
"""scripts/compliance.py — apply policies to all 32 heads."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"
POL = APEX / "POLICIES.json"
VERD = APEX / "VERDICTS.json"


def load(p: Path) -> dict:
    return json.loads(p.read_text()) if p.exists() else {}


def eval_condition(cond: str) -> bool:
    try:
        for op in (" != ", " == "):
            if op in cond:
                left, right = cond.split(op, 1)
                break
        else:
            return False
        f, path = left.split(":", 1)
        fp = ROOT / f
        if not fp.exists():
            return False
        value = load(fp)
        for k in path.split("."):
            if k == "":
                continue
            if isinstance(value, list):
                value = value[int(k)]
            elif isinstance(value, dict):
                if k not in value:
                    return False
                value = value[k]
            else:
                return False
        t = right.strip().strip("'\"")
        if t == "true":
            t = True
        elif t == "false":
            t = False
        elif t == "null":
            t = None
        if op == " != ":
            return value != t
        return value == t
    except Exception:
        return False


def apply_rule(rule: str, conds: list[str]) -> str:
    results = [eval_condition(c) for c in conds]
    if rule.startswith("ALL"):
        return "pass" if all(results) else "fail"
    if rule.startswith("ANY"):
        return "pass" if any(results) else "fail"
    if rule.startswith("SELECT"):
        return "pass" if any(results) else "escalate"
    return "escalate"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--policies", default=str(POL))
    a = ap.parse_args()
    policies = load(Path(a.policies))
    if not policies:
        print(f"[fail] {a.policies} missing or empty")
        return 1
    verdicts = {}
    for hid, pol in policies.items():
        ev = pol.get("policy", {})
        v = apply_rule(ev.get("rule", ""), ev.get("evidence", []))
        verdicts[hid] = {
            "role": pol.get("role"),
            "decision": pol.get("decision"),
            "verdict": v,
        }
    n_pass = sum(1 for x in verdicts.values() if x["verdict"] == "pass")
    n_fail = sum(1 for x in verdicts.values() if x["verdict"] == "fail")
    n_esc = sum(1 for x in verdicts.values() if x["verdict"] == "escalate")
    VERD.write_text(
        json.dumps(
            {
                "schema": "compliance/v1",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "heads": verdicts,
                "summary": {
                    "total": len(verdicts),
                    "pass": n_pass,
                    "fail": n_fail,
                    "escalate": n_esc,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    print(f"[written] {VERD}")
    for hid, v in sorted(verdicts.items()):
        mark = {"pass": "ok  ", "fail": "FAIL", "escalate": "ESC "}[v["verdict"]]
        print(f"  [{mark}] {hid} {v['role']:20s} -> {v['verdict']}")
    print(f"[summary] {n_pass} pass, {n_fail} fail, {n_esc} escalate")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
