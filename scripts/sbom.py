#!/usr/bin/env python3
"""sbom.py — emit SPDX 2.3 JSON for installed Python packages."""

import datetime as dt
import json
import platform
import sys
from importlib.metadata import distributions
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def spdx_id(name, ver):
    return f"SPDXRef-Package-{name}-{ver}".replace("/", "-").replace("_", "-")


def main():
    pkgs = []
    for d in distributions():
        meta = d.metadata
        name = meta.get("Name") or "unknown"
        ver = d.version or "0"
        lic = meta.get("License") or meta.get("License-Expression") or "NOASSERTION"
        pkgs.append(
            {
                "SPDXID": spdx_id(name, ver),
                "name": name,
                "versionInfo": ver,
                "downloadLocation": "NOASSERTION",
                "licenseConcluded": lic,
                "licenseDeclared": lic,
                "copyrightText": "NOASSERTION",
            }
        )
    now = dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    doc = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "residual-compiler-sbom",
        "documentNamespace": f"https://example.invalid/spdx/residual/{now}",
        "creationInfo": {
            "created": now,
            "creators": [
                "Tool: sbom.py",
                f"Runtime: python-{platform.python_version()}",
            ],
        },
        "packages": pkgs,
        "relationships": [
            {
                "spdxElementId": "SPDXRef-DOCUMENT",
                "relationshipType": "DESCRIBES",
                "relatedSpdxElement": p["SPDXID"],
            }
            for p in pkgs
        ],
    }
    out = ROOT / "apex" / "SBOM.spdx.json"
    out.write_text(json.dumps(doc, indent=2) + "\n")
    print(
        json.dumps(
            {"path": str(out.relative_to(ROOT)), "packages": len(pkgs)}, indent=2
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
