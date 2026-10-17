"""
Discovery + Planning bindings with honest stdlib implementations.

Discovery:
- discover-params : translate an intent dict into {root, pattern, query} for the
                    search family, so Discover can actually run.

Planning:
- decompose-work    : split an intent into ordered sub-tasks
- build-task-graph  : produce a node/edge graph from sub-tasks (linear chain)
- sequence-work     : order sub-tasks by dependency
- prioritize-work   : sort sub-tasks by explicit priority field or heuristic
- parallelize-work  : partition sub-tasks into parallelisable groups
- estimate-complexity: crude token/task-based complexity score (honest heuristic)

These do NOT run a language model. They operate on structured dicts.
"""

from pathlib import Path
from .contracts import ResultState

# ---------- discovery ----------


def t_discover_params(i, ctx):
    """Translate an intent into search-family parameters.

    Rules (honest heuristic):
    - if intent has explicit root/pattern/query, use them
    - else if intent.request mentions a path-like token, use it as root
    - default root to '.', pattern to '*.py', query to intent.request
    """
    intent = i.get("intent") or {}
    out = {}
    if isinstance(intent, dict):
        for k in ("root", "pattern", "query"):
            if k in intent:
                out[k] = intent[k]
    # try to extract path-like token from request text
    if "root" not in out and isinstance(intent, dict):
        req = str(intent.get("request", ""))
        for token in req.split():
            if token.startswith("./") or token.startswith("/") or "/" in token:
                out["root"] = token.strip(".,;:'\"")
                break
    out.setdefault("root", ".")
    out.setdefault("pattern", "*.py")
    rp = Path(out["root"])
    if rp.suffix and rp.suffix != "*":  # looks like a file
        out.setdefault("path", str(rp))
        out["root"] = str(rp.parent) if str(rp.parent) else "."
    else:
        out.setdefault("path", out["root"].rstrip("/") + "/" + out["pattern"])
    if "query" not in out and isinstance(intent, dict) and intent.get("request"):
        out["query"] = str(intent["request"])
    return {"result_state": ResultState.PASS.value, "params": out, **out}


# ---------- planning ----------


def _intent_to_tasks(intent):
    """Derive a simple ordered task list from an intent."""
    req = ""
    if isinstance(intent, dict):
        req = str(intent.get("request") or intent.get("objective") or "")
    if not req:
        return []
    # one task per sentence-ish; fall back to whole request
    parts = [p.strip() for p in req.replace(";", ".").split(".") if p.strip()]
    if not parts:
        parts = [req]
    return [
        {"id": f"t{n+1}", "description": p, "status": "pending"}
        for n, p in enumerate(parts)
    ]


def t_decompose_work(i, ctx):
    intent = i.get("intent") or {}
    tasks = _intent_to_tasks(intent)
    if not tasks:
        return {
            "result_state": ResultState.INSUFFICIENT_DATA.value,
            "reason": "no request/objective to decompose",
        }
    return {"result_state": ResultState.PASS.value, "tasks": tasks, "count": len(tasks)}


def t_build_task_graph(i, ctx):
    tasks = i.get("tasks") or []
    if not isinstance(tasks, list) or not tasks:
        return {
            "result_state": ResultState.INSUFFICIENT_DATA.value,
            "reason": "tasks list required",
        }
    nodes = [
        {"id": t["id"], "description": t.get("description", "")}
        for t in tasks
        if "id" in t
    ]
    edges = []
    # linear chain by default: t1 -> t2 -> ... -> tN
    for a, b in zip(nodes, nodes[1:]):
        edges.append({"from": a["id"], "to": b["id"]})
    return {
        "result_state": ResultState.PASS.value,
        "graph": {"nodes": nodes, "edges": edges},
    }


def t_sequence_work(i, ctx):
    tasks = i.get("tasks") or []
    if not isinstance(tasks, list) or not tasks:
        return {
            "result_state": ResultState.INSUFFICIENT_DATA.value,
            "reason": "tasks list required",
        }
    # order by explicit 'after' if present, else by input order
    ordered = sorted(tasks, key=lambda t: t.get("after", 0))
    return {
        "result_state": ResultState.PASS.value,
        "ordered": [t.get("id") for t in ordered if "id" in t],
    }


