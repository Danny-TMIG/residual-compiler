import hashlib, json, subprocess, time
from pathlib import Path
from .contracts import ResultState

REG = {}


def register(name, schema=None):
    def deco(fn):
        REG[name] = {"fn": fn, "schema": schema or {}}
        return fn

    return deco


def call(name, inputs, ctx):
    if name not in REG:
        return {"result_state": ResultState.TOOL_FAILURE.value, "reason": f"unbound tool: {name}"}
    try:
        o = REG[name]["fn"](inputs or {}, ctx or {})
        if not isinstance(o, dict):
            o = {"result": o}
        o.setdefault("result_state", ResultState.PASS.value)
        return o
    except TimeoutError:
        return {"result_state": ResultState.TIMEOUT.value}
    except PermissionError:
        return {"result_state": ResultState.POLICY_DENIED.value}
    except FileNotFoundError as e:
        return {"result_state": ResultState.ENVIRONMENT_FAILURE.value, "reason": str(e)}
    except Exception as e:
        return {"result_state": ResultState.EXECUTION_FAILURE.value, "reason": str(e)}


@register("filesystem-search", {"pattern": "string", "root": "path"})
def filesystem_search(i, ctx):
    root = Path(i.get("root", ".")).expanduser()
    pat = i.get("pattern", "*")
    hits = [str(p) for p in root.rglob(pat)][:500]
    return {"result_state": ResultState.PASS.value, "matches": hits, "count": len(hits)}


@register("regex-search", {"pattern": "string", "path": "path"})
def regex_search(i, ctx):
    import re

    pat = re.compile(i["pattern"])
    p = Path(i.get("path", ".")).expanduser()
    hits = []
    files = [p] if p.is_file() else list(p.rglob("*"))
    for f in files:
        if not f.is_file():
            continue
        try:
            for n, l in enumerate(f.read_text(errors="ignore").splitlines(), 1):
                if pat.search(l):
                    hits.append({"file": str(f), "line": n, "text": l})
        except Exception:
            pass
        if len(hits) >= 500:
            break
    return {"result_state": ResultState.PASS.value, "matches": hits, "count": len(hits)}


@register("execute-command", {"argv": "list[string]", "timeout_s": "int"})
def execute_command(i, ctx):
    argv = i["argv"]
    if not isinstance(argv, list) or not argv:
        return {"result_state": ResultState.INSUFFICIENT_DATA.value, "reason": "argv required"}
    t = int(i.get("timeout_s", 10))
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=t)
    except subprocess.TimeoutExpired:
        return {"result_state": ResultState.TIMEOUT.value}
    return {
        "result_state": (
            ResultState.PASS if r.returncode == 0 else ResultState.EXECUTION_FAILURE
        ).value,
        "returncode": r.returncode,
        "stdout": r.stdout[:8000],
        "stderr": r.stderr[:8000],
    }


@register("evidence-hash", {"path": "path", "algo": "string"})
def evidence_hash(i, ctx):
    p = Path(i["path"]).expanduser()
    h = hashlib.new(i.get("algo", "sha256"))
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return {"result_state": ResultState.PASS.value, "digest": h.hexdigest()}


@register("evidence-capture", {"payload": "json"})
def evidence_capture(i, ctx):
    log = Path(ctx.get("evidence_log", "evidence.log"))
    with log.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps({"ts": time.time(), "payload": i.get("payload")}, ensure_ascii=False) + "\n"
        )
    return {"result_state": ResultState.PASS.value, "recorded": str(log)}


@register("policy-check", {"permissions": "list[string]", "required": "list[string]"})
def policy_check(i, ctx):
    missing = sorted(set(i.get("required", [])) - set(i.get("permissions", [])))
    return {
        "result_state": (ResultState.POLICY_DENIED if missing else ResultState.PASS).value,
        "missing": missing,
    }


@register(
    "authority-check",
    {"actor": "string", "authorities": "list[string]", "required": "list[string]"},
)
def authority_check(i, ctx):
    missing = sorted(set(i.get("required", [])) - set(i.get("authorities", [])))
    return {
        "result_state": (ResultState.NOT_AUTHORIZED if missing else ResultState.PASS).value,
        "missing": missing,
    }
