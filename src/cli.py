import argparse, json, sqlite3, sys
from . import dispatch, tools, seed_skills


def _ensure_tools_for_cli():
    from . import dispatch

    dispatch._ensure_tools()


def main(argv=None):
    _ensure_tools_for_cli()
    ap = argparse.ArgumentParser(prog="atlas")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("seed")
    r = sub.add_parser("route")
    r.add_argument("query")
    r.add_argument("--limit", type=int, default=10)
    d = sub.add_parser("dispatch")
    d.add_argument("skill")
    d.add_argument("--inputs", default="{}")
    l = sub.add_parser("list")
    l.add_argument("--kind", default="skill")
    l.add_argument("--limit", type=int, default=30)
    sub.add_parser("tools")
    sub.add_parser("forbidden")
    sub.add_parser("health")
    sub.add_parser("scope")
    v = sub.add_parser("verify")
    bv = sub.add_parser("verify-bundle")
    bv.add_argument("path")
    sub.add_parser("flow-steps")
    f = sub.add_parser("run-flow")
    f.add_argument("--inputs", default="{}")
    f.add_argument("--no-stop", action="store_true")
    rs = sub.add_parser("roles")
    rs.add_argument("--subsection", default=None)
    rr = sub.add_parser("run-role")
    rr.add_argument("role")
    rr.add_argument("--inputs", default="{}")
    rr.add_argument("--stop-on-fail", action="store_true")
    rk = sub.add_parser("role-skills")
    rk.add_argument("role")
    a = ap.parse_args(argv)
    if a.cmd == "seed":
        seed_skills.main()
    elif a.cmd == "route":
        print(json.dumps(dispatch.route(a.query, a.limit), indent=2))
    elif a.cmd == "dispatch":
        print(json.dumps(dispatch.dispatch(a.skill, json.loads(a.inputs)), indent=2))
    elif a.cmd == "list":
        con = sqlite3.connect("data/atlas/atlas.sqlite")
        con.row_factory = sqlite3.Row
        for r in con.execute(
            "SELECT slug,subsection,name FROM items WHERE kind=? LIMIT ?", (a.kind, a.limit)
        ):
            print(f"{r['slug']:40} {r['subsection'] or '':30} {r['name']}")
    elif a.cmd == "tools":
        print("\n".join(sorted(tools.REG)))
    elif a.cmd == "forbidden":
        from . import compiler_limits

        print(json.dumps(compiler_limits.load_map(), indent=2))
    elif a.cmd == "health":
        from . import observability

        print(json.dumps(observability.health(), indent=2))
    elif a.cmd == "scope":
        from . import scoped, tools as T

        bound = scoped.write_scope(T.REG)
        print(f"bound: {len(bound)} tools")
        for n in bound:
            print(f"  {n}")
    elif a.cmd == "verify":
        from . import audit

        print(json.dumps(audit.verify_chain(), indent=2))
    elif a.cmd == "verify-bundle":
        from . import bundle

        print(json.dumps({"ok": bundle.verify(a.path), "path": a.path}, indent=2))
    elif a.cmd == "flow-steps":
        from . import flow

        for s in flow.flow_steps():
            print(s)
    elif a.cmd == "run-flow":
        from . import flow

        print(json.dumps(flow.run_flow(json.loads(a.inputs), stop_on_fail=not a.no_stop), indent=2))
    elif a.cmd == "roles":
        from . import roles

        for r in roles.list_roles(a.subsection):
            print(r if isinstance(r, str) else f"{r['name']:40} {r['subsection']}")
    elif a.cmd == "role-skills":
        from . import roles

        for s in roles.role_skills(a.role):
            print(f"{s['id']:45} bound={s['bound']} impl={s['impl']!r}")
    elif a.cmd == "run-role":
        from . import roles

        print(
            json.dumps(
                roles.run_role(a.role, json.loads(a.inputs), stop_on_fail=a.stop_on_fail), indent=2
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
