"""
Resolve an actor's authorities from an identity + role-grant store, so callers
don't pass --authorities by hand.

Store: data/actors.json
{
  "actors": [
    {"id": "ci-bot", "role": "ci", "authorities": ["change_approved"]},
    {"id": "sre-oncall", "role": "sre", "authorities": ["change_approved","incident_free"]},
    {"id": "release-manager", "role": "release",
     "authorities": ["change_approved","incident_free","release_signed"]}
  ],
  "roles": {
    "ci": ["change_approved"],
    "sre": ["change_approved","incident_free"],
    "release": ["change_approved","incident_free","release_signed"],
    "analyst": []
  }
}
"""

import json
import os
from pathlib import Path

STORE = Path("data/actors.json")


def load(path=None):
    p = Path(path or STORE)
    if not p.exists():
        return {"actors": [], "roles": {}}
    return json.loads(p.read_text())


def resolve(actor_id=None, actor_role=None, store=None):
    """Return (authorities:set, resolved_from:dict)."""
    if actor_id is None:
        actor_id = os.environ.get("ACTOR_ID")
    if actor_role is None:
        actor_role = os.environ.get("ACTOR_ROLE")
    store = store or load()
    found = None
    for a in store.get("actors", []):
        if a["id"] == actor_id:
            found = a
            break
    if found is None and actor_role:
        for a in store.get("actors", []):
            if a.get("role") == actor_role:
                found = a
                break
    auths = set()
    if found:
        auths |= set(found.get("authorities", []))
    if actor_role:
        auths |= set(store.get("roles", {}).get(actor_role, []))
    return auths, {
        "actor_id": actor_id,
        "actor_role": actor_role,
        "matched": found is not None,
    }
