"""
CLI: compile a task description, evaluate policy, optionally run the flow.

  python -m src.compile_cli "search for TODOs in src/tools.py"
  python -m src.compile_cli "deploy to prod" --authorities change_approved,incident_free
  python -m src.compile_cli "audit src/tools.py" --run
"""

import argparse, json, sys
from . import task_compiler, flow, contracts


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    MAX_QUERY_BYTES = 64 * 1024
    if not argv or not any(a.strip() for a in argv):
        raise ValueError("empty query")
    if sum(len(a) for a in argv) > MAX_QUERY_BYTES:
        raise ValueError(f"query too large (> {MAX_QUERY_BYTES} bytes)")
    ap = argparse.ArgumentParser(prog="compile")
    ap.add_argument("description")
    ap.add_argument("--authorities", default="")
    ap.add_argument("--actor", default=None, help="actor id (falls back to ACTOR_ID env)")
    ap.add_argument("--role", default=None, help="actor role (falls back to ACTOR_ROLE env)")
    ap.add_argument("--policy", default=None)
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args(argv)
    from . import authorities as auth_mod

    if a.authorities:
        auth = [x.strip() for x in a.authorities.split(",") if x.strip()]
        auth_src = {"actor_id": None, "actor_role": None, "matched": True, "override": True}
    else:
        auth, auth_src = auth_mod.resolve(actor_id=a.actor, actor_role=a.role)
        auth = list(auth)
    r = task_compiler.compile_task(
        a.description, authorities=auth, policy_path=a.policy, write_intent=True
    )
    r["authorities"] = {"resolved": auth, "from": auth_src}
    print(json.dumps({"compiled": r}, indent=2))
    if not r["allowed"]:
        print(f"\n[blocked] {r['blocked_reason']}", file=sys.stderr)
        return 2
    if a.run:
        d = flow.run_flow({"_default": r["default"]})
        print(
            json.dumps(
                {
                    "flow_result": d["result_state"],
                    "stages": d["stages_run"],
                    "total": d["stages_total"],
                    "bundle": d["bundle"],
                },
                indent=2,
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
