#!/usr/bin/env python3
"""org.py — executable org design coverage.

For each role in apex/ORG.json:
  - resolve which crafts it owns
  - check each craft's pass in apex/CRAFTS-STATE.json
  - for must_be_independent roles, check witness != owner (from apex/AUTHORITY.json)
  - record gap if crafts is empty
Emits apex/ORG-STATE.json and exits 0 iff all non-gap roles are covered.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"


def load(n):
    p = APEX / n
    return json.loads(p.read_text()) if p.exists() else None


def main():
    org = load("ORG.json")
    if not org:
        sys.exit("missing apex/ORG.json")
    crafts = load("CRAFTS-STATE.json") or {}
    craft_state = {c["craft"]: c for c in crafts.get("crafts", [])}
    authority = load("AUTHORITY.json") or {}

    rows, unresolved = [], []
    for role in org["roles"]:
        owned = role.get("crafts", [])
        gap = role.get("gap")
        checks = []
        for cid in owned:
            cs = craft_state.get(cid)
            if cs is None:
                checks.append({"craft": cid, "status": "absent"})
                unresolved.append(
                    {"role": role["id"], "craft": cid, "reason": "craft_missing"}
                )
                continue
            if not cs.get("pass"):
                checks.append({"craft": cid, "status": "refuted"})
                unresolved.append(
                    {"role": role["id"], "craft": cid, "reason": "craft_not_passing"}
                )
            else:
                checks.append({"craft": cid, "status": "covered"})
        # independence check
        independence_ok = None
        if role.get("must_be_independent"):
            owners = authority.get("owners", {})
            violators = [
                c["craft"]
                for c in checks
                if c["status"] == "covered"
                and owners.get(c["craft"], {}).get("owner")
                == owners.get(c["craft"], {}).get("witness")
            ]
            independence_ok = len(violators) == 0
            if not independence_ok:
                unresolved.append(
                    {
                        "role": role["id"],
                        "reason": "independence_violated",
                        "violators": violators,
                    }
                )
        rows.append(
            {
                "id": role["id"],
                "name": role["name"],
                "owned": owned,
                "checks": checks,
                "gap": gap,
                "independence_ok": independence_ok,
                "covered": (not gap)
                and all(c["status"] == "covered" for c in checks)
                and len(owned) > 0,
            }
        )

    out = {
        "schema": "org-state/v1",
        "lifecycle": org["lifecycle"],
        "roles": rows,
        "covered": sum(1 for r in rows if r["covered"]),
        "total": len(rows),
        "gaps": [r["id"] for r in rows if r["gap"]],
        "unresolved": unresolved,
        "disclaimer": org["disclaimer"],
        "verdict": "COVERED"
        if not unresolved
        else "UNRESOLVED:"
        + ",".join(sorted({u.get("role") or u.get("reason") for u in unresolved})),
    }
    (APEX / "ORG-STATE.json").write_text(json.dumps(out, indent=2) + "\n")
    print(
        json.dumps(
            {k: out[k] for k in ("covered", "total", "gaps", "verdict")}, indent=2
        )
    )
    return 0 if not unresolved else 1


if __name__ == "__main__":
    sys.exit(main())
