# Production runbook

## What this is
An executor for the §01–§08 Dev Agent Skill Atlas. It dispatches §02 skills
(§05 contracts), composes §01 roles, and walks the §08 universal flow. It is
deterministic, fail-closed, and auditable.

## What this is NOT
It does not run a language model. It does not fake skill implementations.
Anything it cannot honestly implement is dispatched as `NOT_RUN`.

## Guarantees

1. **Deterministic**: given the same inputs, the same tools, and the same
   registry, every run produces identical states and identical audit records
   (modulo timestamps).

2. **Fail-closed**: an unknown skill, missing input, unbound tool, permission
   failure, timeout, or broken evidence chain returns a non-`PASS` §07 state.
   There is no path from ambiguity to `PASS`.

3. **Audited**: every dispatch appends a hash-chained record to `evidence.log`.
   Verify with `python -m src.cli verify`. A tampered log fails the check.

4. **Sealed**: every flow run produces `bundles/<run_id>.json` with a top-level
   sha256. Verify with `python -m src.cli verify-bundle <path>`.

5. **Bounded**: every tool call has a hard timeout (`runtime.TIMEOUT_DEFAULT`,
   30s) and output cap (`runtime.OUTPUT_CAP`, 200KB). Exceeding either returns
   `TIMEOUT` / `RESOURCE_EXHAUSTED`, never partial success.

6. **Scoped**: the set of tools the build actually executes is materialized in
   `data/scope.json` at every `seed`. That file is the contract. Anything not
   in it cannot be dispatched.

## Operational commands

    python -m src.cli seed                     # build registry + scope.json
    python -m src.cli scope                    # show what this build executes
    python -m src.cli tools                    # list raw tools registered
    python -m src.cli verify                   # verify evidence chain
    python -m src.cli verify-bundle <path>     # verify a sealed run bundle
    python -m src.cli dispatch <skill> --inputs '<json>'
    python -m src.cli run-role <role> --inputs '<json>'
    python -m src.cli run-flow --inputs '{"_default":{...}}'

## Adding a skill

1. Write the tool in `src/bind_all.py` with `@tools.register("<skill-slug>", {schema})`.
2. Add the skill-slug to the appropriate role in `data/role_map.json` if it
   participates in role composition.
3. `python -m src.cli seed` — the tool becomes dispatchable, `data/scope.json`
   is regenerated.
4. Add a role/flow test.

## Scope (current)

    bound: 73 tools   unbound: 1,616 skills

The 1,616 unbound skills are honest `NOT_RUN`. They require primitives this
environment does not have (kernel APIs, cloud SDKs, model runtimes, media
codecs, formal methods provers, hardware toolchains). The runbook does not
pretend otherwise.

## When the flow stops early

`run-flow` stops at the first stage whose role returns a non-`PASS`/`PARTIAL`.
That is by design. The stopped stage appears in the bundle trace as `NOT_RUN`
with reason "no bound skills" or `INSUFFICIENT_EVIDENCE`. Both mean: the flow
reached a role that this build does not implement.

## Incident response

- `verify` fails: `evidence.log` was truncated or edited. Do not trust any
  bundle produced after the failure point. Rotate `evidence.log` and re-run.
- `verify-bundle` fails: the bundle was tampered with. Discard it.
- A dispatch returns `EXECUTION_FAILURE` on a previously `PASS` skill: the
  underlying tool changed. Re-run `seed` and inspect the schema diff in
  `data/scope.json`.
