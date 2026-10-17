"""
Bind Intent/Intake skills with honest stdlib implementations.

Each of these is real:
- capture-intent      : read a task description from a file or stdin
- parse-intent        : parse JSON/YAML/text into a structured request
- classify-intent     : classify by keyword bucket (real, not LLM)
- normalize-intent    : whitespace/case normalisation
- disambiguate-intent : report ambiguities (missing fields, terse input)
- reconcile-intent    : merge multiple intent dicts, later wins
- mirror-intent       : echo back the canonical form
- formalize-intent    : emit a §05-shaped intent contract
- version-intent      : content-hash for versioning
- compare-intent      : structural diff of two intents

These do NOT pretend to be an LLM. They operate on structured inputs.
"""

import hashlib, json, re, sys
from pathlib import Path
from .contracts import ResultState
from . import tools

# ---------- implementations ----------


def t_capture_intent(i, ctx):
    src = i.get("source")
    if src == "stdin":
        return {"result_state": ResultState.PASS.value, "text": sys.stdin.read()}
    if src:
        p = Path(src).expanduser()
        if not p.exists():
            return {
                "result_state": ResultState.ENVIRONMENT_FAILURE.value,
                "reason": f"no such file: {src}",
            }
        return {"result_state": ResultState.PASS.value, "text": p.read_text(errors="ignore")}
    # no source: pass through whatever text was in inputs
    return {"result_state": ResultState.PASS.value, "text": i.get("text", "")}


def t_parse_intent(i, ctx):
    raw = i.get("text", "")
    if not raw.strip():
        return {"result_state": ResultState.INSUFFICIENT_DATA.value, "reason": "empty text"}
    # try JSON first
    try:
        obj = json.loads(raw)
        return {"result_state": ResultState.PASS.value, "intent": obj, "format": "json"}
    except Exception:
        pass
    # fall back to key: value lines
    kv = {}
    for line in raw.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip().lower().replace(" ", "_")
            v = v.strip()
            if k and v:
                kv.setdefault(k, []).append(v) if k in kv else kv.__setitem__(k, v)
    if kv:
        return {"result_state": ResultState.PASS.value, "intent": kv, "format": "kv"}
    # last resort: whole text as single 'request' field
    return {
        "result_state": ResultState.PASS.value,
        "intent": {"request": raw.strip()},
        "format": "text",
    }


def t_normalize_intent(i, ctx):
    intent = i.get("intent")
    if not isinstance(intent, dict):
        return {
            "result_state": ResultState.INSUFFICIENT_DATA.value,
            "reason": "intent must be a dict",
        }
    out = {}
    for k, v in intent.items():
        nk = re.sub(r"\s+", "_", str(k).strip().lower())
        if isinstance(v, str):
            out[nk] = re.sub(r"\s+", " ", v).strip()
        else:
            out[nk] = v
    return {"result_state": ResultState.PASS.value, "intent": out}


def t_classify_intent(i, ctx):
    intent = i.get("intent") or {}
    text = " ".join(str(v) for v in intent.values()).lower()
    buckets = {
        "search": ["search", "find", "look up", "discover", "explore"],
        "build": ["build", "implement", "create", "generate", "write"],
        "fix": ["fix", "repair", "debug", "resolve", "patch"],
        "test": ["test", "verify", "validate", "check"],
        "review": ["review", "audit", "assess", "inspect"],
        "deploy": ["deploy", "release", "ship", "rollout"],
        "plan": ["plan", "schedule", "estimate", "design"],
    }
    hits = {k: sum(1 for kw in v if kw in text) for k, v in buckets.items()}
    hits = {k: n for k, n in hits.items() if n}
    primary = max(hits, key=hits.get) if hits else "unknown"
    return {"result_state": ResultState.PASS.value, "classification": primary, "scores": hits}


def t_disambiguate_intent(i, ctx):
    intent = i.get("intent") or {}
    issues = []
    if not intent:
        issues.append("intent is empty")
    for k in ("request", "objective", "task"):
        if k not in intent:
            issues.append(f"missing {k}")
    for k, v in intent.items():
        if isinstance(v, str) and len(v.strip()) < 3:
            issues.append(f"field {k} is too terse")
    return {
        "result_state": (ResultState.PASS if not issues else ResultState.PARTIAL).value,
        "issues": issues,
        "clean": not issues,
    }


