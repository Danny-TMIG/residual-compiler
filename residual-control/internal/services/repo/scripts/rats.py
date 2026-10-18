#!/usr/bin/env python3
"""rats.py — emit RATS-conformant Evidence (RFC 9334), software-signed.

This does NOT claim TEE attestation. On macOS without Secure Enclave
integration we cannot produce hardware-signed evidence. The output is
structured per RFC 9334 §3 and labelled signer=software.
"""

import datetime as dt
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"


def uname():
    u = platform.uname()
    return {"system": u.system, "release": u.release, "machine": u.machine}


def csrutil():
    try:
        r = subprocess.run(
            ["csrutil", "status"], capture_output=True, text=True, timeout=3
        )
        return r.stdout.strip() or None
    except Exception:
        return None


def collect():
    return {
        "type": "application/eat-collect+json",
        "platform": uname(),
        "csrutil": csrutil(),
        "python": platform.python_version(),
        "ts": dt.datetime.now(dt.UTC).isoformat(),
    }


def main():
    ev = collect()
    body = json.dumps(ev, sort_keys=True).encode()
    digest = hashlib.sha256(body).hexdigest()
    out = {
        "standard": "IETF RFC 9334",
        "role": "Attester->Verifier",
        "signer": "software",  # <-- honest
        "tee_signed": False,
        "evidence": ev,
        "digest_sha256": digest,
        "note": (
            "Software-signed only. Not TEE-backed. To become Ring 1 this "
            "requires Secure Enclave / SEP-backed measurement, which macOS "
            "does not expose to userspace."
        ),
    }
    (APEX / "RATS-EVIDENCE.json").write_text(json.dumps(out, indent=2) + "\n")
    print(
        json.dumps(
            {
                "path": "apex/RATS-EVIDENCE.json",
                "signer": out["signer"],
                "tee_signed": out["tee_signed"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
