"""Level 2 — reproducibility: build(src) == build(src), byte-for-byte."""

from __future__ import annotations

import gzip
import io
import os
import sys
import tarfile


def build_tarball(files: dict[str, bytes]) -> bytes:
    epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "0"))
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:
        for path in sorted(files):
            content = files[path]
            info = tarfile.TarInfo(name=path)
            info.size = len(content)
            info.mtime = epoch
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.mode = 0o644
            tar.addfile(info, io.BytesIO(content))
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="wb", mtime=0) as gz:
        gz.write(raw.getvalue())
    return out.getvalue()


def verify_reproducible(files, trials: int = 10) -> bool:
    first = build_tarball(files)
    for _ in range(trials - 1):
        if build_tarball(files) != first:
            return False
    return True


if __name__ == "__main__":
    files = {
        "src/__init__.py": b"__version__ = '1.0.0'\n",
        "src/main.py": b"def main(): return 42\n",
        "pyproject.toml": b"[project]\nname = 'demo'\n",
    }
    ok = verify_reproducible(files)
    print(f"[level 2] reproducibility: {'ok' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)
