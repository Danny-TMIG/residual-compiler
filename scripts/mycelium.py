#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"
NP = APEX / "NODES.json"
RP = APEX / "ROUTES.json"
SP = APEX / "MYCELIUM.json"
def load(p):
    if not p.exists():
        return None
    return json.loads(p.read_text())
def ew(expr, st):
    for op in (" != ", " == "):
        if op in expr:
            l, r = expr.split(op, 1)
            v = st.get(l.strip())
            t = r.strip().strip("'")
            if t == "null":
                t = None
            if op == " != ":
                return v != t
            return v == t
    return False
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true")
    a = ap.parse_args()
    nodes = load(NP)["nodes"]
    routes = load(RP)["routes"]
    state = load(SP)
    if a.reset or not state:
        state = {"schema":"mycelium/state/v1","nodes":{},"routes_fired":[],"active_frontier":[],"solved":False}
    for n in nodes:
        n["evidence"] = sorted({r["from"] for r in routes if r["to"] == n["id"] and r["from"] != "EPS"})
    frontier = [n for n in nodes if not n["evidence"]]
    while frontier:
        n = frontier.pop(0)
        if n["id"] in state["nodes"]:
            continue
        ok = all(state["nodes"].get(d, {}).get("verdict") == "pass" for d in n["evidence"])
        entry = {"type": n["type"], "verdict": "pass" if ok else "fail"}
        if n.get("choice"):
            entry["choice"] = n["choice"]
        if n.get("decision"):
            entry["decision"] = n["decision"]
        state["nodes"][n["id"]] = entry
        for r in routes:
            if r["from"] == n["id"] and ew(r["when"], state["nodes"][n["id"]]):
                state["routes_fired"].append([r["from"], r["to"]])
                if r["to"] == "EPS":
                    state["solved"] = True
                else:
                    nxt = next((x for x in nodes if x["id"] == r["to"]), None)
                    if nxt is not None and nxt["id"] not in state["nodes"]:
                        frontier.append(nxt)
        state["active_frontier"] = [x["id"] for x in frontier]
    SP.write_text(json.dumps(state, indent=2) + "\n")
    n_pass = sum(1 for x in state["nodes"].values() if x["verdict"] == "pass")
    print(f"[mycelium] nodes={len(state['nodes'])}/{len(nodes)} pass={n_pass} routes={len(state['routes_fired'])} solved={state['solved']}")
    return 0 if state["solved"] else 1
if __name__ == "__main__":
    sys.exit(main())
