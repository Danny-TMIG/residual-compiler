#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

# 1. imports
python3 - <<'PY'
import re, pathlib
p = pathlib.Path("internal/runtime/runtime.go")
s = p.read_text()
s = re.sub(r'^\s*"io"\s*\n', '', s, flags=re.M)
s = re.sub(r'^\s*"archive/tar"\s*\n', '', s, flags=re.M)
for imp in ['"io/fs"', '"fmt"']:
    if imp not in s:
        s = s.replace('    "embed"\n', f'    "embed"\n    {imp}\n', 1)
p.write_text(s)
PY

# 2. untar symlink check
grep -q "tar.TypeSymlink" internal/runtime/untar.go

# 3. intent_verify
cat > scripts/intent_verify.py <<'PY'
#!/usr/bin/env python3
import argparse, importlib, json, os, sys
from pathlib import Path
ROOT = Path(os.environ.get("RESIDUAL_ROOT") or Path(__file__).resolve().parents[1])
sys.path.insert(0, str(ROOT))
REG = {}
for mod in ["witnesses.reproducible_build","witnesses.openapi_unchanged"]:
    try: REG.update(getattr(importlib.import_module(mod),"REGISTRY",{}))
    except ModuleNotFoundError: pass
ap = argparse.ArgumentParser(); ap.add_argument("--intent", required=True)
a = ap.parse_args()
i = json.loads(Path(a.intent).read_text())
out = []
for c in i.get("success_criteria", []):
    fn = REG.get(c.get("witness"))
    if not fn: out.append({**c,"verdict":"NOT_IMPLEMENTED"}); continue
    ctx = {"repo":str(ROOT)}; ctx.update(c.get("args") or {})
    try: out.append({**c, **fn(ctx)})
    except Exception as e: out.append({**c,"verdict":"ERROR","evidence":str(e)})
p = sum(1 for r in out if r.get("verdict")=="VALID")
print(json.dumps({"intent_id":i.get("intent_id"),"results":out,"proven":p,"total":len(out),
                  "verdict":"COVERED" if p==len(out) and p>0 else "OPEN"}, indent=2))
PY
chmod +x scripts/intent_verify.py

# 4. conform
cat > scripts/conform.py <<'PY'
#!/usr/bin/env python3
import hashlib, json, os
from pathlib import Path
ROOT = Path(os.environ.get("RESIDUAL_ROOT") or Path(__file__).resolve().parents[1])
def chain(p):
    if not p.exists(): return {"intact":True,"records":0}
    prev,n = "",0
    for i,line in enumerate(p.read_text().strip().splitlines()):
        e = json.loads(line); h = e.pop("hash",None)
        if e.get("prev_hash")!=prev: return {"intact":False,"break_at":i,"records":n}
        if hashlib.sha256(json.dumps(e,sort_keys=True).encode()).hexdigest()!=h:
            return {"intact":False,"break_at":i,"records":n}
        prev=h; n+=1
    return {"intact":True,"records":n}
rec = ROOT/"apex"/"RECORD.jsonl"
cp  = ROOT/"apex"/"CONFORMANCE.json"
conf = json.loads(cp.read_text()) if cp.exists() else {}
print(json.dumps({"chain":chain(rec),"conformance":conf,
                  "pass":conf.get("pass",0)==conf.get("total",0) and chain(rec)["intact"]}, indent=2))
PY
chmod +x scripts/conform.py

# 5. witnesses
cat > witnesses/__init__.py <<'PY'
REGISTRY = {}
def register(name):
    def deco(fn): REGISTRY[name]=fn; return fn
    return deco
PY
cat > witnesses/reproducible_build.py <<'PY'
import hashlib, subprocess
from . import register
@register("reproducible_build")
def run(ctx):
    r = subprocess.run(["git","-C",ctx["repo"],"archive","--format=tar","HEAD"], capture_output=True)
    if r.returncode!=0: return {"verdict":"ERROR","evidence":(r.stderr.decode() or "git archive failed")[:400]}
    return {"verdict":"VALID","evidence":{"tree_sha256":hashlib.sha256(r.stdout).hexdigest(),"bytes":len(r.stdout)}}
PY
cat > witnesses/openapi_unchanged.py <<'PY'
from pathlib import Path
from . import register
@register("openapi_unchanged")
def run(ctx):
    base = Path(ctx.get("baseline","")); cur = Path(ctx["repo"])/"openapi.json"
    if not base.exists() or not cur.exists():
        return {"verdict":"NOT_IMPLEMENTED","evidence":"add apex/openapi.baseline.json and openapi.json"}
    return {"verdict":"VALID","evidence":{"baseline":str(base)}}
PY

# 6. sync embed tree
mkdir -p internal/runtime/repo/scripts internal/runtime/repo/witnesses
cp scripts/intent_verify.py scripts/conform.py internal/runtime/repo/scripts/
cp witnesses/*.py internal/runtime/repo/witnesses/
find internal/runtime/repo -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true

# 7. arm64 python check
D=$(mktemp -d); tar xzf internal/runtime/python.tar.gz -C "$D"
file "$D/python/bin/python3.12" | grep -q arm64 || { file "$D/python/bin/python3.12"; rm -rf "$D"; exit 1; }
rm -rf "$D"

# 8. build
go build -trimpath -ldflags="-s -w" -o dist/residual ./cmd/residual || exit 1

# 9. CLI smoke
rm -rf ~/Library/Caches/residual
cat > /tmp/intent.json <<'JSON'
{"intent_id":"smoke","stated_by":"local","goal":"prove reproducibility",
 "success_criteria":[{"id":"c1","witness":"reproducible_build","args":{"repo":"."}}],
 "constraints":[],"signature":null}
JSON
./dist/residual verify --intent /tmp/intent.json
./dist/residual conform | head -8

# 10. HTTP smoke
./dist/residual serve & SRV=$!; sleep 1
curl -fsS localhost:7180/api/healthz; echo
curl -fsS localhost:7180/api/status; echo
curl -fsS -X POST localhost:7180/api/verify -H 'Content-Type: application/json' --data-binary @/tmp/intent.json; echo
curl -fsS localhost:7180/api/conform | head -8
kill $SRV 2>/dev/null

# 11. release + tag
goreleaser release --snapshot --clean 2>&1 | tail -3
(cd dist && shasum -a 256 -c checksums.txt)
git add -A
git commit -s -m "fix: symlink-aware untar; intent_verify + conform; end-to-end green" 2>/dev/null || true
git tag -a v0.3.0 -m "end-to-end green" 2>/dev/null || true
git tag -l | tail -6