def t_prioritize_work(i, ctx):
    tasks = i.get("tasks") or []
    if not isinstance(tasks, list) or not tasks:
        return {
            "result_state": ResultState.INSUFFICIENT_DATA.value,
            "reason": "tasks list required",
        }

    def rank(t):
        # explicit priority wins; else higher for verbs that gate others
        if "priority" in t:
            return -int(t["priority"])
        d = str(t.get("description", "")).lower()
        for i, kw in enumerate(
            ["plan", "design", "test", "verify", "implement", "build", "fix"]
        ):
            if kw in d:
                return i
        return 100

    ordered = sorted(tasks, key=rank)
    return {
        "result_state": ResultState.PASS.value,
        "ordered": [t.get("id") for t in ordered if "id" in t],
    }


def t_parallelize_work(i, ctx):
    tasks = i.get("tasks") or []
    if not isinstance(tasks, list) or not tasks:
        return {
            "result_state": ResultState.INSUFFICIENT_DATA.value,
            "reason": "tasks list required",
        }
    # partition by explicit 'phase' if present, else one bucket per task (serial)
    phases = {}
    for t in tasks:
        ph = t.get("phase", f"serial-{t.get('id','?')}")
        phases.setdefault(ph, []).append(t.get("id"))
    return {
        "result_state": ResultState.PASS.value,
        "groups": [{"phase": ph, "tasks": ids} for ph, ids in phases.items()],
    }


def t_estimate_complexity(i, ctx):
    tasks = i.get("tasks") or []
    if not isinstance(tasks, list) or not tasks:
        return {
            "result_state": ResultState.INSUFFICIENT_DATA.value,
            "reason": "tasks list required",
        }
    # crude: total description length / 80 chars as a proxy for "units of work"
    total_chars = sum(len(str(t.get("description", ""))) for t in tasks)
    score = round(total_chars / 80.0, 2)
    return {
        "result_state": ResultState.PASS.value,
        "tasks": len(tasks),
        "total_chars": total_chars,
        "complexity_units": score,
    }


# ---------- bindings ----------

BINDINGS = {
    # NOTE: discover-params is intentionally NOT in BINDINGS — there is no
    # matching §02 skill in the atlas. It is a flow-level transform between
    # Formalize and Discover, registered as a raw tool below.
    "decompose-work": ("decompose-work", {"intent": "json"}),
    "build-task-graph": ("build-task-graph", {"tasks": "json"}),
    "sequence-work": ("sequence-work", {"tasks": "json"}),
    "prioritize-work": ("prioritize-work", {"tasks": "json"}),
    "parallelize-work": ("parallelize-work", {"tasks": "json"}),
    "estimate-complexity": ("estimate-complexity", {"tasks": "json"}),
}

IMPLS = {
    "discover-params": t_discover_params,
    "decompose-work": t_decompose_work,
    "build-task-graph": t_build_task_graph,
    "sequence-work": t_sequence_work,
    "prioritize-work": t_prioritize_work,
    "parallelize-work": t_parallelize_work,
    "estimate-complexity": t_estimate_complexity,
}

_REGISTERED = False


def register_all(tools_mod=None):
    global _REGISTERED
    if tools_mod is None:
        from . import tools as tools_mod  # noqa: F401
    n = 0
    for name, fn in IMPLS.items():
        if name in tools_mod.REG:
            continue
        schema = {}
        for slug, (t, s) in BINDINGS.items():
            if t == name:
                schema = s
                break
        tools_mod.register(name, schema)(fn)
        n += 1
    _REGISTERED = True
    return n


def apply():
    from . import seed_skills

    added = 0
    for slug, (tool, schema) in BINDINGS.items():
        if seed_skills.IMPL.get(slug) != tool:
            seed_skills.IMPL[slug] = tool
            added += 1
    return added
