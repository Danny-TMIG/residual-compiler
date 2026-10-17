import json, time
from pathlib import Path
from .contracts import ResultState
from . import roles, tools, audit, bundle

FLOW_DB = Path("data/atlas/atlas.sqlite")
FLOW_MAP = Path("data/flow_map.json")


def flow_steps():
    import sqlite3

    con = sqlite3.connect(FLOW_DB)
    con.row_factory = sqlite3.Row
    rows = con.execute("SELECT name FROM items WHERE kind='flow_step'").fetchall()
    con.close()
    return [r["name"] for r in rows]


def role_for(stage):
    if not FLOW_MAP.exists():
        return None
    return json.loads(FLOW_MAP.read_text()).get(stage)


def run_flow(inputs=None, stop_on_fail=True):
    chain = audit.verify_chain()
    if not chain["ok"]:
        return {
            "result_state": ResultState.VERIFICATION_FAILURE.value,
            "reason": f"evidence chain broken at record {chain['at']}",
        }
    inputs = inputs or {}
    ctx = {"evidence_log": "evidence.log"}
    stages = flow_steps()
    trace = []
    seed = {}
    for stage in stages:
        role = role_for(stage)
        if not role:
            trace.append(
                {
                    "stage": stage,
                    "role": None,
                    "result_state": ResultState.NOT_RUN.value,
                    "reason": "no role mapped",
                }
            )
            continue
        step_inputs = dict(seed)
        for k, v in inputs.items():
            if k == "_default" and isinstance(v, dict):
                m = dict(step_inputs)
                m.update(v)
                step_inputs = m
            else:
                step_inputs[k] = v
        out = roles.run_role(role, step_inputs, ctx)
        trace.append(
            {
                "stage": stage,
                "role": role,
                "result_state": out.get("result_state"),
                "skills_run": out.get("skills_run"),
                "skills_bound": out.get("skills_bound"),
            }
        )
        if out.get("result_state") in (ResultState.PASS.value, ResultState.PARTIAL.value):
            for t in out.get("trace", []):
                for k, v in (t.get("detail") or {}).items():
                    seed[k] = v
        if stage == "Formalize" and isinstance(seed.get("intent"), dict):
            params = tools.call("discover-params", {"intent": seed["intent"]}, ctx)
            if params.get("result_state") == ResultState.PASS.value:
                for k in ("root", "pattern", "query", "path"):
                    if k in params:
                        seed[k] = params[k]
        hard_stop = out.get("result_state") in (
            ResultState.FAIL.value,
            ResultState.INSUFFICIENT_DATA.value,
            ResultState.INSUFFICIENT_EVIDENCE.value,
            ResultState.VERIFICATION_FAILURE.value,
            ResultState.POLICY_DENIED.value,
            ResultState.EXECUTION_FAILURE.value,
        )
        if hard_stop and stop_on_fail:
            break
    states = [t["result_state"] for t in trace if t["result_state"] != ResultState.NOT_RUN.value]
    if not states:
        agg = ResultState.NOT_RUN.value
    elif ResultState.FAIL.value in states:
        agg = ResultState.FAIL.value
    elif any(
        s in (ResultState.INSUFFICIENT_DATA.value, ResultState.INSUFFICIENT_EVIDENCE.value)
        for s in states
    ):
        agg = ResultState.INSUFFICIENT_EVIDENCE.value
    elif all(s == ResultState.PASS.value for s in states):
        agg = ResultState.PASS.value
    else:
        agg = ResultState.PARTIAL.value
    b = bundle.seal(
        kind="flow",
        config={"inputs": inputs, "stop_on_fail": stop_on_fail},
        trace=trace,
        evidence_records=[],
    )
    return {
        "flow": "universal",
        "result_state": agg,
        "stages_total": len(stages),
        "stages_run": len(trace),
        "trace": trace,
        "bundle": b,
        "ts": time.time(),
    }
