import sys
from pathlib import Path

ROOT = Path.cwd()
FILES = {}

FILES["README.md"] = "\n".join([
    "# residual-compiler",
    "",
    "6-layer engineering tapeout: 32 heads, 22 chores, 64 streams, 10 mycelium nodes,",
    "57 sovereign nodes, 6 theorems.",
    "",
    "## Quick start",
    "",
    "    python3 -m venv .venv && source .venv/bin/activate",
    "    python3 -m pip install -e '.[test]'",
    "    make all",
    "",
    "## Targets",
    "",
    "- make install  - editable install with test + dev extras",
    "- make test     - pytest",
    "- make lint     - ruff + mypy",
    "- make tapeout  - scripts/tapesout.py",
    "- make braid    - 5-backend graph agreement",
    "- make machine  - apex machine state hardening",
    "- make engines  - engine availability probe",
    "- make all      - everything above",
    "",
    "## Status",
    "",
    "- braid: 5/5 backends agree",
    "- machine: 111 nodes, validate PASS",
    "- engines: see apex/ENGINES-PROBED.json",
    "",
])

FILES["SECURITY.md"] = "\n".join([
    "# Security Policy",
    "",
    "## Reporting a Vulnerability",
    "",
    "Open a private security advisory on this repository, or email the maintainer.",
    "Do not open a public issue.",
    "",
    "Response target: 72 hours. No public disclosure without coordination.",
    "",
    "## Supported Versions",
    "",
    "| Version | Supported |",
    "| ------- | --------- |",
    "| 1.3.x   | yes       |",
    "| 1.2.x   | yes       |",
    "| < 1.2   | no        |",
    "",
])

FILES["CONTRIBUTING.md"] = "\n".join([
    "# Contributing",
    "",
    "## Setup",
    "",
    "    python3 -m venv .venv && source .venv/bin/activate",
    "    python3 -m pip install -e '.[test,dev]'",
    "    pre-commit install",
    "",
    "## Before opening a PR",
    "",
    "    make lint",
    "    make test",
    "",
    "Both must pass. Keep diffs focused; one concern per PR.",
    "",
])

FILES["Dockerfile"] = "\n".join([
    "FROM python:3.12-slim",
    "",
    "RUN apt-get update \\",
    " && apt-get install -y --no-install-recommends git make \\",
    " && rm -rf /var/lib/apt/lists/*",
    "",
    "WORKDIR /app",
    "COPY . .",
    "",
    "RUN python3 -m pip install --no-cache-dir -e '.[test]'",
    "",
    "ENV PYTHONHASHSEED=0",
    "ENTRYPOINT [\"python3\", \"scripts/tapesout.py\"]",
    "",
])

FILES[".github/workflows/ci.yml"] = "\n".join([
    "name: ci",
    "",
    "on:",
    "  push:",
    "    branches: [main]",
    "  pull_request:",
    "",
    "jobs:",
    "  test:",
    "    runs-on: ubuntu-latest",
    "    strategy:",
    "      matrix:",
    "        python-version: ['3.11', '3.12']",
    "    steps:",
    "      - uses: actions/checkout@v4",
    "      - uses: actions/setup-python@v5",
    "        with:",
    "          python-version: ${{ matrix.python-version }}",
    "      - run: python3 -m pip install -e '.[test,dev]'",
    "      - run: python3 -m ruff check src tests scripts apex",
    "      - run: python3 -m mypy src apex",
    "      - run: python3 -m pytest -q",
    "",
])

FILES[".gitignore"] = "\n".join([
    ".venv/",
    "__pycache__/",
    "*.pyc",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    "build/",
    "dist/",
    "*.egg-info/",
    "**/target/",
    "braid/rust/target/",
    "",
])

FILES["docs/adr/0001-architecture.md"] = "\n".join([
    "# ADR 0001 - Architecture",
    "",
    "- Status: proposed",
    "- Date: 2026-10-17",
    "",
    "## Context",
    "",
    "Describe the forces at play.",
    "",
    "## Decision",
    "",
    "Describe the decision.",
    "",
    "## Consequences",
    "",
    "What becomes easier, what becomes harder.",
    "",
])

FILES["docs/rfc/0001-template.md"] = "\n".join([
    "# RFC 0001 - Template",
    "",
    "## Summary",
    "## Motivation",
    "## Detailed design",
    "## Alternatives considered",
    "## Unresolved questions",
    "",
])

FILES["docs/runbooks/README.md"] = "# Runbooks\n\nOperational procedures. One file per incident class.\n"
FILES["docs/postmortems/README.md"] = "# Postmortems\n\nBlameless. One file per incident. Use TEMPLATE.md.\n"
FILES["docs/postmortems/TEMPLATE.md"] = "\n".join([
    "# Postmortem - YYYY-MM-DD - <title>",
    "",
    "## Impact",
    "## Timeline",
    "## Root cause",
    "## Detection",
    "## Response",
    "## Action items",
    "",
])

def main():
    print("root: " + str(ROOT))
    wrote, skipped = [], []
    for rel, content in FILES.items():
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists():
            skipped.append(rel)
            print("[skip]  " + rel + " (exists)")
            continue
        p.write_text(content)
        wrote.append(rel)
        print("[write] " + rel + " (" + str(len(content)) + " bytes)")
    print("")
    print("wrote " + str(len(wrote)) + ", skipped " + str(len(skipped)))
    return 0

if __name__ == "__main__":
    sys.exit(main())
