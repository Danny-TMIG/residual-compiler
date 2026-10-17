# Enforced limits

Input caps are enforced before any work runs. Every row below corresponds to a
test in `tests/test_input_limits.py`. If a limit is missing here, it is missing
in code — file it as a bug.

| Entry point | Limit | Where enforced | Behavior on exceed |
|---|---|---|---|
| `src.compile_cli` query | 64 KiB | `src/compiler_limits.py` | raises `ValueError` |
| `src.residuals.for_task` tokens | 256 | `src/residuals.py` | truncated to first 256 |
| `residuals_fts MATCH` term length | SQLite default | SQLite | query error, returns `[]` |
| HTTP request body | n/a (no server) | — | — |

## Benchmarks

`python bench/load_fts.py` prints median latency per token count. CI fails if
the worst median exceeds 2000 ms. Run it before and after any change to
`src/residuals.py`.

## Regenerating derived artifacts

Ignored (not tracked): `data/residuals.sqlite`, `data/residuals.jsonl`,
`data/skills.sqlite`, `data/atlas/atlas.sqlite`, `state/runs.sqlite`,
`attestation.json`. Rebuild with `./build.sh` or the `make data` target.


## Skills DB schema

The `skills` table has exactly two columns: `id` (TEXT, the contract identifier)
and `contract` (TEXT, a JSON-serialized `SkillContract`). There is **no**
`impl` column — bound state lives inside the JSON blob at `contract.impl`,
populated by `seed_skills.main()` / `bind_all.apply()`.

To count bound skills: parse `contract` as JSON and check `impl` is truthy.
`SELECT ... WHERE impl != ''` will always fail with
`no such column: impl`.
