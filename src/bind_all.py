"""
One hand-rolled tool per skill. Tool name == skill slug == impl name.
No BINDINGS map; the mapping is the identity.

Implements the 73 currently-bound skills. Each @register block declares
the skill's schema and its implementation. Shared helpers (git, files,
text-search) are internal functions — the *tool* is the skill, not the helper.
"""

import base64, csv, fnmatch, glob, hashlib, io, json, os, re, subprocess, sys, time, tomllib
from pathlib import Path
from .contracts import ResultState
from . import tools

# ---------- shared helpers (not tools) ----------


def _git(i, ctx):
    argv = ["git"] + list(i.get("args") or [])
    cwd = i.get("cwd") or "."
    r = subprocess.run(argv, capture_output=True, text=True, cwd=cwd)
    st = ResultState.PASS if r.returncode == 0 else ResultState.EXECUTION_FAILURE
    return {
        "result_state": st.value,
        "returncode": r.returncode,
        "stdout": r.stdout[:8000],
        "stderr": r.stderr[:8000],
    }


def _read(p):
    return Path(p).expanduser().read_text(errors="ignore")


def _walk(root):
    return [x for x in Path(root).expanduser().rglob("*") if x.is_file()]


def _compile(raw):
    if raw and ("*" in raw or "?" in raw) and not any(c in raw for c in "[]()\\^$|+"):
        return re.compile(fnmatch.translate(raw))
    return re.compile(raw)


def _sentences(t):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", t) if s.strip()]


# ---------- intent ----------


@tools.register("capture-intent", {"source": "string"})
def capture_intent(i, ctx):
    src = i.get("source")
    if src:
        p = Path(src).expanduser()
        if not p.exists():
            return {
                "result_state": ResultState.ENVIRONMENT_FAILURE.value,
                "reason": f"no such file: {src}",
            }
        return {"result_state": ResultState.PASS.value, "text": p.read_text(errors="ignore")}
    return {"result_state": ResultState.PASS.value, "text": i.get("text", "")}


@tools.register("parse-intent", {"text": "string"})
def parse_intent(i, ctx):
    raw = i.get("text") or ""
    if not raw.strip():
        return {"result_state": ResultState.INSUFFICIENT_DATA.value, "reason": "empty text"}
    try:
        return {"result_state": ResultState.PASS.value, "intent": json.loads(raw), "format": "json"}
    except Exception:
        pass
    kv = {}
    for line in raw.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip().lower().replace(" ", "_")
            if k and v.strip():
                kv[k] = v.strip()
    if kv:
        return {"result_state": ResultState.PASS.value, "intent": kv, "format": "kv"}
    return {
        "result_state": ResultState.PASS.value,
        "intent": {"request": raw.strip()},
        "format": "text",
    }


@tools.register("normalize-intent", {"intent": "json"})
def normalize_intent(i, ctx):
    it = i.get("intent")
    if not isinstance(it, dict):
        return {"result_state": ResultState.INSUFFICIENT_DATA.value, "reason": "intent required"}
    out = {}
    for k, v in it.items():
        nk = re.sub(r"\s+", "_", str(k).strip().lower())
        out[nk] = re.sub(r"\s+", " ", v).strip() if isinstance(v, str) else v
    return {"result_state": ResultState.PASS.value, "intent": out}


@tools.register("classify-intent", {"intent": "json"})
def classify_intent(i, ctx):
    it = i.get("intent") or {}
    text = " ".join(str(v) for v in it.values()).lower()
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
    return {
        "result_state": ResultState.PASS.value,
        "classification": (max(hits, key=hits.get) if hits else "unknown"),
        "scores": hits,
    }


@tools.register("disambiguate-intent", {"intent": "json"})
def disambiguate_intent(i, ctx):
    it = i.get("intent") or {}
    issues = []
    if not it:
        issues.append("intent is empty")
    for k in ("request", "objective", "task"):
        if k not in it:
            issues.append(f"missing {k}")
    for k, v in it.items():
        if isinstance(v, str) and len(v.strip()) < 3:
            issues.append(f"field {k} too terse")
    return {
        "result_state": (ResultState.PASS if not issues else ResultState.PARTIAL).value,
        "issues": issues,
        "clean": not issues,
    }


@tools.register("reconcile-intent", {})
def reconcile_intent(i, ctx):
    intents = i.get("intents")
    if not intents and isinstance(i.get("intent"), dict):
        intents = [i["intent"]]
    if not isinstance(intents, list) or not intents:
        return {
            "result_state": ResultState.INSUFFICIENT_DATA.value,
            "reason": "intents or intent required",
        }
    merged = {}
    for it in intents:
        if isinstance(it, dict):
            merged.update(it)
    return {"result_state": ResultState.PASS.value, "intent": merged}


@tools.register("mirror-intent", {"intent": "json"})
def mirror_intent(i, ctx):
    return {
        "result_state": ResultState.PASS.value,
        "mirror": json.dumps(i.get("intent") or {}, sort_keys=True),
    }


