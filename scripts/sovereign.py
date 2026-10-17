#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT/"apex"
N = APEX/"SOVEREIGN-NODES.json"; R = APEX/"SOVEREIGN-ROUTES.json"; S = APEX/"SOVEREIGN-STATE.json"

def load(p): return json.loads(p.read_text()) if p.exists() else None

def eval_when(expr, st):
    for op in (" != ", " == "):
        if op in expr:
            l, r = expr.split(op, 1)
            v = st.get(l.strip()); t = r.strip().strip("'\"")
            if t == "null": t = None
            return (v != t) if op == " != " else (v == t)
    return False

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--reset", action="store_true"); a = ap.parse_args()
    nodes = load(N)["nodes"]; routes = load(R)["routes"]
    state = {"schema":"sovereign/state/v1","nodes":{},"routes_fired":[],"active_frontier":[],"solved":False} if (a.reset or not load(S)) else load(S)

    for n in nodes:
        n["evidence"] = sorted({r["from"] for r in routes if r["to"] == n["id"] and r["from"] != "ε"})

    frontier = [n for n in nodes if not n["evidence"]]
    while frontier:
        n = frontier.pop(0)
        if n["id"] in state["nodes"]: continue
        verdict = "pass" if all(state["nodes"].get(d, {}).get("verdict")=="pass" for d in n["evidence"]) else "fail"
        entry = {"type":n["type"],"verdict":verdict}
        if n["terminal"]:
            entry["decision"] = None
        state["nodes"][n["id"]] = entry
        for r in routes:
            if r["from"] == n["id"] and eval_when(r["when"], state["nodes"][n["id"]]):
                state["routes_fired"].append([r["from"], r["to"]])
                if r["to"] == "ε":
                    state["solved"] = True
                else:
                    nxt = next((x for x in nodes if x["id"] == r["to"]), None)
                    if nxt and nxt["id"] not in state["nodes"]: frontier.append(nxt)
        state["active_frontier"] = [x["id"] for x in frontier]

    S.write_text(json.dumps(state, indent=2))
    n_pass = sum(1 for x in state["nodes"].values() if x["verdict"]=="pass")
    n_term = sum(1 for k in state["nodes"] if k in {n["id"] for n in nodes if n["terminal"]})
    print(f"[sovereign] nodes={len(state['nodes'])}/{len(nodes)}  pass={n_pass}  terminal={n_term}  routes={len(state['routes_fired'])}  solved={state['solved']}")
    return 0 if state["solved"] else 1

if __name__ == "__main__":
    sys.exit(main())
