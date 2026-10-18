#!/usr/bin/env python3
"""conformance.py — the honest matrix.

Ring 1: verified in code tonight (a witness script produced a verdict).
Ring 2: declared (doc exists, no verification).
Ring 3: explicitly out of scope.

Reads apex/CRAFTS-STATE.json (produced by control_plane.py).
"""

import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"

# craft -> (standards family letter, ring, note)
MAP = {
    "structural": ("A/B", 2, "sysctl/ioreg only; no IEC 60068 records"),
    "electrical": ("A", 1, "spectral witness; invariant currently refuted:bandwidth"),
    "software": ("D", 1, "braid: 5 runtimes agree on the same graph"),
    "firmware": ("B9/B10", 2, "bootloader node RUNNING; no measured boot chain"),
    "protocol": ("E3/G6", 2, "capability DSL; no OpenAPI/HTTP attestation"),
    "systems": ("J", 2, "closure DSL; no ISMS, no risk register"),
    "data": ("F/M", 1, "idempotency witness (exactly-once proven)"),
    "security": ("H8", 2, "provenance hash chain; not TEE-signed"),
    "verification": ("R", 1, "cross_domain witness; verdict PARTIAL (honest)"),
    "build": ("D7/J7", 1, "braid cross-runtime; SBOM emitted separately"),
}

# Families we explicitly disclaim.
OUT_OF_SCOPE = ["O", "P", "Q"]


def main():
    st = APEX / "CRAFTS-STATE.json"
    if not st.exists():
        print(
            "missing apex/CRAFTS-STATE.json — run scripts/control_plane.py first",
            file=sys.stderr,
        )
        return 1
    crafts = json.loads(st.read_text())
    rows, ring_counts = [], {1: 0, 2: 0, 3: 0}
    for c in crafts["crafts"]:
        fam, ring, note = MAP.get(c["craft"], ("?", 3, "unmapped"))
        ring_counts[ring] += 1
        rows.append(
            {
                "craft": c["craft"],
                "standards_family": fam,
                "ring": ring,
                "gate": c["gate"],
                "witness": c["witness"],
                "witness_rc": c["witness_rc"],
                "witness_verdict": c.get("witness_verdict"),
                "pass": c["pass"],
                "note": note,
            }
        )
    out = {
        "generated": dt.datetime.now(dt.UTC).isoformat(),
        "rings": ring_counts,
        "crafts": rows,
        "out_of_scope_families": OUT_OF_SCOPE,
        "disclaimer": (
            "Ring 1 = code-verified (witness ran, verdict parsed). "
            "Ring 2 = declared, not verified. "
            "Ring 3 = out of scope. Claims above Ring 1 require external audit."
        ),
        "source": "apex/CRAFTS-STATE.json",
    }
    (APEX / "CONFORMANCE.json").write_text(json.dumps(out, indent=2) + "\n")
    print(
        json.dumps(
            {
                "path": "apex/CONFORMANCE.json",
                "rings": ring_counts,
                "pass": sum(1 for r in rows if r["pass"]),
                "total": len(rows),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