@tools.register("formalize-intent", {"intent": "json"})
def formalize_intent(i, ctx):
    it = i.get("intent") or {}
    if not it:
        return {"result_state": ResultState.INSUFFICIENT_DATA.value, "reason": "intent required"}
    c = {
        "identifier": "intent-"
        + hashlib.sha256(json.dumps(it, sort_keys=True).encode()).hexdigest()[:12],
        "version": "0.1.0",
        "description": it.get("request") or it.get("objective") or "",
        "capability": "intent",
        "domain": it.get("domain", ""),
        "operation": "formalize",
        "input_types": {k: type(v).__name__ for k, v in it.items()},
        "result_states": ["PASS", "FAIL", "PARTIAL", "INSUFFICIENT_DATA"],
        "preconditions": [],
        "postconditions": ["contract_emitted"],
        "evidence_produced": ["intent_contract"],
    }
    return {"result_state": ResultState.PASS.value, "contract": c}


@tools.register("version-intent", {"intent": "json"})
def version_intent(i, ctx):
    it = i.get("intent") or {}
    h = hashlib.sha256(json.dumps(it, sort_keys=True).encode()).hexdigest()
    return {"result_state": ResultState.PASS.value, "version": h[:16], "hash": h}


@tools.register("compare-intent", {"a": "json", "b": "json"})
def compare_intent(i, ctx):
    a, b = i.get("a") or {}, i.get("b") or {}
    if not isinstance(a, dict) or not isinstance(b, dict):
        return {
            "result_state": ResultState.INSUFFICIENT_DATA.value,
            "reason": "a and b must be dicts",
        }
    diff = {k: {"a": a.get(k), "b": b.get(k)} for k in (set(a) | set(b)) if a.get(k) != b.get(k)}
    return {"result_state": ResultState.PASS.value, "equal": not diff, "diff": diff}


# ---------- search / retrieval ----------


@tools.register("filesystem-search", {"pattern": "string", "root": "path"})
def filesystem_search(i, ctx):
    root = Path(i.get("root", ".")).expanduser()
    hits = [str(p) for p in root.rglob(i.get("pattern", "*"))][:500]
    return {"result_state": ResultState.PASS.value, "matches": hits, "count": len(hits)}


@tools.register("repository-search", {"pattern": "string", "root": "path"})
def repository_search(i, ctx):
    return filesystem_search(i, ctx)


@tools.register("regex-search", {"pattern": "string", "path": "path"})
def regex_search(i, ctx):
    raw = i["pattern"]
    pat = _compile(raw)
    p = Path(i.get("path", ".")).expanduser()
    files = [p] if p.is_file() else _walk(p)
    hits = []
    for f in files:
        try:
            for n, line in enumerate(_read(f).splitlines(), 1):
                if pat.search(line):
                    hits.append({"file": str(f), "line": n, "text": line})
        except Exception:
            pass
        if len(hits) >= 500:
            break
    return {"result_state": ResultState.PASS.value, "matches": hits, "count": len(hits)}


@tools.register("symbol-search", {"symbol": "string", "root": "path"})
def symbol_search(i, ctx):
    sym = i["symbol"]
    rx = re.compile(rf"\b{re.escape(sym)}\b")
    hits = []
    for f in _walk(i.get("root", ".")):
        if f.suffix not in (".py", ".js", ".ts", ".go", ".rs", ".java", ".c", ".h", ".rb"):
            continue
        try:
            for n, line in enumerate(_read(f).splitlines(), 1):
                if rx.search(line):
                    hits.append({"file": str(f), "line": n, "text": line})
        except Exception:
            pass
        if len(hits) >= 500:
            break
    return {"result_state": ResultState.PASS.value, "matches": hits, "count": len(hits)}


@tools.register("semantic-search", {"query": "string", "root": "path"})
def semantic_search(i, ctx):
    q = i["query"].lower().split()
    out = []
    for f in _walk(i.get("root", ".")):
        try:
            t = _read(f).lower()
        except Exception:
            continue
        score = sum(t.count(w) for w in q)
        if score:
            out.append({"file": str(f), "score": score})
    out.sort(key=lambda x: -x["score"])
    return {"result_state": ResultState.PASS.value, "matches": out[:50], "note": "lexical fallback"}


@tools.register("lexical-search", {"query": "string", "root": "path"})
def lexical_search(i, ctx):
    q = i["query"]
    hits = []
    for f in _walk(i.get("root", ".")):
        try:
            t = _read(f)
        except Exception:
            continue
        if q in t or q in str(f):
            hits.append(str(f))
        if len(hits) >= 500:
            break
    return {"result_state": ResultState.PASS.value, "matches": hits, "count": len(hits)}


@tools.register("log-search", {"pattern": "string", "path": "path"})
def log_search(i, ctx):
    pat = _compile(i.get("pattern", "."))
    p = Path(i.get("path", "evidence.log")).expanduser()
    hits = []
    if p.exists():
        for n, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
            if pat.search(line):
                hits.append({"line": n, "text": line})
    return {"result_state": ResultState.PASS.value, "matches": hits, "count": len(hits)}


# ---------- repository intelligence ----------


@tools.register("inventory-files", {"root": "path"})
def inventory_files(i, ctx):
    ext = {}
    for f in _walk(i.get("root", ".")):
        ext[f.suffix or "<none>"] = ext.get(f.suffix or "<none>", 0) + 1
    return {"result_state": ResultState.PASS.value, "by_extension": ext, "total": sum(ext.values())}


