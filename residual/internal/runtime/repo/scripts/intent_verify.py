#!/usr/bin/env python3
import argparse, importlib, json, os, sys
from pathlib import Path

ROOT = Path(os.environ.get("RESIDUAL_ROOT") or Path(__file__).resolve().parents[1])
sys.path.insert(0, str(ROOT))

REG, LOAD_ERRORS = {}, []
import witnesses as _w
for mod in ["witnesses.reproducible_build", "witnesses.openapi_unchanged"]:
    try:
        importlib.import_module(mod)
    except Exception as e:
        LOAD_ERRORS.append(f"{mod}: {type(e).__name__}: {e}")
REG = dict(_w.REGISTRY)

def run(c):
    fn = REG.get(c.get("witness"))
    if not fn:
        return {**c, "verdict": "NOT_IMPLEMENTED",
                "evidence": f"witness '{c.get('witness')}' not in registry {sorted(REG)}",
                "load_errors": LOAD_ERRORS}
    ctx = {"repo": str(ROOT)}
    ctx.update(c.get("args") or {})
    try:
        return {**c, **fn(ctx)}
    except Exception as e:
        return {**c, "verdict": "ERROR", "evidence": str(e)}

ap = argparse.ArgumentParser()
ap.add_argument("--intent", required=True)
a = ap.parse_args()
intent = json.loads(Path(a.intent).read_text())
results = [run(c) for c in intent.get("success_criteria", [])]
proven = sum(1 for r in results if r.get("verdict") == "VALID")
print(json.dumps({
    "intent_id": intent.get("intent_id"),
    "results": results,
    "proven": proven,
    "total": len(results),
    "verdict": "COVERED" if proven == len(results) and proven > 0 else "OPEN",
}, indent=2))
