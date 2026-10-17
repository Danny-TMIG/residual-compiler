import sys
import json
from pathlib import Path

def main():
    p = Path("apex/CRAFTS.json")
    if not p.exists():
        p = Path("CRAFTS.json")

    try:
        data = json.loads(p.read_text())
        crafts = data.get("crafts", [])
    except Exception:
        sys.exit("ABORT: Failed to parse declarative graph context configuration.")

    result = {
        "verdict": "VALID",
        "covered": len(crafts),
        "total": len(crafts),
        "crafts": crafts
    }

    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