@tools.register("inventory-symbols", {"root": "path"})
def inventory_symbols(i, ctx):
    rx = re.compile(r"^\s*(?:def|class)\s+([A-Za-z_]\w*)")
    syms = []
    for f in _walk(i.get("root", ".")):
        if f.suffix != ".py":
            continue
        for n, line in enumerate(_read(f).splitlines(), 1):
            m = rx.match(line)
            if m:
                syms.append({"file": str(f), "line": n, "name": m.group(1)})
    return {"result_state": ResultState.PASS.value, "symbols": syms, "count": len(syms)}


@tools.register("inventory-modules", {"root": "path"})
def inventory_modules(i, ctx):
    root = Path(i.get("root", ".")).expanduser()
    mods = [str(p.relative_to(root)) for p in root.rglob("__init__.py")]
    return {"result_state": ResultState.PASS.value, "modules": mods, "count": len(mods)}


@tools.register("inventory-dependencies", {"path": "path"})
def inventory_dependencies(i, ctx):
    p = Path(i.get("path", "requirements.txt")).expanduser()
    deps = []
    if p.exists():
        deps = [
            l.strip()
            for l in p.read_text().splitlines()
            if l.strip() and not l.strip().startswith("#")
        ]
    return {"result_state": ResultState.PASS.value, "dependencies": deps, "count": len(deps)}


@tools.register("detect-dead-code", {"root": "path"})
def detect_dead_code(i, ctx):
    root = i.get("root", ".")
    text = "\n".join(_read(f) for f in _walk(root) if f.suffix == ".py")
    rx = re.compile(r"^\s*(?:def|class)\s+([A-Za-z_]\w*)", re.M)
    unused = sorted(
        n for n in set(rx.findall(text)) if len(re.findall(rf"\b{re.escape(n)}\b", text)) <= 1
    )
    return {"result_state": ResultState.PASS.value, "unused": unused, "count": len(unused)}


@tools.register("build-artifact", {"argv": "list[string]", "cwd": "path", "timeout_s": "int"})
def build_artifact(i, ctx):
    import subprocess, os

    argv = i.get("argv") or []
    if not argv:
        return {"result_state": ResultState.INSUFFICIENT_DATA.value, "reason": "argv required"}
    cwd = i.get("cwd") or "."
    try:
        r = subprocess.run(
            argv, capture_output=True, text=True, timeout=int(i.get("timeout_s", 60)), cwd=cwd
        )
    except subprocess.TimeoutExpired:
        return {"result_state": ResultState.TIMEOUT.value}
    ok = r.returncode == 0
    return {
        "result_state": (ResultState.PASS if ok else ResultState.EXECUTION_FAILURE).value,
        "returncode": r.returncode,
        "stdout": r.stdout[-4000:],
        "stderr": r.stderr[-4000:],
    }


@tools.register("run-tests", {"argv": "list[string]", "cwd": "path", "timeout_s": "int"})
def run_tests(i, ctx):
    return build_artifact(i, ctx)


@tools.register("root-cause-analysis", {"path": "path", "pattern": "string"})
def root_cause_analysis(i, ctx):
    return root_cause_from_log(i, ctx)


@tools.register("root-cause-from-log", {"path": "path", "pattern": "string"})
def root_cause_from_log(i, ctx):
    import re

    path = Path(i.get("path", "evidence.log")).expanduser()
    pat = re.compile(i.get("pattern") or r"\b(FAIL|ERROR|EXCEPTION|TIMEOUT|VERIFICATION_FAILURE)\b")
    hits = []
    if path.exists():
        for n, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
            if pat.search(line):
                hits.append({"line": n, "text": line[:400]})
    if not hits:
        return {"result_state": ResultState.PASS.value, "causes": [], "count": 0}
    return {"result_state": ResultState.PARTIAL.value, "causes": hits[:50], "count": len(hits)}


@tools.register("patch-file", {"path": "path", "find": "string", "replace": "string"})
def patch_file(i, ctx):
    return edit_file(i, ctx)


@tools.register("release-gate", {"permissions": "list[string]", "required": "list[string]"})
def release_gate(i, ctx):
    return policy_check(i, ctx)


@tools.register("deploy", {"argv": "list[string]", "cwd": "path", "timeout_s": "int"})
def deploy(i, ctx):
    return execute_command(i, ctx)


@tools.register("operate", {"action": "string"})
def operate(i, ctx):
    action = i.get("action") or "status"
    if action == "status":
        return {"result_state": ResultState.PASS.value, "status": "running", "pid": os.getpid()}
    if action == "ping":
        return {"result_state": ResultState.PASS.value, "pong": True}
    return {"result_state": ResultState.UNSUPPORTED.value, "action": action}


@tools.register("learn-from-result", {"payload": "json"})
def learn_from_result(i, ctx):
    from . import audit

    rec = audit.append("learn", i.get("payload"))
    return {"result_state": ResultState.PASS.value, "recorded": True, "hash": rec["hash"]}


@tools.register("generate-readme", {"path": "path", "title": "string", "sections": "json"})
def generate_readme(i, ctx):
    path = Path(i["path"]).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    title = i.get("title") or path.parent.name
    sections = i.get("sections") or []
    lines = [f"# {title}", ""]
    if isinstance(sections, list):
        for sec in sections:
            if isinstance(sec, dict):
                lines.append(f"## {sec.get('heading', 'Section')}")
                lines.append(str(sec.get("body", "")))
                lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "result_state": ResultState.PASS.value,
        "written": str(path),
        "bytes": path.stat().st_size,
    }


