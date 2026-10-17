# residual-compiler

6-layer engineering tapeout: 32 heads, 22 chores, 64 streams, 10 mycelium nodes,
57 sovereign nodes, 6 theorems.

## Quick start

    python3 -m venv .venv && source .venv/bin/activate
    python3 -m pip install -e '.[test]'
    make all

## Targets

- make install  - editable install with test + dev extras
- make test     - pytest
- make lint     - ruff + mypy
- make tapeout  - scripts/tapesout.py
- make braid    - 5-backend graph agreement
- make machine  - apex machine state hardening
- make engines  - engine availability probe
- make all      - everything above

## Status

- braid: 5/5 backends agree
- machine: 111 nodes, validate PASS
- engines: see apex/ENGINES-PROBED.json