def t_reconcile_intent(i, ctx):
    intents = i.get("intents")
    if not intents and isinstance(i.get("intent"), dict):
        intents = [i["intent"]]
    if not isinstance(intents, list) or not intents:
        return {
            "result_state": ResultState.INSUFFICIENT_DATA.value,
            "reason": "intents list (or single intent) required",
        }
    merged = {}
    for it in intents:
        if isinstance(it, dict):
            for k, v in it.items():
                merged[k] = v  # later wins
    return {"result_state": ResultState.PASS.value, "intent": merged}


def t_mirror_intent(i, ctx):
    return {
        "result_state": ResultState.PASS.value,
        "mirror": json.dumps(i.get("intent") or {}, sort_keys=True),
    }


def t_formalize_intent(i, ctx):
    intent = i.get("intent") or {}
    if not intent:
        return {"result_state": ResultState.INSUFFICIENT_DATA.value, "reason": "intent required"}
    # §05-shaped contract
    contract = {
        "identifier": "intent-"
        + hashlib.sha256(json.dumps(intent, sort_keys=True).encode()).hexdigest()[:12],
        "version": "0.1.0",
        "description": intent.get("request") or intent.get("objective") or "",
        "capability": "intent",
        "domain": intent.get("domain", ""),
        "operation": "formalize",
        "input_types": {k: type(v).__name__ for k, v in intent.items()},
        "result_states": ["PASS", "FAIL", "PARTIAL", "INSUFFICIENT_DATA"],
        "preconditions": [],
        "postconditions": ["contract_emitted"],
        "evidence_produced": ["intent_contract"],
    }
    return {"result_state": ResultState.PASS.value, "contract": contract}


def t_version_intent(i, ctx):
    intent = i.get("intent") or {}
    h = hashlib.sha256(json.dumps(intent, sort_keys=True).encode()).hexdigest()
    return {"result_state": ResultState.PASS.value, "version": h[:16], "hash": h}


def t_compare_intent(i, ctx):
    a = i.get("a") or {}
    b = i.get("b") or {}
    if not isinstance(a, dict) or not isinstance(b, dict):
        return {
            "result_state": ResultState.INSUFFICIENT_DATA.value,
            "reason": "a and b must be dicts",
        }
    keys = set(a) | set(b)
    diff = {}
    for k in keys:
        if a.get(k) != b.get(k):
            diff[k] = {"a": a.get(k), "b": b.get(k)}
    return {"result_state": ResultState.PASS.value, "equal": not diff, "diff": diff}


# ---------- bindings + registration ----------

BINDINGS = {
    # source and text are alternatives; only 'source' declared required.
    "capture-intent": ("capture-intent", {"source": "string"}),
    "parse-intent": ("parse-intent", {"text": "string"}),
    "normalize-intent": ("normalize-intent", {"intent": "json"}),
    "classify-intent": ("classify-intent", {"intent": "json"}),
    "disambiguate-intent": ("disambiguate-intent", {"intent": "json"}),
    # accepts intents list OR single intent; nothing strictly required
    "reconcile-intent": ("reconcile-intent", {}),
    "mirror-intent": ("mirror-intent", {"intent": "json"}),
    "formalize-intent": ("formalize-intent", {"intent": "json"}),
    "version-intent": ("version-intent", {"intent": "json"}),
    "compare-intent": ("compare-intent", {"a": "json", "b": "json"}),
}

IMPLS = {
    "capture-intent": t_capture_intent,
    "parse-intent": t_parse_intent,
    "normalize-intent": t_normalize_intent,
    "classify-intent": t_classify_intent,
    "disambiguate-intent": t_disambiguate_intent,
    "reconcile-intent": t_reconcile_intent,
    "mirror-intent": t_mirror_intent,
    "formalize-intent": t_formalize_intent,
    "version-intent": t_version_intent,
    "compare-intent": t_compare_intent,
}

_REGISTERED = False


def register_all(tools_mod=None):
    global _REGISTERED
    if tools_mod is None:
        from . import tools as tools_mod  # noqa: F401
    if _REGISTERED and len(tools_mod.REG) > 0:
        # still try to ensure our tools are present
        pass
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
