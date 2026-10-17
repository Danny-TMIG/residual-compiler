#!/usr/bin/env python3
import hashlib, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"

def sha(b):
    return hashlib.sha256(b).hexdigest()

def leaf(data):
    return {"hash": sha(data), "data_len": len(data),
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

def node(inputs, op):
    combined = op + ":" + "".join(sorted(inputs))
    return {"hash": sha(combined.encode()), "op": op, "inputs": inputs,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

def verify(chain):
    violations = []
    for i, r in enumerate(chain):
        if "inputs" not in r:
            continue
        expected = sha((r["op"] + ":" + "".join(sorted(r["inputs"]))).encode())
        if r["hash"] != expected:
            violations.append({"index": i, "kind": "hash_mismatch"})
    return {"records": len(chain), "violations": violations,
            "verdict": "VALID" if not violations else "INVALID"}

def main():
    l = leaf(b"hello world")
    t1 = node([l["hash"]], "TRANSFORM")
    t2 = node([t1["hash"]], "ATTEST")
    chain = [l, t1, t2]
    result = verify(chain)
    result["chain"] = chain
    print(json.dumps(result, indent=2))
    (APEX / "PROVENANCE.json").write_text(json.dumps(result, indent=2) + "\n")
    return 0 if result["verdict"] == "VALID" else 1

if __name__ == "__main__":
    sys.exit(main())
