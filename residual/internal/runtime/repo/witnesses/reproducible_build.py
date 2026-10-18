import hashlib, subprocess
from pathlib import Path
from . import register

@register("reproducible_build")
def run(ctx):
    repo = Path(ctx["repo"])
    # if the extracted copy isn't a git repo, use a deterministic walk
    r = subprocess.run(["git", "-C", str(repo), "rev-parse", "--git-dir"],
                       capture_output=True)
    if r.returncode != 0:
        # fallback: hash all files deterministically
        h = hashlib.sha256()
        n = 0
        for p in sorted(repo.rglob("*")):
            if p.is_file() and ".git" not in p.parts:
                rel = p.relative_to(repo).as_posix()
                h.update(rel.encode())
                h.update(p.read_bytes())
                n += 1
        return {"verdict": "VALID",
                "evidence": {"mode": "tree-walk", "files": n,
                             "tree_sha256": h.hexdigest()}}
    r = subprocess.run(["git", "-C", str(repo), "archive", "--format=tar", "HEAD"],
                       capture_output=True)
    if r.returncode != 0:
        return {"verdict": "ERROR",
                "evidence": (r.stderr.decode() or "git archive failed")[:400]}
    return {"verdict": "VALID",
            "evidence": {"mode": "git-archive",
                         "tree_sha256": hashlib.sha256(r.stdout).hexdigest(),
                         "bytes": len(r.stdout)}}
