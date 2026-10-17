import json, sqlite3
from pathlib import Path
from .contracts import ResultState, SkillContract, normalize_result, validate_contract
from . import tools, runtime, audit

DB = Path("data/atlas/atlas.sqlite")
SK = Path("data/skills.sqlite")
EV = Path("evidence.log")


def _ensure_tools():
    try:
        from . import bind_all  # registers all skill-tools via @tools.register
    except Exception:
        pass


def route(query, limit=10):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT i.id,i.kind,i.section,i.subsection,i.name,i.slug "
        "FROM items_fts f JOIN items i ON i.rowid=f.rowid "
        "WHERE items_fts MATCH ? ORDER BY rank LIMIT ?",
        (" OR ".join(query.split()), limit),
    ).fetchall()
    con.close()
    return [dict(r) for r in rows]


def init():
    if SK.exists():
        return
    con = sqlite3.connect(SK)
    con.execute("CREATE TABLE skills(id TEXT PRIMARY KEY, contract TEXT)")
    con.commit()
    con.close()


def bind(c):
    init()
    e = validate_contract(c)
    if e:
        raise ValueError("; ".join(e))
    con = sqlite3.connect(SK)
    con.execute(
        "INSERT OR REPLACE INTO skills VALUES(?,?)", (c.identifier, json.dumps(c.as_dict()))
    )
    con.commit()
    con.close()


def get(sid):
    init()
    con = sqlite3.connect(SK)
    # 1. exact match
    r = con.execute("SELECT contract FROM skills WHERE id=?", (sid,)).fetchone()
    if not r:
        # 2. all prefix matches
        rows = con.execute(
            "SELECT id, contract FROM skills WHERE id LIKE ?", (sid + "__%",)
        ).fetchall()
        if len(rows) == 1:
            r = rows[0]
        elif len(rows) > 1:
            # 3. prefer a bound one, then the first alphabetically
            bound = [(i, c) for i, c in rows if json.loads(c).get("impl")]
            r = (bound or sorted(rows))[0]
    con.close()
    return SkillContract(**json.loads(r[1] if len(r) > 1 else r[0])) if r else None


def _check(inp, spec):
    bad = []
    for k, t in spec.items():
        if k not in inp:
            bad.append(f"missing {k}")
            continue
        v = inp[k]
        ok = (
            (t == "string" and isinstance(v, str))
            or (t == "int" and isinstance(v, int))
            or (t == "list[string]" and isinstance(v, list) and all(isinstance(x, str) for x in v))
            or (t in ("json", "obj") and isinstance(v, (dict, list)))
            or (t == "path" and isinstance(v, str))
        )
        if not ok:
            bad.append(f"{k} must be {t}")
    return bad


def dispatch(sid, inputs, ctx=None, retries=None):
    _ensure_tools()
    ctx = dict(ctx or {})
    ctx.setdefault("evidence_log", str(EV))
    c = get(sid)
    if c is None:
        return {
            "result_state": ResultState.NOT_RUN.value,
            "reason": f"skill not in registry: {sid}",
        }
    if not c.impl:
        return {"result_state": ResultState.NOT_RUN.value, "reason": f"not bound: {sid}"}
    if c.impl not in tools.REG:
        return {"result_state": ResultState.TOOL_FAILURE.value, "reason": f"tool missing: {c.impl}"}
    e = _check(inputs, c.input_types)
    if e:
        audit.append(
            "dispatch", {"skill": sid, "state": ResultState.INSUFFICIENT_DATA.value, "errors": e}
        )
        return {"result_state": ResultState.INSUFFICIENT_DATA.value, "errors": e}
    if c.permissions:
        pol = tools.call(
            "policy-check",
            {"permissions": ctx.get("permissions", []), "required": c.permissions},
            ctx,
        )
        if pol.get("result_state") != ResultState.PASS.value:
            audit.append("dispatch", {"skill": sid, "state": ResultState.POLICY_DENIED.value})
            return {"result_state": ResultState.POLICY_DENIED.value, "policy": pol}
    attempts = 0
    mx = 1 + (retries if retries is not None else int(c.retries.get("max", 0)))
    last = None
    while attempts < mx:
        attempts += 1
        last = runtime.run_tool(tools.REG[c.impl]["fn"], inputs, ctx)
        st = normalize_result(last)
        if st == ResultState.PASS or st.value not in set(c.retries.get("on", [])):
            break
    out = dict(last or {})
    out["result_state"] = normalize_result(out).value
    out["skill"] = c.identifier
    out["attempts"] = attempts
    audit.append("dispatch", {"skill": sid, "state": out["result_state"], "attempts": attempts})
    return out
