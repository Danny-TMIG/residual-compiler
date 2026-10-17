"""
Policy engine. Policies are JSON rules that gate whether a task is allowed
to execute. Every rule is evaluated; the task runs only if the result is
ALLOW. DENY is terminal. ESCALATE means "would run but requires an actor
whose authorities satisfy the requires list".

Policy file shape:
{
  "rules": [
    {"id": "no-prod-writes",
     "when": {"operation": "deploy", "target_env": "prod"},
     "then": "DENY",
     "reason": "production deploys require a change window"},
    {"id": "read-only-by-default",
     "when": {"operation": "execute"},
     "then": "ESCALATE",
     "requires": ["change_approved"]},
    {"id": "allow-search",
     "when": {"operation": "search"},
     "then": "ALLOW"}
  ],
  "default": "DENY"
}
"""

import json
import re
from pathlib import Path
from .contracts import ResultState

DEFAULT_POLICY_PATH = Path("data/policy.json")


def load(path=None):
    p = Path(path or DEFAULT_POLICY_PATH)
    if not p.exists():
        return {"rules": [], "default": "ALLOW"}
    return json.loads(p.read_text())


def _match(when, ctx):
    """when fields are conjunctive; values may be strings, lists, or regex."""
    for k, want in (when or {}).items():
        have = ctx.get(k)
        if isinstance(want, list):
            if have not in want:
                return False
        elif isinstance(want, str) and want.startswith("re:"):
            if not re.search(want[3:], str(have)):
                return False
        elif have != want:
            return False
    return True


def evaluate(operation_ctx, authorities=None, policy=None):
    """
    operation_ctx: dict with keys like operation, target_env, path, argv, ...
    authorities:   list of strings the caller holds
    Returns: {"decision": "ALLOW"|"DENY"|"ESCALATE",
              "reasons": [...], "matched": [rule_id, ...]}
    """
    policy = policy or load()
    authorities = set(authorities or [])
    matched, reasons = [], []
    decision = None  # first matching DENY wins; ESCALATE upgrades if no DENY
    for rule in policy.get("rules", []):
        if not _match(rule.get("when"), operation_ctx):
            continue
        matched.append(rule["id"])
        then = rule.get("then", "DENY")
        if then == "DENY":
            reasons.append(f"{rule['id']}: {rule.get('reason','denied')}")
            return {"decision": "DENY", "reasons": reasons, "matched": matched}
        if then == "ESCALATE":
            missing = [a for a in rule.get("requires", []) if a not in authorities]
            if missing:
                decision = "ESCALATE"
                reasons.append(f"{rule['id']}: missing authorities {missing}")
            else:
                reasons.append(f"{rule['id']}: authorities satisfied")
                if decision is None:
                    decision = "ALLOW"
        if then == "ALLOW":
            if decision is None:
                decision = "ALLOW"
    if decision is None:
        decision = policy.get("default", "DENY")
        reasons.append(f"default: {decision}")
    return {"decision": decision, "reasons": reasons, "matched": matched}
