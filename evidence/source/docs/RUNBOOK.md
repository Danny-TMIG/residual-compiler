# Runbook

## What this is
An executor for the §01–§08 Dev Agent Skill Atlas. It compiles a task
description into an executable input set, checks that input against policy,
runs only if allowed, and produces a tamper-evident, sealed record of the
entire chain.

## Guarantees
- Deterministic: identical inputs → identical states and audit records.
- Fail-closed: any ambiguity returns a non-PASS §07 state.
- Audited: every dispatch appends a hash-chained record to evidence.log.
- Sealed: every flow run produces bundles/<run_id>.json with sha256.
- Bounded: 30s per-tool timeout, 200KB output cap.
- Scoped: data/scope.json is the contract of what this build executes.

## The three paths

### Full flow, executable task
    python -m src.compile_cli "audit src for quality" \
      --authorities change_approved --run
    # -> policy ALLOW, flow 31/31, bundle sealed

### Blocked by policy
    python -m src.compile_cli "audit src for quality"
    # -> policy ESCALATE, blocked, reason printed to stderr

### Denied unconditionally (prod deploy in this build)
    python -m src.compile_cli "deploy to prod" \
      --authorities change_approved,incident_free,release_signed
    # -> policy DENY (no-unapproved-prod-deploy), blocked

## Add a skill
1. Add `@tools.register("<atlas-slug>", {schema})` to src/bind_all.py
2. Add `<atlas-slug>` to the relevant role in data/role_map.json if it
   participates in role composition
3. `python -m src.cli seed` — rebuilds data/skills.sqlite and data/scope.json
4. `python -m src.cli run-role <role> --inputs '<json>'` to test

## Add a policy rule
1. Edit `RULES` in data/policy_source.py
2. `python -m src.policy_builder_cli validate`
3. `python -m src.policy_builder_cli build`
4. `python -m src.policy_builder_cli diff <old.json>` to review change

## Verify
    python -m src.cli verify                            # chain integrity
    python -m src.cli verify-bundle bundles/<id>.json   # bundle integrity
    python -m src.policy_builder_cli validate           # policy syntax
    python -m src.cli scope                             # what this build executes

## Scope (current)
Bound: 138 tools / 1689 atlas skills. Unbound: 1551 (correctly NOT_RUN).
Flow: 31/31 given executable inputs; 17/31 given only a task description.

## Incident
- `verify` fails: evidence.log was edited. Rotate it; discard downstream bundles.
- `verify-bundle` fails: the bundle was tampered with. Discard it.
- A previously PASS skill now fails: re-run seed and inspect data/scope.json diff.

## Reproduction
From a clean /tmp/test:
    python -m src.cli seed
    python -m src.compile_cli "audit src for quality" \
      --authorities change_approved --run
