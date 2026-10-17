# Contributing

## Setup
    python -m venv .venv && . .venv/bin/activate
    pip install -e ".[dev]"
    python -m src.cli seed

## Add a skill
1. `@tools.register("<atlas-slug>", {schema})` in src/bind_all.py
2. Add `<atlas-slug>` to a role in data/role_map.json
3. `python -m src.cli seed`
4. Add a test in tests/test_dispatch.py asserting it PASSes with valid inputs.

## Add a policy rule
1. Add a dict to `RULES` in data/policy_source.py
2. `python -m src.policy_builder_cli validate`
3. `python -m src.policy_builder_cli build`
4. Add a test in tests/test_policy.py.

## Add a flow role
1. Add the role to `data/flow_map.json` mapping a stage -> role
2. Add the role to `data/role_map.json` with a skill list
3. `python -m src.cli run-flow --inputs '<json>'` to test.
