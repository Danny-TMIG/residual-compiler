import hashlib, subprocess
from . import register

@register("reproducible_build")
def run(ctx):
    r = subprocess.run(["git", "-C", ctx["repo"], "archive", "--format=tar", "HEAD"],
                       capture_output=True)
    if r.returncode != 0:
        return {"verdict": "ERROR", "evidence": (r.stderr.decode() or "git archive failed")[:400]}
    return {"verdict": "VALID",
            "evidence": {"tree_sha256": hashlib.sha256(r.stdout).hexdigest(), "bytes": len(r.stdout)}}
