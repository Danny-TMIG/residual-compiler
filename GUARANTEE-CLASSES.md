# Guarantee Classes — the complete enumeration

Six families, 30 classes. Three kinds: mechanical, oracle, terminal.
The mechanical classes are closed by the pipeline. The oracle classes are
closed by an external reader. The terminal classes are closed by the user.

If a class is missing, this document is wrong, not the pipeline (Family E,
Class E2 — completeness, established by an external reader).

## A — Structural (5, mechanical)
A0 files exist · A1 entry points importable · A2 layout matches pyproject ·
A3 no orphaned modules · A4 deps resolve

## B — Semantic (7, mechanical)
B0 parses · B1 type-checks · B2 lints clean · B3 formats ·
B4 no self-compare/dead branch/shadow · B5 tests pass · B6 coverage ≥ threshold

## C — Behavioral (5, mechanical)
C0 deterministic · C1 reproducible · C2 matrix-equal · C3 no skipped gates · C4 smoke-compile

## D — Contractual (4, mechanical)
D0 API surface · D1 version consistent · D2 parity · D3 assets hashable

## E — Epistemic (6, oracle)
D4 changelog reflects diff · E0 every claim observed · E1 residual named ·
E2 **enumeration complete** (fixed point) · E3 no overclaim · E4 terminal recognized

## F — Terminal (3, terminal)
F0 ship · F1 hold · F2 accept residual

## The theorem
G* = (⋀_{A–D} ρ=V) ∧ (⋀_E ρ=reader) ∧ (⋀_F ρ=T)
A–D is mechanical; E is oracle; F is input. The release gate requires all three.
