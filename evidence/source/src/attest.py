import hashlib
import json
from pathlib import Path

DIST = Path("dist")
OUT = DIST / "attestation.json"


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def build():
    subs = []
    if (DIST / "seed.json").exists():
        subs.append(
            {
                "name": "seed.json",
                "digest": {"sha256": _sha((DIST / "seed.json").read_bytes())},
            }
        )
    for py in sorted(Path("src").rglob("*.py")):
        subs.append(
            {"name": py.as_posix(), "digest": {"sha256": _sha(py.read_bytes())}}
        )
    return {"schema": 1, "subject": subs}


if __name__ == "__main__":
    DIST.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(build(), indent=2, sort_keys=True))
    print(f"wrote {OUT}")