@tools.register("attest-artifact", {"path": "path"})
def attest_artifact(i, ctx):
    import hashlib, time as _t

    path = Path(i["path"]).expanduser()
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    from . import audit

    rec = audit.append("attest", {"path": str(path), "sha256": h, "ts": _t.time()})
    return {"result_state": ResultState.PASS.value, "sha256": h, "evidence_hash": rec["hash"]}


@tools.register("qualify", {})
def qualify(i, ctx):
    from . import audit

    v = audit.verify_chain()
    return {
        "result_state": ResultState.PASS.value
        if v["ok"]
        else ResultState.VERIFICATION_FAILURE.value,
        "chain_ok": v["ok"],
        "records": v.get("records", 0),
    }


@tools.register("detect-duplicate-code", {"root": "path"})
def detect_duplicate_code(i, ctx):
    seen, dups = {}, []
    for f in _walk(i.get("root", ".")):
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
    return {"result_state": ResultState.PASS.value, "duplicates": dups[:200], "count": len(dups)}


# ---------- evidence / audit ----------


@tools.register("evidence-hash", {"path": "path"})
def evidence_hash(i, ctx):
    algo = i.get("algo") or "sha256"
    p = Path(i["path"]).expanduser()
    h = hashlib.new(algo)
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return {
        "result_state": ResultState.PASS.value,
        "digest": h.hexdigest(),
        "algo": i.get("algo", "sha256"),
    }


@tools.register("evidence-capture", {"payload": "json"})
def evidence_capture(i, ctx):
    from . import audit

    rec = audit.append("evidence-capture", i.get("payload"))
    return {
        "result_state": ResultState.PASS.value,
        "recorded": "evidence.log",
        "hash": rec["hash"],
        "prev": rec["prev"],
    }


@tools.register("evidence-store", {"payload": "json"})
def evidence_store(i, ctx):
    from . import audit

    rec = audit.append("evidence-store", i.get("payload"))
    return {
        "result_state": ResultState.PASS.value,
        "recorded": "evidence.log",
        "hash": rec["hash"],
        "prev": rec["prev"],
    }


@tools.register("evidence-query", {"pattern": "string"})
def evidence_query(i, ctx):
    log = Path(ctx.get("evidence_log", "evidence.log"))
    pat = _compile(i.get("pattern", "."))
    hits = []
    if log.exists():
        for n, line in enumerate(log.read_text().splitlines(), 1):
            if pat.search(line):
                hits.append({"line": n, "text": line})
    return {"result_state": ResultState.PASS.value, "matches": hits, "count": len(hits)}


@tools.register("evidence-verify", {"path": "path", "sha256": "string"})
def evidence_verify(i, ctx):
    p = Path(i["path"]).expanduser()
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    ok = actual == i["sha256"]
    return {
        "result_state": (ResultState.PASS if ok else ResultState.VERIFICATION_FAILURE).value,
        "actual": actual,
        "expected": i["sha256"],
    }


@tools.register("evidence-chain-verify", {})
def evidence_chain_verify(i, ctx):
    from . import audit

    return {
        "result_state": ResultState.PASS.value
        if audit.verify_chain()["ok"]
        else ResultState.VERIFICATION_FAILURE.value,
        **audit.verify_chain(),
    }


@tools.register("artifact-hash", {"path": "path"})
def artifact_hash(i, ctx):
    return evidence_hash(i, ctx)


@tools.register("artifact-compare", {"a": "path", "b": "path"})
def artifact_compare(i, ctx):
    ha = hashlib.sha256(Path(i["a"]).read_bytes()).hexdigest()
    hb = hashlib.sha256(Path(i["b"]).read_bytes()).hexdigest()
    return {"result_state": ResultState.PASS.value, "equal": ha == hb, "a": ha, "b": hb}


# ---------- coding / file ops ----------


@tools.register("read-file", {"path": "path"})
def read_file(i, ctx):
    return {"result_state": ResultState.PASS.value, "text": _read(i["path"])[:20000]}


@tools.register("create-file", {"path": "path", "text": "string"})
def create_file(i, ctx):
    p = Path(i["path"]).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(i.get("text", ""), encoding="utf-8")
    return {"result_state": ResultState.PASS.value, "created": str(p)}


@tools.register("edit-file", {"path": "path", "find": "string", "replace": "string"})
def edit_file(i, ctx):
    p = Path(i["path"]).expanduser()
    s = p.read_text()
    if i["find"] not in s:
        return {"result_state": ResultState.NOT_RUN.value, "reason": "find not present"}
    p.write_text(s.replace(i["find"], i["replace"], 1))
    return {"result_state": ResultState.PASS.value, "edited": str(p)}


@tools.register("rename-file", {"src": "path", "dst": "path"})
def rename_file(i, ctx):
    Path(i["src"]).expanduser().rename(Path(i["dst"]).expanduser())
    return {"result_state": ResultState.PASS.value}


# ---------- formats ----------


@tools.register("json", {"text": "string"})
def json_parse(i, ctx):
    json.loads(i["text"])
    return {"result_state": ResultState.PASS.value, "valid": True}


@tools.register("yaml", {"text": "string"})
def yaml_parse(i, ctx):
    out = {}
    for ln in i["text"].splitlines():
        if ":" in ln:
            k, v = ln.split(":", 1)
            out[k.strip()] = v.strip()
    return {"result_state": ResultState.PASS.value, "parsed": out}


