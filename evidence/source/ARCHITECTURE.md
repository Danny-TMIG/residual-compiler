# Architecture

## Data flow
description --> task_compiler --> intent + default + policy check
             --> (if ALLOW) flow.run_flow --> role dispatch --> tools
             --> audit.append per dispatch
             --> bundle.seal at end of run

## Modules
| Module | Role |
|---|---|
| src/parse_atlas.py | Parse atlas.txt -> atlas.sqlite |
| src/bind_*.py | Register tool per §02 skill |
| src/contracts.py | §05 SkillContract, §07 ResultState |
| src/dispatch.py | Validate contract, retry, normalize, audit |
| src/runtime.py | 30s timeout, 200KB cap |
| src/roles.py | Compose skills into a role, aggregate §07 |
| src/flow.py | 31 stages; stop on hard states |
| src/audit.py | Hash-chained evidence.log |
| src/bundle.py | Sealed run bundle, sha256 |
| src/scoped.py | scope.json — what this build executes |
| src/policy.py | ALLOW / DENY / ESCALATE |
| src/policy_builder.py | Validate + build + diff policies |
| src/authorities.py | Resolve actor authorities from data/actors.json |
| src/task_compiler.py | Description -> executable _default |
| src/compile_cli.py | CLI: compile + optional run |
| src/observability.py | Structured logs + health |

## Invariants
- Every dispatch is audited, chained via prev hash.
- Every flow run produces a sealed bundle.
- Unbound skill => NOT_RUN, never PASS.
- Missing contract inputs => INSUFFICIENT_DATA, never EXECUTION_FAILURE.
- Policy: DENY > ESCALATE > ALLOW > default (DENY).
- Every source file in the repo regenerates the rest from atlas.txt + policy_source.py + role_map.json.
