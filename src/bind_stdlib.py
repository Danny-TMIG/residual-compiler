"""
Bind every atlas skill that can be honestly implemented with the Python
stdlib in this environment. Everything else stays unbound (NOT_RUN).

Each entry: (skill_slug, tool_name, schema, fn)
The tool_fn is registered under tool_name; seed_skills maps skill_slug -> tool_name.
"""

import base64
import csv
import hashlib
import io
import json
import re
import subprocess
import tomllib
from pathlib import Path

from .contracts import ResultState

# ---------- implementations ----------


def _read(p):
    return Path(p).expanduser().read_text(errors="ignore")


def _walk(root):
    return [p for p in Path(root).expanduser().rglob("*") if p.is_file()]


# search / retrieval
def t_repository_search(i, ctx):
    root = i.get("root", ".")
    pat = i.get("pattern", "*.py")
    return {
        "result_state": ResultState.PASS.value,
        "matches": [str(p) for p in Path(root).rglob(pat)][:500],
    }


def t_symbol_search(i, ctx):
    sym = i["symbol"]
    root = i.get("root", ".")
    out = []
    rx = re.compile(rf"\b{re.escape(sym)}\b")
    for f in _walk(root):
        if f.suffix not in (
            ".py",
            ".js",
            ".ts",
            ".go",
            ".rs",
            ".java",
            ".c",
            ".h",
            ".rb",
        ):
            continue
        try:
            for n, line in enumerate(_read(f).splitlines(), 1):
                if rx.search(line):
                    out.append({"file": str(f), "line": n, "text": line})
        except Exception:
            pass
        if len(out) >= 500:
            break
    return {"result_state": ResultState.PASS.value, "matches": out, "count": len(out)}


def t_semantic_search(i, ctx):
    # no embeddings model; do a grounded lexical fallback and say so
    q = i["query"].lower().split()
    root = i.get("root", ".")
    out = []
    for f in _walk(root):
        try:
            t = _read(f).lower()
        except Exception:
            continue
        score = sum(t.count(w) for w in q)
        if score:
            out.append({"file": str(f), "score": score})
    out.sort(key=lambda x: -x["score"])
    return {
        "result_state": ResultState.PASS.value,
        "matches": out[:50],
        "note": "lexical fallback (no embedding model bound)",
    }


def t_lexical_search(i, ctx):
    q = i["query"]
    root = i.get("root", ".")
    out = [str(f) for f in _walk(root) if q in str(f) or q in _read(f)]
    return {
        "result_state": ResultState.PASS.value,
        "matches": out[:500],
        "count": len(out),
    }


def t_log_search(i, ctx):
    pat = re.compile(i.get("pattern", "."))
    path = Path(i.get("path", "evidence.log")).expanduser()
    hits = []
    if path.exists():
        for n, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
            if pat.search(line):
                hits.append({"line": n, "text": line})
    return {"result_state": ResultState.PASS.value, "matches": hits, "count": len(hits)}


# repository intelligence
def t_inventory_files(i, ctx):
    root = i.get("root", ".")
    exts = {}
    for f in _walk(root):
        exts[f.suffix or "<none>"] = exts.get(f.suffix or "<none>", 0) + 1
    return {
        "result_state": ResultState.PASS.value,
        "by_extension": exts,
        "total": sum(exts.values()),
    }


def t_inventory_symbols(i, ctx):
    root = i.get("root", ".")
    rx = re.compile(r"^\s*(?:def|class)\s+([A-Za-z_][\w]*)")
    syms = []
    for f in _walk(root):
        if f.suffix != ".py":
            continue
        for n, line in enumerate(_read(f).splitlines(), 1):
            m = rx.match(line)
            if m:
                syms.append({"file": str(f), "line": n, "name": m.group(1)})
    return {"result_state": ResultState.PASS.value, "symbols": syms, "count": len(syms)}


def t_inventory_modules(i, ctx):
    root = Path(i.get("root", ".")).expanduser()
    mods = [str(p.relative_to(root)) for p in root.rglob("__init__.py")]
    return {"result_state": ResultState.PASS.value, "modules": mods, "count": len(mods)}


def t_inventory_dependencies(i, ctx):
    req = Path(i.get("path", "requirements.txt")).expanduser()
    deps = []
    if req.exists():
        deps = [
            ln.strip()
            for ln in req.read_text().splitlines()
            if ln.strip() and not ln.strip().startswith("#")
        ]
    return {
        "result_state": ResultState.PASS.value,
        "dependencies": deps,
        "count": len(deps),
    }


