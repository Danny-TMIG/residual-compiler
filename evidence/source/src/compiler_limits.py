"""
Enforce residual->skill limits at compile time.

Rule: if the compiler matched a residual, any skill listed under that
residual's `forbids` in data/residual_skill_map.json is removed from the
candidate set (or, in strict mode, blocks the task).

This is a *subtractive* constraint. It never adds a skill.
"""

import json
from pathlib import Path

MAP_PATH = Path("data/residual_skill_map.json")


def load_map(path=None):
    p = Path(path or MAP_PATH)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def apply(matched_residuals, candidate_skills, mode="strict"):
    """
    matched_residuals: list of {"id":..., "residual":..., "class":...}
    candidate_skills:  list of skill slugs (e.g. role_map entries for a role)
    mode: "strict" (block task) | "filter" (drop skills) | "warn" (keep + flag)

    Returns: {
      "mode": mode,
      "forbidden": {skill: residual_id},
      "kept": [...],
      "blocked": bool,
      "reason": str | None,
    }
    """
    m = load_map()
    forbidden = {}
    for r in matched_residuals:
        entry = m.get(r["id"])
        if not entry:
            continue
        for s in entry.get("forbids", []):
            if s in candidate_skills:
                forbidden[s] = r["id"]

    kept = [s for s in candidate_skills if s not in forbidden]
    blocked = mode == "strict" and bool(forbidden)
    reason = None
    if blocked:
        pairs = sorted(forbidden.items())
        reason = "; ".join(f"{s} forbids by residual {r}" for s, r in pairs)
    return {
        "mode": mode,
        "forbidden": forbidden,
        "kept": kept,
        "blocked": blocked,
        "reason": reason,
    }
