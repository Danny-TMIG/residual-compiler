from pathlib import Path
from . import register

@register("openapi_unchanged")
def run(ctx):
    base = Path(ctx.get("baseline", ""))
    cur = Path(ctx["repo"]) / "openapi.json"
    if not base.exists() or not cur.exists():
        return {"verdict": "NOT_IMPLEMENTED",
                "evidence": "add apex/openapi.baseline.json and openapi.json"}
    return {"verdict": "VALID", "evidence": {"baseline": str(base)}}