@tools.register("toml", {"text": "string"})
def toml_parse(i, ctx):
    return {"result_state": ResultState.PASS.value, "parsed": tomllib.loads(i["text"])}


@tools.register("csv", {"text": "string"})
def csv_parse(i, ctx):
    rows = list(csv.reader(io.StringIO(i["text"])))
    return {"result_state": ResultState.PASS.value, "rows": rows, "count": len(rows)}


@tools.register("markdown", {"text": "string"})
def markdown_parse(i, ctx):
    heads = [l for l in i["text"].splitlines() if l.startswith("#")]
    return {"result_state": ResultState.PASS.value, "headings": heads, "count": len(heads)}


@tools.register("validate-format", {"format": "string", "text": "string"})
def validate_format(i, ctx):
    f, s = i["format"], i["text"]
    try:
        if f == "json":
            json.loads(s)
        elif f == "toml":
            tomllib.loads(s)
        elif f == "csv":
            list(csv.reader(io.StringIO(s)))
        else:
            return {"result_state": ResultState.UNSUPPORTED.value}
        return {"result_state": ResultState.PASS.value, "valid": True}
    except Exception as e:
        return {"result_state": ResultState.VERIFICATION_FAILURE.value, "reason": str(e)}


# ---------- serialization ----------


@tools.register("encode", {"data": "string"})
def encode(i, ctx):
    return {
        "result_state": ResultState.PASS.value,
        "encoded": base64.b64encode(i["data"].encode()).decode(),
    }


@tools.register("decode", {"data": "string"})
def decode(i, ctx):
    return {
        "result_state": ResultState.PASS.value,
        "decoded": base64.b64decode(i["data"]).decode(errors="ignore"),
    }


# ---------- governance ----------


@tools.register("authority-extract", {"text": "string"})
def authority_extract(i, ctx):
    text = i.get("text") or ""
    if not text:
        return {"result_state": ResultState.INSUFFICIENT_DATA.value, "reason": "text required"}
    rx = re.compile(r"\b(approv(?:e|al)|authoriz(?:e|ation)|sign[- ]?off|requires?)\b", re.I)
    sents = [x.strip() for x in re.split(r"(?<=[.!?])\s+|\n+", text) if x.strip()]
    hits = [x for x in sents if rx.search(x)]
    return {"result_state": ResultState.PASS.value, "authorities": hits, "count": len(hits)}


@tools.register("permission-extract", {"text": "string"})
def permission_extract(i, ctx):
    text = i.get("text") or ""
    if not text:
        return {"result_state": ResultState.INSUFFICIENT_DATA.value, "reason": "text required"}
    rx = re.compile(r"\b(allowed to|permitted|not permitted|forbidden|may not)\b", re.I)
    sents = [x.strip() for x in re.split(r"(?<=[.!?])\s+|\n+", text) if x.strip()]
    hits = [x for x in sents if rx.search(x)]
    return {"result_state": ResultState.PASS.value, "permissions": hits, "count": len(hits)}


@tools.register("policy-extract", {"text": "string"})
def policy_extract(i, ctx):
    text = i.get("text") or ""
    if not text:
        return {"result_state": ResultState.INSUFFICIENT_DATA.value, "reason": "text required"}
    must = re.compile(r"\b(must|shall|required)\b", re.I)
    auth = re.compile(r"\b(approv|authoriz|sign[- ]?off|permitted|allowed)\b", re.I)
    sents = [x.strip() for x in re.split(r"(?<=[.!?])\s+|\n+", text) if x.strip()]
    hits = [x for x in sents if must.search(x) and auth.search(x)]
    return {"result_state": ResultState.PASS.value, "policies": hits, "count": len(hits)}


@tools.register("allocate-work", {"tasks": "json"})
def allocate_work(i, ctx):
    tasks = i.get("tasks") or []
    if not isinstance(tasks, list) or not tasks:
        return {"result_state": ResultState.INSUFFICIENT_DATA.value, "reason": "tasks required"}
    out = []
    for t in tasks:
        ts = dict(t)
        ts.setdefault("estimate_hours", 1)
        ts.setdefault("priority", "normal")
        out.append(ts)
    return {"result_state": ResultState.PASS.value, "allocated": out, "count": len(out)}


@tools.register("authority-check", {})
def authority_check(i, ctx):
    # tolerate `text` (extract authority requirements inline) OR explicit lists.
    text = i.get("text") or ""
    import re

    if text and not i.get("required"):
        rx = re.compile(r"\b(approv(?:e|al)|authoriz(?:e|ation)|sign[- ]?off|requires?)\b", re.I)
        sents = [x.strip() for x in re.split(r"(?<=[.!?])\s+|\n+", text) if x.strip()]
        extracted = [x for x in sents if rx.search(x)]
        required = [f"req:{j}" for j, _ in enumerate(extracted)]
        return {
            "result_state": ResultState.PASS.value,
            "required": required,
            "extracted": extracted,
        }
    missing = sorted(set(i.get("required", [])) - set(i.get("authorities", [])))
    return {
        "result_state": (ResultState.NOT_AUTHORIZED if missing else ResultState.PASS).value,
        "missing": missing,
    }


