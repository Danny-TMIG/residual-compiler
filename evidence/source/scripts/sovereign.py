#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"
NODES_PATH = APEX / "SOVEREIGN-NODES.json"
ROUTES_PATH = APEX / "SOVEREIGN-ROUTES.json"
STATE_PATH = APEX / "SOVEREIGN-STATE.json"


def load_json(path):
    if not path.exists():
        return None
    return json.loads(path.read_text())


def eval_when(expr, st):
    for op in (" != ", " == "):
        if op in expr:
            left, right = expr.split(op, 1)
            left = left.strip()
            right = right.strip().strip("'")
            value = st.get(left)
            if right == "null":
                right = None
            if op == " != ":
                return value != right
            return value == right
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true")
    args = ap.parse_args()
    nodes = load_json(NODES_PATH)["nodes"]
    routes = load_json(ROUTES_PATH)["routes"]
    state = load_json(STATE_PATH)
    if args.reset or state is None:
        state = {
            "schema": "sovereign/state/v1",
            "nodes": {},
            "routes_fired": [],
            "active_frontier": [],
            "solved": False,
        }
    for n in nodes:
        n["evidence"] = sorted(
            {r["from"] for r in routes if r["to"] == n["id"] and r["from"] != "EPS"}
        )
    frontier = [n for n in nodes if not n["evidence"]]
    while frontier:
        n = frontier.pop(0)
        if n["id"] in state["nodes"]:
            continue
        ok = all(
            state["nodes"].get(d, {}).get("verdict") == "pass" for d in n["evidence"]
        )
        entry = {"type": n["type"], "verdict": "pass" if ok else "fail"}
        if n["terminal"]:
            entry["decision"] = None
        state["nodes"][n["id"]] = entry
        for r in routes:
            if r["from"] == n["id"] and eval_when(r["when"], state["nodes"][n["id"]]):
                state["routes_fired"].append([r["from"], r["to"]])
                if r["to"] == "EPS":
                    state["solved"] = True
                else:
                    nxt = next((x for x in nodes if x["id"] == r["to"]), None)
                    if nxt is not None and nxt["id"] not in state["nodes"]:
                        frontier.append(nxt)
        state["active_frontier"] = [x["id"] for x in frontier]
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")
    n_pass = sum(1 for x in state["nodes"].values() if x["verdict"] == "pass")
    print(
        "[sovereign] nodes=%d/%d pass=%d routes=%d solved=%s"
        % (
            len(state["nodes"]),
            len(nodes),
            n_pass,
            len(state["routes_fired"]),
            state["solved"],
        )
    )
    return 0 if state["solved"] else 1


if __name__ == "__main__":
    sys.exit(main())
