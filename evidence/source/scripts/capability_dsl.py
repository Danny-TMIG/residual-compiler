#!/usr/bin/env python3
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"

def parse(text):
    m = re.search(r"capability\s+(\w+)\s*\{([^}]+)\}", text)
    if not m:
        return {"error": "no capability block"}
    name = m.group(1); body = m.group(2)
    in_m = re.search(r"inputs:\s*\[([^\]]*)\]", body)
    out_m = re.search(r"outputs:\s*\[([^\]]*)\]", body)
    layer_m = re.search(r"layer_bound:\s*(\d+)", body)
    ev_m = re.search(r"evidence:\s*\"([^\"]+)\"", body)
    inputs = re.findall(r"\"([^\"]+)\"", in_m.group(1)) if in_m else []
    outputs = re.findall(r"\"([^\"]+)\"", out_m.group(1)) if out_m else []
    layer = int(layer_m.group(1)) if layer_m else None
    ev = ev_m.group(1) if ev_m else None
    errors = []
    if not inputs: errors.append("no inputs")
    if not outputs: errors.append("no outputs")
    if layer is None: errors.append("no layer_bound")
    if not ev: errors.append("no evidence_of_possession")
    return {"name": name, "inputs": inputs, "outputs": outputs,
            "layer_bound": layer, "evidence": ev, "errors": errors, "valid": len(errors)==0}

def check(provider, consumer):
    if not provider.get("valid") or not consumer.get("valid"):
        return {"compatible": False, "reason": "invalid capability"}
    missing = [i for i in consumer["inputs"] if i not in provider["outputs"]]
    if missing:
        return {"compatible": False, "missing": missing}
    if provider["layer_bound"] < consumer["layer_bound"]:
        return {"compatible": False, "reason": f"layer {provider['layer_bound']} < {consumer['layer_bound']}"}
    return {"compatible": True, "provider": provider["name"], "consumer": consumer["name"]}

def main():
    p = parse(
        'capability GenA {\n'
        '  inputs: ["File", "Spec"]\n'
        '  outputs: ["Artifact", "Hash"]\n'
        '  layer_bound: 5\n'
        '  evidence: "ev-gen-a"\n'
        '}\n'
    )
    c = parse(
        'capability UseA {\n'
        '  inputs: ["Artifact"]\n'
        '  outputs: ["Result"]\n'
        '  layer_bound: 5\n'
        '  evidence: "ev-use-a"\n'
        '}\n'
    )
    compat = check(p, c)
    out = {"provider": p, "consumer": c, "compat": compat}
    print(json.dumps(out, indent=2))
    (APEX / "CAPABILITY.json").write_text(json.dumps(out, indent=2) + "\n")
    return 0 if compat["compatible"] else 1

if __name__ == "__main__":
    sys.exit(main())