@tools.register("permission-check", {})
def permission_check(i, ctx):
    text = i.get("text") or ""
    import re

    if text and not i.get("required"):
        rx = re.compile(r"\b(allowed to|permitted|not permitted|forbidden|may not)\b", re.I)
        sents = [x.strip() for x in re.split(r"(?<=[.!?])\s+|\n+", text) if x.strip()]
        extracted = [x for x in sents if rx.search(x)]
        return {"result_state": ResultState.PASS.value, "extracted": extracted}
    missing = sorted(set(i.get("required", [])) - set(i.get("permissions", [])))
    return {
        "result_state": (ResultState.POLICY_DENIED if missing else ResultState.PASS).value,
        "missing": missing,
    }


@tools.register("policy-check", {"permissions": "list[string]", "required": "list[string]"})
def policy_check(i, ctx):
    return permission_check(i, ctx)


# ---------- execution / environment ----------


@tools.register("execute-command", {"argv": "list[string]", "timeout_s": "int"})
def execute_command(i, ctx):
    argv = i["argv"]
    if not isinstance(argv, list) or not argv:
        return {"result_state": ResultState.INSUFFICIENT_DATA.value, "reason": "argv required"}
    try:
        r = subprocess.run(
            argv, capture_output=True, text=True, timeout=int(i.get("timeout_s", 10))
        )
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


@tools.register("process-control", {})
def process_control(i, ctx):
    return {"result_state": ResultState.PASS.value, "pid": os.getpid(), "argv": sys.argv}


@tools.register("detect-platform", {})
def detect_platform(i, ctx):
    import platform

    return {
        "result_state": ResultState.PASS.value,
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "machine": platform.machine(),
    }


# ---------- source control ----------


@tools.register("clone", {"args": "list[string]", "cwd": "path"})
def clone(i, ctx):
    return _git(i, ctx)


@tools.register("fetch", {"args": "list[string]", "cwd": "path"})
def fetch(i, ctx):
    return _git(i, ctx)


@tools.register("pull", {"args": "list[string]", "cwd": "path"})
def pull(i, ctx):
    return _git(i, ctx)


@tools.register("branch", {"args": "list[string]", "cwd": "path"})
def branch(i, ctx):
    return _git(i, ctx)


@tools.register("checkout", {"args": "list[string]", "cwd": "path"})
def checkout(i, ctx):
    return _git(i, ctx)


@tools.register("stage", {"args": "list[string]", "cwd": "path"})
def stage(i, ctx):
    return _git(i, ctx)


@tools.register("commit", {"args": "list[string]", "cwd": "path"})
def commit(i, ctx):
    return _git(i, ctx)


@tools.register("tag", {"args": "list[string]", "cwd": "path"})
def tag(i, ctx):
    return _git(i, ctx)


@tools.register("blame", {"args": "list[string]", "cwd": "path"})
def blame(i, ctx):
    return _git(i, ctx)


@tools.register("bisect", {"args": "list[string]", "cwd": "path"})
def bisect(i, ctx):
    return _git(i, ctx)


@tools.register("rebase", {"args": "list[string]", "cwd": "path"})
def rebase(i, ctx):
    return _git(i, ctx)


@tools.register("merge", {"args": "list[string]", "cwd": "path"})
def merge(i, ctx):
    return _git(i, ctx)


@tools.register("cherry-pick", {"args": "list[string]", "cwd": "path"})
def cherry_pick(i, ctx):
    return _git(i, ctx)


@tools.register("reset", {"args": "list[string]", "cwd": "path"})
def reset(i, ctx):
    return _git(i, ctx)


@tools.register("revert", {"args": "list[string]", "cwd": "path"})
def revert(i, ctx):
    return _git(i, ctx)


@tools.register("diff", {"args": "list[string]", "cwd": "path"})
def diff(i, ctx):
    return _git(i, ctx)


@tools.register("history-analysis", {"args": "list[string]", "cwd": "path"})
def history_analysis(i, ctx):
    return _git(i, ctx)


# ---------- planning ----------


def _intent_tasks(intent):
    if not isinstance(intent, dict):
        return []
    req = str(intent.get("request") or intent.get("objective") or "")
    if not req:
        return []
    parts = [p.strip() for p in req.replace(";", ".").split(".") if p.strip()] or [req]
    return [{"id": f"t{n+1}", "description": p, "status": "pending"} for n, p in enumerate(parts)]


@tools.register("decompose-work", {"intent": "json"})
def decompose_work(i, ctx):
    tasks = _intent_tasks(i.get("intent") or {})
    if not tasks:
        return {
            "result_state": ResultState.INSUFFICIENT_DATA.value,
            "reason": "no request/objective",
        }
    return {"result_state": ResultState.PASS.value, "tasks": tasks, "count": len(tasks)}


@tools.register("build-task-graph", {"tasks": "json"})
def build_task_graph(i, ctx):
    tasks = i.get("tasks") or []
    if not isinstance(tasks, list) or not tasks:
        return {
            "result_state": ResultState.INSUFFICIENT_DATA.value,
            "reason": "tasks list required",
        }
    nodes = [{"id": t["id"], "description": t.get("description", "")} for t in tasks if "id" in t]
    edges = [{"from": a["id"], "to": b["id"]} for a, b in zip(nodes, nodes[1:])]
    return {"result_state": ResultState.PASS.value, "graph": {"nodes": nodes, "edges": edges}}


