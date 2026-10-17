# Guarantee Classes — the complete lattice

Every class of guarantee that can exist for a software artifact, ordered by
strength. Each class guarantees exactly one thing, and exactly nothing about
the class above it.

## The classes

| Class | Name | Guarantees | Does not guarantee | Mechanism |
|-------|------|------------|-------------------|-----------|
| 0 | Presence | exists | well-formed | `git ls-files`, `gh release view` |
| 1 | Well-formedness | parses | type-correct | `compileall`, `json.loads`, `yaml.safe_load` |
| 2 | Type-correctness | types hold | styled | `mypy`, `tsc`, `pydantic` |
| 3 | Style-conformance | style holds | falsifiable | `ruff`, `eslint`, `black --check` |
| 4 | Falsifiability | claims have teeth | claims satisfied | apex L4 |
| 5 | Satisfiability | claims satisfiable | artifact is the witness | apex L7 |
| 6 | Determinism | deterministic per run | across machines | apex L1 |
| 7 | Reproducibility | reproducible across machines | across OS | apex L2 |
| 8 | Parity | parity across OS | named correctly | apex L3 |
| 9 | Signing | signed by identity | identity knew | `cosign`, `sigstore`, GPG |
| 10 | Provenance | produced by process | process is correct | SLSA attestation |
| 11 | Witness | observed | observer is correct | apex L5 |
| 12 | Composition | composition holds | composition is complete | apex L6 |
| 13 | Completeness | no class missing | artifact is correct | external judge |
| 14 | Correctness | artifact is what was wanted | — terminal | user |

## Independence property

Every class is independent of every other class. An artifact can be:

- type-correct and wrong (`def add(a,b): return a - b` is `(int,int)->int`)
- deterministic and wrong (same wrong answer every run)
- reproducible and wrong (wrong bytes, same on every machine)
- parity and wrong (wrong bytes, same on every OS)
- signed and wrong (known identity signed wrong bytes)
- provenance and wrong (correct process, wrong output)
- observed and wrong (observer said ACCEPTED, artifact is wrong)

That is why the classes are ordered by strength. A chain of all 14 is the
strongest claim you can make, and it still stops at "the artifact is what the
user wanted" — which requires the user to say so.

## The apex's coverage

The 7-level apex covers classes 4–12:

| Apex level | Class covered |
|------------|---------------|
| L1 determinism | Class 6 |
| L2 reproducibility | Class 7 |
| L3 parity | Class 8 |
| L4 falsifiability | Class 4 |
| L5 observer | Class 11 |
| L6 tapeout | Class 12 |
| L7 satisfiability | Class 5 |

The apex does not cover classes 0, 1, 2, 3, 9, 10, 13, 14. Each is covered
by another mechanism:

- Class 0 — `git ls-files`, `gh release view`
- Class 1 — `compileall`, `python -c "import x"`
- Class 2 — `mypy`
- Class 3 — `ruff`
- Class 9 — `cosign sign` / `sigstore` (not in this repo)
- Class 10 — `actions/attest-build-provenance` (in release job)
- Class 13 — external judge
- Class 14 — user

## Full stack for v1.2.1

The complete guarantee for `v1.2.1` is the union of:

1. `git tag v1.2.1` + `gh release view v1.2.1` → Class 0
2. `pre-commit` hooks (ruff, ruff-format, mypy, check-yaml, check-toml,
   trailing-whitespace, end-of-file-fixer) → Classes 1–3
3. `quality` job (ruff, mypy) → Classes 2–3
4. 6 test jobs → Classes 4–8
5. `apex` job → Classes 4–12
6. `security` job (bandit, pip-audit) → application-level vulnerability scan
   (not one of the 15 classes)
7. `sbom` job → Class 10 (partially — SBOM is provenance metadata)
8. `parity` job → Class 8
9. `release` job → Classes 9–10 (SLSA attestation)
10. Observer's judgment → Class 11 (implicit, not enforced)

## The classes that cannot be mechanical

### Class 13 — completeness of the guarantee set

To establish that no class is missing, you would have to enumerate "all
classes" from outside. Any enumeration is itself incomplete — the set of all
sets is not a set. So Class 13 cannot be mechanically established. It
requires an external judge.

### Class 14 — correctness

The artifact does what the user wanted. "Wanted" is not a property of the
artifact; it is a relationship between the artifact and an external intent.
No mechanical system can verify a relationship it cannot observe. It
requires the user.

Both are the observer's domain. The observer's judgment, in the apex's L5, is
the only mechanism that can bridge these classes — and even then, the bridge
is a record, not a proof. It says "an observer said ACCEPTED", not "the
observer was correct."

## What "all classes" means

"All classes of guarantee" is not a set you can enumerate and check off. It
is a lattice: each class is a level, and every level is independent of every
other. Some are mechanical (Classes 0–12). Some are partially mechanical
(9, 10, 11 via signing, attestation, observation). Some are not (13, 14).

The honest complete guarantee is:

> Every class that can be mechanically established on this artifact has
> been. Every class that cannot be mechanically established is recorded as
> an observer's judgment. The system does not claim to have verified the
> classes it cannot verify.

That is the state of `v1.2.1`. The mechanical classes (0–12) are verified by
the pipeline. The non-mechanical classes (13, 14) are unverified, and
unverifiable by any pipeline. They are the user's domain — and the release is
published under the user's signature, not the pipeline's.

The apex stops at Class 12 for a reason. Class 13 and 14 are not apex
problems. They are the user's problems, and the apex's job is to hand off to
the user at the boundary — which is exactly what L5's observer link does.

## The terminal statement

A guarantee is not a property of the artifact. It is a property of the
relationship between the artifact and an observer who knows what the artifact
should be. The mechanical classes are observers that can be mechanized: the
parser, the type checker, the linter, the determinism check, the parity check,
the signature, the attestation, the apex. The non-mechanical classes are
observers that cannot be mechanized: the external judge who knows no class is
missing, the user who knows what they wanted.

The pipeline is the set of mechanizable observers. The observer's judgment is
the set of non-mechanizable observers. The full guarantee is the union. The
apex is the boundary between them.

## Appendix — the two classes that close by hand

### Class 13 — completeness, established by an external reader

An external reader checks that this document enumerates what is actually
there: the jobs in `ci.yml`, the hooks in `.pre-commit-config.yaml`, the
levels in `apex/`, the mechanisms named for each class. If the enumeration
matches, Class 13 is established for this snapshot. If it does not, the
document is wrong, not the pipeline.

### Class 14 — correctness, established by the user

The user decides that `v1.2.1` is the artifact they wanted to ship. No
automation can make that decision. It is the terminal class by construction.
