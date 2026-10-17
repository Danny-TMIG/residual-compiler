"""
Compile a plain-English task description into the executable inputs the flow
needs (`_default`), then check those inputs against policy.

Returns:
{
  "description": <original>,
  "intent": <parsed dict>,
  "policy": {"decision": ..., "reasons": ..., "matched": ...},
  "default": {...},            # what would be passed to run_flow
  "allowed": bool,
  "blocked_reason": str | None
}

Rules:
- Text with "deploy to prod"      -> operation=deploy, target_env=prod
- Text with "audit/build/test"    -> operation=execute (needs approval by policy)
- Text with "search/find"         -> operation=search
- Path-like token (foo/bar.py)    -> root=parent, path=token
- argv=["true"] always included   -> safe no-op build step
- All produces default inputs the flow can consume
"""

import re
from pathlib import Path
from . import policy as policy_mod
from . import residuals as residual_mod
from . import compiler_limits as cl
from .contracts import ResultState

OPS = {
    # ordered: first match wins. deploy > execute > learn > search.
    "deploy": re.compile(r"\b(deploy|release|ship|rollout)\b", re.I),
    "execute": re.compile(r"\b(audit|build|run|test|execute|repair|patch)\b", re.I),
    "learn": re.compile(r"\b(learn|retain|remember)\b", re.I),
    "search": re.compile(r"\b(search|find|look\s+up|discover)\b", re.I),
}
ENV = re.compile(r"\b(prod|production|staging|dev|development|test)\b", re.I)
PATH_TOKEN = re.compile(r"(\./[\w./\-]+|/[\w./\-]+|[\w][\w.\-]*/[\w./\-]+)")


def _classify(desc):
    op = "search"
    for name, rx in OPS.items():
        if rx.search(desc):
            op = name
            break
    env = "dev"
    m = ENV.search(desc)
    if m:
        env = "prod" if m.group(1).lower() in ("prod", "production") else m.group(1).lower()
    paths = PATH_TOKEN.findall(desc)
    return {"operation": op, "target_env": env, "paths": paths}


def _build_default(desc, cls):
    """Construct the _default dict the flow can consume."""
    default = {
        "source": "/tmp/task.json",
        "objective": desc,
        "argv": ["true"],
        "cwd": ".",
        "timeout_s": 10,
        "pattern": "FAIL|ERROR",
        "payload": {"note": desc[:200]},
        "permissions": [],
        "required": [],
        "action": "status",
    }
    if cls["paths"]:
        p = cls["paths"][0].rstrip("/")
        default["path"] = p
        default["root"] = str(Path(p).parent) if Path(p).suffix else p
        default["a"] = p
        default["b"] = p
        default["find"] = "def register"
        default["replace"] = "def register"
    else:
        default.update(
            {
                "path": "src/tools.py",
                "root": "src",
                "a": "src/tools.py",
                "b": "src/tools.py",
                "find": "def register",
                "replace": "def register",
            }
        )
    return default


def compile_task(description, authorities=None, policy_path=None, write_intent=False):
    """Compile a description into executable inputs; consult residuals and
    enforce residual->skill limits before returning."""
    cls = _classify(description)
    op_ctx = {
        "operation": cls["operation"],
        "target_env": cls["target_env"],
        "description": description,
        "paths": cls["paths"],
    }
    pol = policy_mod.evaluate(op_ctx, authorities=authorities, policy=policy_mod.load(policy_path))

    default = _build_default(description, cls)
    if cls["paths"]:
        p0 = cls["paths"][0]
        if Path(p0).suffix:
            default["path"] = p0
            default["root"] = str(Path(p0).parent) or "."
        else:
            default["root"] = p0
            default["path"] = f"{p0.rstrip('/')}/**"

    matched = residual_mod.for_task(description)
    # candidates = every bound skill in the registry + every role_map member.
    # The compiler limit applies to what the pipeline *could* call, not just
    # what the current role happens to compose.
    try:
        import sqlite3 as _sq

        _c = _sq.connect("data/skills.sqlite")
        bound = [r[0] for r in _c.execute("SELECT id FROM skills")]
        _c.close()
    except Exception:
        bound = []
    try:
        import json as _j

        _rm = _j.loads(Path("data/role_map.json").read_text())
        role_skills = [s for v in _rm.values() for s in v]
    except Exception:
        role_skills = []

    # normalize to bare slugs: strip "slug__subsection"
    candidates = sorted({s.split("__", 1)[0] for s in bound + role_skills})
    limit = cl.apply(matched, candidates, mode="strict")
    limit = cl.apply(matched, candidates, mode="strict")

    default["residual_constraints"] = [
        {
            "id": m["id"],
            "class": m["class"],
            "residual": m["residual"],
            "source": m["source"],
            "arity": m["arity"],
        }
        for m in matched
    ]
    default["forbidden_skills"] = limit["forbidden"]
    default["blocked_by_residual"] = limit["blocked"]

    if limit["blocked"]:
        pol = dict(pol)
        pol["decision"] = "DENY"
        pol["reasons"] = list(pol.get("reasons", [])) + [limit["reason"]]
        pol["matched"] = list(pol.get("matched", [])) + ["residual_limit"]

    intent = {
        "request": description,
        "objective": description,
        "operation": cls["operation"],
        "target_env": cls["target_env"],
    }
    if write_intent:
        Path("/tmp/task.json").write_text(__import__("json").dumps(intent), encoding="utf-8")

    return {
        "description": description,
        "intent": intent,
        "policy": pol,
        "default": default,
        "allowed": pol["decision"] == "ALLOW",
        "blocked_reason": (None if pol["decision"] == "ALLOW" else "; ".join(pol["reasons"])),
        "residuals": {
            "register_sha256": residual_mod.hash(),
            "matched": matched,
            "count": len(matched),
            "limits": {
                "mode": limit["mode"],
                "forbidden": limit["forbidden"],
                "blocked": limit["blocked"],
                "reason": limit["reason"],
            },
        },
    }
