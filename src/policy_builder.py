"""
Build, validate, and version data/policy.json from a rule list.

A "rule" is one JSON object with `when` (conjunctive conditions), `then`
(ALLOW | DENY | ESCALATE), and optional `requires` (list of authority names
for ESCALATE) or `reason` (string for DENY). This module:

  - validates rule syntax (bad rules fail loudly, not silently)
  - deduplicates ids
  - writes the canonical policy.json with a version + sha256
  - can diff two policies to detect drift
"""

import hashlib, json
from pathlib import Path

VALID_THEN = {"ALLOW", "DENY", "ESCALATE"}
VALID_WHEN_KEYS = {
    "operation",
    "target_env",
    "description",
    "paths",
    "actor_role",
    "actor_id",
    "artifact_kind",
}
DEFAULT_PATH = Path("data/policy.json")


def _canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def validate_rule(rule):
    errs = []
    if not isinstance(rule, dict):
        return ["rule is not an object"]
    if not rule.get("id"):
        errs.append("missing id")
    if rule.get("then") not in VALID_THEN:
        errs.append(f"then must be one of {sorted(VALID_THEN)}")
    when = rule.get("when", {})
    for k in when:
        if k not in VALID_WHEN_KEYS:
            errs.append(f"unknown when-key {k!r} (valid: {sorted(VALID_WHEN_KEYS)})")
    if rule.get("then") == "ESCALATE" and not isinstance(rule.get("requires"), list):
        errs.append("ESCALATE needs `requires` list")
    if rule.get("then") == "DENY" and not rule.get("reason"):
        errs.append("DENY needs `reason` string")
    return errs


def build(rules, default="DENY"):
    seen = set()
    errs = []
    for r in rules:
        e = validate_rule(r)
        if e:
            errs.append(f"{r.get('id','<no-id>')}: {e}")
        rid = r.get("id")
        if rid in seen:
            errs.append(f"duplicate id {rid!r}")
        seen.add(rid)
    if errs:
        raise ValueError("invalid policy:\n  " + "\n  ".join(errs))
    body = {"version": 1, "rules": rules, "default": default}
    body["sha256"] = hashlib.sha256(
        _canon({k: v for k, v in body.items() if k != "sha256"}).encode()
    ).hexdigest()
    return body


def write(policy, path=DEFAULT_PATH):
    Path(path).parent.mkdir(exist_ok=True, parents=True)
    Path(path).write_text(json.dumps(policy, indent=2, ensure_ascii=False))
    return policy["sha256"]


def diff(a_path, b_path):
    a = json.loads(Path(a_path).read_text())
    b = json.loads(Path(b_path).read_text())
    a_ids = {r["id"]: r for r in a.get("rules", [])}
    b_ids = {r["id"]: r for r in b.get("rules", [])}
    return {
        "added": sorted(set(b_ids) - set(a_ids)),
        "removed": sorted(set(a_ids) - set(b_ids)),
        "changed": sorted(i for i in (set(a_ids) & set(b_ids)) if a_ids[i] != b_ids[i]),
        "default_changed": a.get("default") != b.get("default"),
    }