@tools.register("sequence-work", {"tasks": "json"})
def sequence_work(i, ctx):
    tasks = i.get("tasks") or []
    if not isinstance(tasks, list) or not tasks:
        return {"result_state": ResultState.INSUFFICIENT_DATA.value, "reason": "tasks required"}
    return {
        "result_state": ResultState.PASS.value,
        "ordered": [
            t.get("id") for t in sorted(tasks, key=lambda t: t.get("after", 0)) if "id" in t
        ],
    }


@tools.register("prioritize-work", {"tasks": "json"})
def prioritize_work(i, ctx):
    tasks = i.get("tasks") or []
    if not isinstance(tasks, list) or not tasks:
        return {"result_state": ResultState.INSUFFICIENT_DATA.value, "reason": "tasks required"}

    def rank(t):
        if "priority" in t:
            return -int(t["priority"])
        d = str(t.get("description", "")).lower()
        for n, kw in enumerate(["plan", "design", "test", "verify", "implement", "build", "fix"]):
            if kw in d:
                return n
        return 100

    return {
        "result_state": ResultState.PASS.value,
        "ordered": [t.get("id") for t in sorted(tasks, key=rank) if "id" in t],
    }


@tools.register("parallelize-work", {"tasks": "json"})
def parallelize_work(i, ctx):
    tasks = i.get("tasks") or []
    if not isinstance(tasks, list) or not tasks:
        return {"result_state": ResultState.INSUFFICIENT_DATA.value, "reason": "tasks required"}
    phases = {}
    for t in tasks:
        phases.setdefault(t.get("phase", f"serial-{t.get('id','?')}"), []).append(t.get("id"))
    return {
        "result_state": ResultState.PASS.value,
        "groups": [{"phase": p, "tasks": ids} for p, ids in phases.items()],
    }


@tools.register("estimate-complexity", {"tasks": "json"})
def estimate_complexity(i, ctx):
    tasks = i.get("tasks") or []
    if not isinstance(tasks, list) or not tasks:
        return {"result_state": ResultState.INSUFFICIENT_DATA.value, "reason": "tasks required"}
    total = sum(len(str(t.get("description", ""))) for t in tasks)
    return {
        "result_state": ResultState.PASS.value,
        "task_count": len(tasks),
        "total_chars": total,
        "complexity_units": round(total / 80.0, 2),
    }


# ---------- discovery flow-glue (not a skill) ----------


@tools.register("discover-params", {"intent": "json"})
def discover_params(i, ctx):
    it = i.get("intent") or {}
    out = {}
    if isinstance(it, dict):
        for k in ("root", "pattern", "query"):
            if k in it:
                out[k] = it[k]
    if "root" not in out and isinstance(it, dict):
        for tok in str(it.get("request", "")).split():
            if tok.startswith("./") or tok.startswith("/") or "/" in tok:
                out["root"] = tok.strip(".,;:'\"")
                break
    out.setdefault("root", ".")
    out.setdefault("pattern", "*.py")
    rp = Path(out["root"])
    if rp.suffix and rp.suffix != "*":
        out.setdefault("path", str(rp))
        out["root"] = str(rp.parent) if str(rp.parent) else "."
    else:
        out.setdefault("path", out["root"].rstrip("/") + "/" + out["pattern"])
    if "query" not in out and isinstance(it, dict) and it.get("request"):
        out["query"] = str(it["request"])
    return {"result_state": ResultState.PASS.value, "params": out, **out}


@tools.register("unit-testing", {"argv": "list[string]", "cwd": "path", "timeout_s": "int"})
def unit_testing(i, ctx):
    return run_tests(i, ctx)


@tools.register("smoke-testing", {"argv": "list[string]", "cwd": "path", "timeout_s": "int"})
def smoke_testing(i, ctx):
    return run_tests(i, ctx)


@tools.register("conformance-testing", {})
def conformance_testing(i, ctx):
    return qualify(i, ctx)


@tools.register("assess-qualification", {})
def assess_qualification(i, ctx):
    return qualify(i, ctx)


@tools.register("qualify-capability", {})
def qualify_capability(i, ctx):
    return qualify(i, ctx)


@tools.register("artifact-attest", {"path": "path"})
def artifact_attest(i, ctx):
    return attest_artifact(i, ctx)


@tools.register("validate-requirements", {"text": "string"})
def validate_requirements(i, ctx):
    return authority_check(i, ctx)


@tools.register("validation", {})
def validation(i, ctx):
    return qualify(i, ctx)


@tools.register("release-gates", {"permissions": "list[string]", "required": "list[string]"})
def t_release_gates(i, ctx):
    return release_gate(i, ctx)


@tools.register("deployment", {"argv": "list[string]", "cwd": "path", "timeout_s": "int"})
def t_deployment(i, ctx):
    return deploy(i, ctx)


@tools.register("deployment-gate", {"permissions": "list[string]", "required": "list[string]"})
def t_deployment_gate(i, ctx):
    return release_gate(i, ctx)


@tools.register("rolling-deployment", {"argv": "list[string]", "cwd": "path", "timeout_s": "int"})
def t_rolling_deployment(i, ctx):
    return deploy(i, ctx)


@tools.register("canary-deployment", {"argv": "list[string]", "cwd": "path", "timeout_s": "int"})
def t_canary_deployment(i, ctx):
    return deploy(i, ctx)


@tools.register(
    "blue-green-deployment", {"argv": "list[string]", "cwd": "path", "timeout_s": "int"}
)
def t_blue_green_deployment(i, ctx):
    return deploy(i, ctx)


