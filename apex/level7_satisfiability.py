"""Level 7 — joint satisfiability.

L4 verified each claim independently: each has a counterexample.
L7 verifies the claims jointly: there exists an artifact that satisfies all of them.

This is a new class of guarantee. L1-L6 can all pass on a set of claims
that are jointly unsatisfiable — each claim has teeth, each claim is
independently falsifiable, but no artifact can satisfy all of them.
L7 refuses that state.
"""
from __future__ import annotations
import itertools
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Iterable


class Result(Enum):
    VERIFIED = "VERIFIED"
    REFUTED = "REFUTED"
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True)
class Claim:
    name: str
    predicate: Callable[[Any], bool]
    source: str
    adversarial: tuple


@dataclass(frozen=True)
class Witness:
    """A witness is an artifact that satisfies every claim.
    A claim set with a witness is satisfiable. Without one, unsatisfiable."""
    artifact: Any
    satisfied: tuple[str, ...]

    def __post_init__(self):
        if not self.satisfied:
            raise ValueError("witness must satisfy at least one claim")


def find_witness(claims: tuple[Claim, ...],
                 domain: Iterable[Any],
                 max_search: int = 10_000) -> Result:
    """Search the domain for an artifact satisfying all claims.
    Returns VERIFIED if a witness is found, REFUTED if the domain is
    exhausted without one, UNVERIFIED if the search exceeded max_search."""
    domain = list(domain)
    if len(domain) > max_search:
        return Result.UNVERIFIED
    for x in domain:
        try:
            if all(c.predicate(x) for c in claims):
                return Result.VERIFIED
        except Exception:
            continue
    return Result.REFUTED


def find_witness_constructive(claims: tuple[Claim, ...],
                              constructors: dict[str, Callable[[], Any]]) -> Result:
    """Constructive search: try each constructor. If any produces an artifact
    satisfying all claims, return VERIFIED. If every constructor fails,
    return UNVERIFIED — not REFUTED. Constructive non-existence is not
    proof of unsatisfiability; only exhaustive or SMT search is."""
    for name, make in constructors.items():
        try:
            x = make()
        except Exception:
            continue
        try:
            if all(c.predicate(x) for c in claims):
                return Result.VERIFIED
        except Exception:
            continue
    return Result.UNVERIFIED


def find_witness_smt(claims: tuple[Claim, ...], smt_solver) -> Result:
    """If an SMT solver is available, ask it. The solver either returns a
    model (VERIFIED) or proves unsatisfiable (REFUTED)."""
    try:
        r = smt_solver(claims)
    except Exception:
        return Result.UNVERIFIED
    if r is None:
        return Result.REFUTED
    return Result.VERIFIED


# ============================================================================
# HARNESS — verify the satisfiability layer
# ============================================================================

def main() -> int:
    print("=" * 64)
    print("LEVEL 7 — joint satisfiability")
    print("=" * 64)
    failures = []

    # 1. Two claims that ARE jointly satisfiable
    print("\n[1] satisfiable claims")
    claims_ok = (
        Claim("positive", lambda x: x > 0, "L7", (-1,)),
        Claim("small", lambda x: x < 10, "L7", (10, 11)),
    )
    r = find_witness(claims_ok, domain=range(-5, 15))
    print(f"  [{'ok' if r == Result.VERIFIED else 'FAIL'}] "
          f"positive ∧ small: {r.value}")
    if r != Result.VERIFIED:
        failures.append("satisfiable")

    # 2. Two claims that are NOT jointly satisfiable
    print("\n[2] unsatisfiable claims")
    claims_bad = (
        Claim("positive", lambda x: x > 0, "L7", (-1,)),
        Claim("negative", lambda x: x < 0, "L7", (1,)),
    )
    r = find_witness(claims_bad, domain=range(-5, 15))
    print(f"  [{'ok' if r == Result.REFUTED else 'FAIL'}] "
          f"positive ∧ negative: {r.value}")
    if r != Result.REFUTED:
        failures.append("unsatisfiable")

    # 3. Claims with a constructive witness
    print("\n[3] constructive witness")
    claims_constructive = (
        Claim("is_dict", lambda x: isinstance(x, dict), "L7", (1, "a")),
        Claim("has_key", lambda x: "k" in x, "L7", ({}, {"x": 1})),
    )
    constructors = {
        "empty": lambda: {},
        "with_k": lambda: {"k": 1},
        "with_x": lambda: {"x": 1},
        "raise": lambda: 1 / 0,
    }
    r = find_witness_constructive(claims_constructive, constructors)
    print(f"  [{'ok' if r == Result.VERIFIED else 'FAIL'}] "
          f"is_dict ∧ has_key (constructive): {r.value}")
    if r != Result.VERIFIED:
        failures.append("constructive")

    # 4. Adversarial: two claims each falsifiable, jointly unsatisfiable
    print("\n[4] adversarial: each falsifiable, jointly unsatisfiable")
    adversarial_claims = (
        Claim("alice", lambda x: x == "alice", "L7", ("bob",)),
        Claim("bob", lambda x: x == "bob", "L7", ("alice",)),
    )
    # Each claim has a counterexample → REFUTED at L4. Good.
    # No x satisfies both → REFUTED at L7. Also good.
    r = find_witness(adversarial_claims, domain=("alice", "bob", "carol"))
    print(f"  [{'ok' if r == Result.REFUTED else 'FAIL'}] "
          f"alice ∧ bob: {r.value}")
    if r != Result.REFUTED:
        failures.append("adversarial")

    # 4b. Constructive with no valid constructor → UNVERIFIED
    print("\n[4b] constructive, no valid constructor")
    impossible_constructive = (
        Claim("never", lambda x: False, "L7", (1,)),
    )
    r = find_witness_constructive(impossible_constructive, {"a": lambda: 1})
    print(f"  [{'ok' if r == Result.UNVERIFIED else 'FAIL'}] "
          f"no witness by construction: {r.value}")
    if r != Result.UNVERIFIED:
        failures.append("constructive-unverified")

    # 5. Search budget exceeded → UNVERIFIED, not VERIFIED
    print("\n[5] search budget exceeded")
    big_domain = range(1_000_000)
    r = find_witness(claims_ok, domain=big_domain, max_search=100)
    print(f"  [{'ok' if r == Result.UNVERIFIED else 'FAIL'}] "
          f"budget exceeded: {r.value}")
    if r != Result.UNVERIFIED:
        failures.append("budget")

    print()
    if failures:
        print(f"[gap] {len(failures)} satisfiability checks failed: {failures}")
        return 1
    print(f"[level 7] satisfiability: ok")
    print("  L7 answers what L1-L6 cannot: do the claims describe any artifact?")
    print("  L4 verified each claim has a counterexample.")
    print("  L7 verifies the claims jointly describe at least one artifact.")
    print("  Two claims can both have counterexamples and still be jointly")
    print("  unsatisfiable — L7 catches that; L4 does not.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
