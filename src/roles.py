"""
§01 AGENT FUNCTIONS as executable roles.

Note: §01 subsections ("Discovery / Research") and §02 subsections
("Search / Retrieval") are DIFFERENT taxonomies. Role->skill composition is
therefore either curated (role_map.json, preferred) or mapped heuristically
via SUBSECTION_ALIASES + name overlap. The atlas supplies names, not the
composition graph; this file supplies the graph.
"""

import json
import sqlite3
import time
from pathlib import Path
from .contracts import ResultState
from . import dispatch, tools

ATLAS = Path("data/atlas/atlas.sqlite")
SKILLS = Path("data/skills.sqlite")
ROLE_MAP = Path("data/role_map.json")
EVIDENCE = Path("evidence.log")

# §01 subsection -> candidate §02 subsections (heuristic, overrideable)
SUBSECTION_ALIASES = {
    "Discovery / Research": ["Search / Retrieval", "Repository Intelligence"],
    "Intent / Intake": ["Intent", "Context", "Requirements"],
    "Analysis / Reasoning": ["Statistics", "Optimization", "Quality"],
    "Planning": ["Planning", "Scheduling"],
    "Architecture / Design": ["Architecture", "Modeling", "API Engineering", "UI / UX"],
    "Specification / Formalization": ["Formal Methods"],
    "Implementation": [
        "Coding",
        "Language Engineering",
        "Programming Paradigms",
        "Algorithms",
        "Data Structures",
    ],
    "Transformation": ["Serialization", "Interoperability", "Migration", "Integration"],
    "Review": ["Quality", "Standards / Compliance"],
    "Verification / Validation": ["Testing", "Reliability", "Formal Methods"],
    "Debugging / Repair": ["Debugging", "Performance", "Observability"],
    "Security": [
        "Application Security",
        "Security Testing",
        "Threat / Defense",
        "Cryptography",
        "Identity",
        "Sandbox / Isolation",
    ],
    "Operations": ["Orchestration", "Runtime Control", "Operations Management"],
    "Observability": ["Observability", "Performance"],
    "Governance / Authority": [
        "Governance",
        "Policy",
        "Evidence",
        "Qualification",
        "Provenance",
    ],
    "Coordination": [
        "Multi-Agent Coordination",
        "Scheduling",
        "Messaging / Events",
        "Agent Management",
    ],
    "Evidence / Qualification": ["Evidence", "Qualification", "Audit", "Provenance"],
    "Documentation / Knowledge": ["Documentation", "Knowledge"],
    "Stewardship": ["Artifact Management", "Lifecycle"],
}

ORDER_HINTS = [
    # producers first
    "capture",
    "read",
    "acquire",
    "collect",
    "fetch",
    "search",
    "inventory",
    "inspect",
    "scan",
    "detect",
    "parse",
    "extract",
    # transformers
    "normalize",
    "classify",
    "disambiguate",
    "reconcile",
    "merge",
    "map",
    "analyze",
    "assess",
    "evaluate",
    # validators / checkers
    "verify",
    "validate",
    "check",
    # reporters / emitters
    "mirror",
    "report",
    "formalize",
    "emit",
    "record",
    "attest",
    "version",
    "compare",
    # enforcers last
    "enforce",
    "gate",
]


def _rank(slug):
    for i, h in enumerate(ORDER_HINTS):
        if h in slug:
            return i
    return len(ORDER_HINTS)


def list_roles(subsection=None):
    con = sqlite3.connect(ATLAS)
    con.row_factory = sqlite3.Row
    if subsection:
        rows = con.execute(
            "SELECT name,slug,subsection FROM items "
            "WHERE kind='role' AND subsection=? ORDER BY name",
            (subsection,),
        ).fetchall()
        con.close()
        return [dict(r) for r in rows]
    rows = con.execute(
        "SELECT DISTINCT subsection FROM items WHERE kind='role' ORDER BY subsection"
    ).fetchall()
    con.close()
    return [r["subsection"] for r in rows]


def _curated(role):
    if not ROLE_MAP.exists():
        return None
    m = json.loads(ROLE_MAP.read_text(encoding="utf-8"))
    return m.get(role)  # list of skill slugs, or None