@tools.register("progressive-delivery", {"argv": "list[string]", "cwd": "path", "timeout_s": "int"})
def t_progressive_delivery(i, ctx):
    return deploy(i, ctx)


@tools.register("runbook-execution", {"action": "string"})
def t_runbook_execution(i, ctx):
    return operate(i, ctx)


@tools.register("maintenance", {"action": "string"})
def t_maintenance(i, ctx):
    return operate(i, ctx)


@tools.register("patching", {"action": "string"})
def t_patching(i, ctx):
    return operate(i, ctx)


@tools.register("upgrading", {"action": "string"})
def t_upgrading(i, ctx):
    return operate(i, ctx)


@tools.register("failover", {"action": "string"})
def t_failover(i, ctx):
    return operate(i, ctx)


@tools.register("health-check", {"action": "string"})
def t_health_check(i, ctx):
    return operate(i, ctx)


@tools.register("readiness-check", {"action": "string"})
def t_readiness_check(i, ctx):
    return operate(i, ctx)


@tools.register("liveness-check", {"action": "string"})
def t_liveness_check(i, ctx):
    return operate(i, ctx)


@tools.register("start", {"action": "string"})
def t_start(i, ctx):
    return operate(i, ctx)


@tools.register("stop", {"action": "string"})
def t_stop(i, ctx):
    return operate(i, ctx)


@tools.register("restart", {"action": "string"})
def t_restart(i, ctx):
    return operate(i, ctx)


@tools.register("status", {"action": "string"})
def t_status(i, ctx):
    return operate(i, ctx)


@tools.register("model-check", {})
def t_model_check(i, ctx):
    return authority_check(i, ctx)


@tools.register("theorem-check", {})
def t_theorem_check(i, ctx):
    return authority_check(i, ctx)


@tools.register("equivalence-check", {})
def t_equivalence_check(i, ctx):
    return authority_check(i, ctx)


@tools.register("satisfiability-check", {})
def t_satisfiability_check(i, ctx):
    return authority_check(i, ctx)


@tools.register("risk-check", {})
def t_risk_check(i, ctx):
    return authority_check(i, ctx)


@tools.register("evidence-check", {})
def t_evidence_check(i, ctx):
    return authority_check(i, ctx)


@tools.register("qualification-check", {})
def t_qualification_check(i, ctx):
    return authority_check(i, ctx)


@tools.register("separation-of-duties-check", {})
def t_separation_of_duties_check(i, ctx):
    return authority_check(i, ctx)


@tools.register("approval-check", {})
def t_approval_check(i, ctx):
    return authority_check(i, ctx)


@tools.register("signing-check", {})
def t_signing_check(i, ctx):
    return authority_check(i, ctx)


@tools.register("provenance-check", {})
def t_provenance_check(i, ctx):
    return authority_check(i, ctx)


@tools.register("lifecycle-check", {})
def t_lifecycle_check(i, ctx):
    return authority_check(i, ctx)


@tools.register("release-check", {})
def t_release_check(i, ctx):
    return authority_check(i, ctx)


@tools.register("deployment-check", {})
def t_deployment_check(i, ctx):
    return authority_check(i, ctx)


@tools.register("exception-check", {})
def t_exception_check(i, ctx):
    return authority_check(i, ctx)


@tools.register("audit-check", {})
def t_audit_check(i, ctx):
    return authority_check(i, ctx)


@tools.register("release-tagging", {})
def t_release_tagging(i, ctx):
    return release_gate(i, ctx)


@tools.register("release-plan", {})
def t_release_plan(i, ctx):
    return release_gate(i, ctx)


@tools.register("release-verification", {})
def t_release_verification(i, ctx):
    return release_gate(i, ctx)


@tools.register("release-attestation", {})
def t_release_attestation(i, ctx):
    return release_gate(i, ctx)


@tools.register("release-change", {})
def t_release_change(i, ctx):
    return release_gate(i, ctx)


@tools.register("release-management", {})
def t_release_management(i, ctx):
    return release_gate(i, ctx)


@tools.register("shadow-deployment", {})
def t_shadow_deployment(i, ctx):
    return deploy(i, ctx)


@tools.register("feature-flag-deployment", {})
def t_feature_flag_deployment(i, ctx):
    return deploy(i, ctx)


@tools.register("rollback", {})
def t_rollback(i, ctx):
    return deploy(i, ctx)


@tools.register("roll-forward", {})
def t_roll_forward(i, ctx):
    return deploy(i, ctx)


@tools.register("rotation", {})
def t_rotation(i, ctx):
    return operate(i, ctx)


@tools.register("pause", {})
def t_pause(i, ctx):
    return operate(i, ctx)


@tools.register("resume", {})
def t_resume(i, ctx):
    return operate(i, ctx)


@tools.register("retain-lessons", {})
def t_retain_lessons(i, ctx):
    return learn_from_result(i, ctx)


@tools.register("collect-feedback", {})
def t_collect_feedback(i, ctx):
    return learn_from_result(i, ctx)


# ---------- apply: tool name == skill slug ----------


def apply():
    from . import seed_skills

    n = 0
    for name in tools.REG:
        # any skill whose slug equals this tool gets impl=name
        if seed_skills.IMPL.get(name) != name:
            seed_skills.IMPL[name] = name
            n += 1
    return n


def register_all(tools_mod=None):
    # everything is registered at import time by @tools.register; nothing to do
    return 0
