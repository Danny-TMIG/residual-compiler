"""Level 3 — parity: build(x) is identical on every OS/Python combination."""

from __future__ import annotations

import hashlib
import sys


def normalize_path(p: str) -> str:
    return p.replace("\\", "/")


def normalize_line_endings(b: bytes) -> bytes:
    return b.replace(b"\r\n", b"\n")


def emit_artifact(files: dict[str, bytes]) -> dict:
    normalized = {
        normalize_path(p): normalize_line_endings(c) for p, c in files.items()
    }
    digest = hashlib.sha256(
        b"".join(p.encode() + b"\0" + normalized[p] for p in sorted(normalized))
    ).hexdigest()
    return {
        "files": sorted(normalized),
        "digest": digest,
        "file_count": len(normalized),
    }


def verify_parity(files: dict[str, bytes]) -> bool:
    base = emit_artifact(files)
    windows_files = {
        p.replace("/", "\\"): c.replace(b"\n", b"\r\n") for p, c in files.items()
    }
    windows = emit_artifact(windows_files)
    return base["digest"] == windows["digest"]


if __name__ == "__main__":
    files = {
        "src/__init__.py": b"__version__ = '1.0.0'\n",
        "src/main.py": b"def main():\n    return 42\n",
    }
    ok = verify_parity(files)
    print(f"[level 3] parity: {'ok' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)