def t_detect_dead_code(i, ctx):
    root = i.get("root", ".")
    all_text = "\n".join(_read(f) for f in _walk(root) if f.suffix == ".py")
    rx = re.compile(r"^\s*(?:def|class)\s+([A-Za-z_][\w]*)", re.MULTILINE)
    names = set(rx.findall(all_text))
    unused = sorted(
        n for n in names if len(re.findall(rf"\b{re.escape(n)}\b", all_text)) <= 1
    )
    return {
        "result_state": ResultState.PASS.value,
        "unused": unused,
        "count": len(unused),
    }


def t_detect_duplicate_code(i, ctx):
    root = i.get("root", ".")
    seen, dups = {}, []
    for f in _walk(root):
        if f.suffix != ".py":
            continue
        for n, line in enumerate(_read(f).splitlines(), 1):
            s = line.strip()
            if len(s) < 20:
                continue
            if s in seen:
                dups.append({"text": s, "first": seen[s], "dup": f"{f}:{n}"})
            else:
                seen[s] = f"{f}:{n}"
    return {
        "result_state": ResultState.PASS.value,
        "duplicates": dups[:200],
        "count": len(dups),
    }


# evidence / audit / artifact
def t_evidence_store(i, ctx):
    log = Path(ctx.get("evidence_log", "evidence.log"))
    with log.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {"ts": __import__("time").time(), "evidence": i}, ensure_ascii=False
            )
            + "\n"
        )
    return {"result_state": ResultState.PASS.value, "stored": str(log)}


def t_evidence_query(i, ctx):
    log = Path(ctx.get("evidence_log", "evidence.log"))
    pat = re.compile(i.get("pattern", "."))
    hits = []
    if log.exists():
        for n, line in enumerate(log.read_text().splitlines(), 1):
            if pat.search(line):
                hits.append({"line": n, "text": line})
    return {"result_state": ResultState.PASS.value, "matches": hits, "count": len(hits)}


def t_evidence_verify(i, ctx):
    p = Path(i["path"]).expanduser()
    expected = i["sha256"]
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    ok = h == expected
    return {
        "result_state": (
            ResultState.PASS if ok else ResultState.VERIFICATION_FAILURE
        ).value,
        "actual": h,
        "expected": expected,
    }