def role_skills(role):
    con = sqlite3.connect(ATLAS)
    con.row_factory = sqlite3.Row
    r = con.execute(
        "SELECT subsection FROM items WHERE kind='role' AND name=? LIMIT 1", (role,)
    ).fetchone()
    if not r:
        con.close()
        return []
    role_sub = r["subsection"]

    # candidate skill slugs: curated first, then alias-mapped §02 subsections
    curated = _curated(role)
    if curated:
        cands = [(s, None) for s in curated]
    else:
        skill_subs = SUBSECTION_ALIASES.get(role_sub, [])
        ph = ",".join("?" * len(skill_subs)) if skill_subs else "''"
        rows = con.execute(
            f"SELECT slug,subsection FROM items WHERE kind='skill' "
            f"AND subsection IN ({ph})",
            skill_subs,
        ).fetchall()
        cands = [(x["slug"], x["subsection"]) for x in rows]
    con.close()

    # join to the registry: each candidate slug can have several __subsection rows
    sk = sqlite3.connect(SKILLS)
    out = []
    seen = set()
    for slug, sub in cands:
        for cid, contract in sk.execute(
            "SELECT id,contract FROM skills WHERE id=? OR id LIKE ?",
            (slug, slug + "__%"),
        ):
            if cid in seen:
                continue
            seen.add(cid)
            c = json.loads(contract)
            out.append(
                {
                    "id": cid,
                    "slug": c["identifier"].split("__")[0],
                    "impl": c["impl"],
                    "bound": bool(c["impl"]),
                    "subsection": c["capability"],
                }
            )
    sk.close()
    curated = _curated(role)
    if curated:
        order = {slug: i for i, slug in enumerate(curated)}
        out.sort(key=lambda x: order.get(x["slug"], len(order)))
    else:
        out.sort(key=lambda x: (not x["bound"], _rank(x["slug"]), x["id"]))
    return out


def _skill_inputs(inputs, slug):
    """Per-skill inputs: {slug: {...}, "_default": {...}} or a flat dict."""
    if isinstance(inputs, dict) and "_default" in inputs:
        return inputs.get(slug, inputs.get("_default", {})) or {}
    return inputs or {}


def _load_role_inputs(role):
    """Load data/role_inputs/<role-with-dashes>.json if present."""
    fname = role.replace(" / ", "_").replace(" ", "_") + ".json"
    p = Path("data/role_inputs") / fname
    if p.exists():
        import json as _j

        return _j.loads(p.read_text())
    return None


def run_role(role, inputs=None, ctx=None, stop_on_fail=False):
    if not inputs:
        inputs = _load_role_inputs(role) or {}
    else:
        inputs = inputs or {}
    ctx = dict(ctx or {})
    ctx.setdefault("evidence_log", str(EVIDENCE))
    skills = role_skills(role)
    if not skills:
        return {
            "role": role,
            "result_state": ResultState.NOT_RUN.value,
            "reason": f"role found but no mapped skills; add to data/role_map.json or SUBSECTION_ALIASES: {role}",
        }
    trace = []
    seed = {}
    for s in skills:
        if not s["bound"]:
            trace.append(
                {
                    "skill": s["id"],
                    "result_state": ResultState.NOT_RUN.value,
                    "reason": "unbound",
                }
            )
            continue
        overrides = _skill_inputs(inputs, s["slug"])
        step_inputs = dict(overrides) if isinstance(overrides, dict) else {}
        step_inputs.update(seed)
        o = dispatch.dispatch(s["id"], step_inputs, ctx)
        trace.append(
            {
                "skill": s["id"],
                "result_state": o.get("result_state"),
                "detail": {
                    k: v
                    for k, v in o.items()
                    if k not in ("result_state", "skill", "attempts")
                },
            }
        )
        if o.get("result_state") == ResultState.PASS.value:
            for k, v in o.items():
                if k in ("result_state", "skill", "attempts"):
                    continue
                seed[k] = v
        if stop_on_fail and o.get("result_state") != ResultState.PASS.value:
            break
    bound_states = [t["result_state"] for t in trace if t.get("reason") != "unbound"]
    if not bound_states:
        agg = ResultState.NOT_RUN.value
    elif ResultState.FAIL.value in bound_states:
        agg = ResultState.FAIL.value
    elif any(
        s
        in (
            ResultState.INSUFFICIENT_DATA.value,
            ResultState.INSUFFICIENT_EVIDENCE.value,
        )
        for s in bound_states
    ):
        agg = ResultState.INSUFFICIENT_EVIDENCE.value
    elif all(s == ResultState.PASS.value for s in bound_states):
        agg = ResultState.PASS.value
    else:
        agg = ResultState.PARTIAL.value
    if len(trace) > 25 and all(t.get("reason") == "unbound" for t in trace):
        trace = [
            {
                "summary": f"{len(trace)} skills defined but none bound",
                "result_state": ResultState.NOT_RUN.value,
            }
        ]
    bundle = {
        "role": role,
        "result_state": agg,
        "skills_total": len(skills),
        "skills_bound": sum(1 for s in skills if s["bound"]),
        "skills_run": len(bound_states),
        "trace": trace,
        "ts": time.time(),
    }
    tools.call("evidence-capture", {"payload": {"role": role, "aggregate": agg}}, ctx)
    return bundle
