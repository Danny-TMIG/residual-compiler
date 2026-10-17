import hashlib
import json
import sys
from pathlib import Path

DIST = Path("dist")
SEED = DIST / "seed.json"


def _seed():
    return {
        "schema": 1,
        "items": [
            {"id": "a", "value": 1},
            {"id": "b", "value": 2},
            {"id": "c", "value": 3},
        ],
    }


def _bytes():
    return json.dumps(_seed(), sort_keys=True, separators=(",", ":")).encode()


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def cmd_seed():
    DIST.mkdir(exist_ok=True)
    SEED.write_bytes(_bytes())
    print(f"seed sha256={_sha(_bytes())}")


def cmd_verify():
    if not SEED.exists():
        print("::error::seed missing", file=sys.stderr)
        sys.exit(1)
    if _sha(_bytes()) != _sha(SEED.read_bytes()):
        print("::error::mismatch", file=sys.stderr)
        sys.exit(1)
    print("chain OK")


def cmd_policy():
    items = json.loads(SEED.read_text())["items"]
    bad = {i["id"] for i in items} - {"a", "b", "c"}
    if bad:
        print(f"::error::ids {sorted(bad)}")
        sys.exit(1)
    print(f"policy OK items={len(items)}")


if __name__ == "__main__":
    {"seed": cmd_seed, "verify": cmd_verify, "policy-validate": cmd_policy}[
        sys.argv[1]
    ]()