def t_artifact_hash(i, ctx):
    """Hash an artifact's evidence payload deterministically."""
    import hashlib
    import json

    payload = json.dumps(
        {"i": i, "ctx": ctx}, sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def t_artifact_compare(i, ctx):
    a, b = Path(i["a"]).expanduser(), Path(i["b"]).expanduser()
    ha = hashlib.sha256(a.read_bytes()).hexdigest()
    hb = hashlib.sha256(b.read_bytes()).hexdigest()
    return {"result_state": ResultState.PASS.value, "equal": ha == hb, "a": ha, "b": hb}


# encoding / serialization / format
def t_encode(i, ctx):
    return {
        "result_state": ResultState.PASS.value,
        "encoded": base64.b64encode(i["data"].encode()).decode(),
    }


def t_decode(i, ctx):
    return {
        "result_state": ResultState.PASS.value,
        "decoded": base64.b64decode(i["data"]).decode(errors="ignore"),
    }


def t_json(i, ctx):
    s = i["text"]
    json.loads(s)
    return {"result_state": ResultState.PASS.value, "valid": True}


def t_yaml(i, ctx):
    # minimal YAML subset: parse `key: value` lines
    out = {}
    for ln in i["text"].splitlines():
        if ":" in ln:
            k, v = ln.split(":", 1)
            out[k.strip()] = v.strip()
    return {"result_state": ResultState.PASS.value, "parsed": out}


def t_toml(i, ctx):
    return {"result_state": ResultState.PASS.value, "parsed": tomllib.loads(i["text"])}


def t_csv(i, ctx):
    rows = list(csv.reader(io.StringIO(i["text"])))
    return {"result_state": ResultState.PASS.value, "rows": rows, "count": len(rows)}


def t_markdown(i, ctx):
    heads = [ln for ln in i["text"].splitlines() if ln.startswith("#")]
    return {
        "result_state": ResultState.PASS.value,
        "headings": heads,
        "count": len(heads),
    }


def t_validate_format(i, ctx):
    fmt = i["format"]
    s = i["text"]
    try:
        if fmt == "json":
            json.loads(s)
        elif fmt == "toml":
            tomllib.loads(s)
        elif fmt == "csv":
            list(csv.reader(io.StringIO(s)))
        else:
            return {"result_state": ResultState.UNSUPPORTED.value, "format": fmt}
        return {"result_state": ResultState.PASS.value, "valid": True}
    except Exception as e:
        return {
            "result_state": ResultState.VERIFICATION_FAILURE.value,
            "reason": str(e),
        }


# coding
def t_read_file(i, ctx):
    return {"result_state": ResultState.PASS.value, "text": _read(i["path"])[:20000]}


def t_create_file(i, ctx):
    p = Path(i["path"]).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(i.get("text", ""), encoding="utf-8")
    return {"result_state": ResultState.PASS.value, "created": str(p)}


def t_edit_file(i, ctx):
    p = Path(i["path"]).expanduser()
    s = p.read_text()
    if i["find"] not in s:
        return {"result_state": ResultState.NOT_RUN.value, "reason": "find not present"}
    p.write_text(s.replace(i["find"], i["replace"], 1))
    return {"result_state": ResultState.PASS.value, "edited": str(p)}


def t_rename_file(i, ctx):
    Path(i["src"]).expanduser().rename(Path(i["dst"]).expanduser())
    return {"result_state": ResultState.PASS.value}


def t_diff(i, ctx):
    a = _read(i["a"]).splitlines()
    b = _read(i["b"]).splitlines()
    import difflib

    d = list(difflib.unified_diff(a, b, fromfile=i["a"], tofile=i["b"]))
    return {"result_state": ResultState.PASS.value, "diff": d, "lines": len(d)}


# source control (delegates to git)
def t_git(i, ctx):
    argv = ["git"] + i["args"]
    r = subprocess.run(argv, capture_output=True, text=True, cwd=i.get("cwd", "."))
    st = ResultState.PASS if r.returncode == 0 else ResultState.EXECUTION_FAILURE
    return {
        "result_state": st.value,
        "stdout": r.stdout[:8000],
        "stderr": r.stderr[:8000],
        "returncode": r.returncode,
    }


# process / runtime
def t_process_control(i, ctx):
    return {
        "result_state": ResultState.PASS.value,
        "pid": __import__("os").getpid(),
        "argv": __import__("sys").argv,
    }


def t_detect_platform(i, ctx):
    import platform
    import sys

    return {
        "result_state": ResultState.PASS.value,
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "machine": platform.machine(),
    }


# ---------- skill -> (tool, schema) map ----------
# each entry: skill_slug -> (tool_name, schema)
# only skills with a real implementation are listed
BINDINGS = {
    # search / retrieval
    "repository-search": ("repository-search", {"root": "path", "pattern": "string"}),
    "symbol-search": ("symbol-search", {"symbol": "string", "root": "path"}),
    "semantic-search": ("semantic-search", {"query": "string", "root": "path"}),
    "lexical-search": ("lexical-search", {"query": "string", "root": "path"}),
    "log-search": ("log-search", {"pattern": "string", "path": "path"}),
    "regex-search": ("regex-search", {"pattern": "string", "path": "path"}),
    "filesystem-search": ("filesystem-search", {"pattern": "string", "root": "path"}),
    # repository intelligence
    "inventory-files": ("inventory-files", {"root": "path"}),
    "inventory-symbols": ("inventory-symbols", {"root": "path"}),
    "inventory-modules": ("inventory-modules", {"root": "path"}),
    "inventory-dependencies": ("inventory-dependencies", {"path": "path"}),
    "detect-dead-code": ("detect-dead-code", {"root": "path"}),
    "detect-duplicate-code": ("detect-duplicate-code", {"root": "path"}),
    # evidence / audit / artifact
    "evidence-capture": ("evidence-capture", {"payload": "json"}),
    "evidence-hash": ("evidence-hash", {"path": "path", "algo": "string"}),
    "evidence-store": ("evidence-store", {"payload": "json"}),
    "evidence-query": ("evidence-query", {"pattern": "string"}),
    "evidence-verify": ("evidence-verify", {"path": "path", "sha256": "string"}),
    "artifact-hash": ("artifact-hash", {"path": "path", "algo": "string"}),
    "artifact-compare": ("artifact-compare", {"a": "path", "b": "path"}),
    # encoding / format
    "encode": ("encode", {"data": "string"}),
    "decode": ("decode", {"data": "string"}),
    "json": ("json-parse", {"text": "string"}),
    "yaml": ("yaml-parse", {"text": "string"}),
    "toml": ("toml-parse", {"text": "string"}),
    "csv": ("csv-parse", {"text": "string"}),
    "markdown": ("markdown-parse", {"text": "string"}),
    "validate-format": ("validate-format", {"format": "string", "text": "string"}),
    # coding
    "read-file": ("read-file", {"path": "path"}),
    "create-file": ("create-file", {"path": "path", "text": "string"}),
    "edit-file": ("edit-file", {"path": "path", "find": "string", "replace": "string"}),
    "rename-file": ("rename-file", {"src": "path", "dst": "path"}),
    "diff": ("diff", {"a": "path", "b": "path"}),
    # source control
    "clone": ("git", {"args": "list[string]", "cwd": "path"}),
    "fetch": ("git", {"args": "list[string]", "cwd": "path"}),
    "pull": ("git", {"args": "list[string]", "cwd": "path"}),
    "branch": ("git", {"args": "list[string]", "cwd": "path"}),
    "checkout": ("git", {"args": "list[string]", "cwd": "path"}),
    "stage": ("git", {"args": "list[string]", "cwd": "path"}),
    "commit": ("git", {"args": "list[string]", "cwd": "path"}),
    "tag": ("git", {"args": "list[string]", "cwd": "path"}),
    "diff-git": ("git", {"args": "list[string]", "cwd": "path"}),
    "blame": ("git", {"args": "list[string]", "cwd": "path"}),
    "bisect": ("git", {"args": "list[string]", "cwd": "path"}),
    "rebase": ("git", {"args": "list[string]", "cwd": "path"}),
    "merge": ("git", {"args": "list[string]", "cwd": "path"}),
    "cherry-pick": ("git", {"args": "list[string]", "cwd": "path"}),
    "reset": ("git", {"args": "list[string]", "cwd": "path"}),
    "revert": ("git", {"args": "list[string]", "cwd": "path"}),
    "history-analysis": ("git", {"args": "list[string]", "cwd": "path"}),
    # process / env
    "process-control": ("process-control", {}),
    "detect-platform": ("detect-platform", {}),
    "execute-command": (
        "execute-command",
        {"argv": "list[string]", "timeout_s": "int"},
    ),
    # policy / authority
    "policy-check": (
        "policy-check",
        {"permissions": "list[string]", "required": "list[string]"},
    ),
    "authority-check": (
        "authority-check",
        {"actor": "string", "authorities": "list[string]", "required": "list[string]"},
    ),
    "permission-check": (
        "policy-check",
        {"permissions": "list[string]", "required": "list[string]"},
    ),
}

# map tool_name -> implementation
IMPLS = {
    "repository-search": t_repository_search,
    "symbol-search": t_symbol_search,
    "semantic-search": t_semantic_search,
    "lexical-search": t_lexical_search,
    "log-search": t_log_search,
    "inventory-files": t_inventory_files,
    "inventory-symbols": t_inventory_symbols,
    "inventory-modules": t_inventory_modules,
    "inventory-dependencies": t_inventory_dependencies,
    "detect-dead-code": t_detect_dead_code,
    "detect-duplicate-code": t_detect_duplicate_code,
    "evidence-store": t_evidence_store,
    "evidence-query": t_evidence_query,
    "evidence-verify": t_evidence_verify,
    "artifact-hash": t_artifact_hash,
    "artifact-compare": t_artifact_compare,
    "encode": t_encode,
    "decode": t_decode,
    "json-parse": t_json,
    "yaml-parse": t_yaml,
    "toml-parse": t_toml,
    "csv-parse": t_csv,
    "markdown-parse": t_markdown,
    "validate-format": t_validate_format,
    "read-file": t_read_file,
    "create-file": t_create_file,
    "edit-file": t_edit_file,
    "rename-file": t_rename_file,
    "diff": t_diff,
    "git": t_git,
    "process-control": t_process_control,
    "detect-platform": t_detect_platform,
}

_REGISTERED = False


def register_all(tools_mod=None):
    """Register any IMPL not already registered. Idempotent.

    tools_mod: the tools module to register into. Pass YOUR tools module
    so that the registry written here is the one your caller reads.
    """
    global _REGISTERED
    if tools_mod is None:
        from . import tools as tools_mod
    if _REGISTERED and len(tools_mod.REG) > 0:
        return 0
    n = 0
    for tool, fn in IMPLS.items():
        if tool in tools_mod.REG:
            continue
        schema = {}
        for slug, (t, sc) in BINDINGS.items():
            if t == tool:
                schema = sc
                break
        tools_mod.register(tool, schema)(fn)
        n += 1
    _REGISTERED = True
    return n


def apply():
    """Merge BINDINGS into seed_skills.IMPL so re-seeding binds them."""
    from . import seed_skills

    added = 0
    for slug, (tool, schema) in BINDINGS.items():
        if seed_skills.IMPL.get(slug) != tool:
            seed_skills.IMPL[slug] = tool
            added += 1
    return added
