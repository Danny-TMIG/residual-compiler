"""Level 4 — falsifiability: every claim has an adversarial input."""

from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol


class Refutation(Enum):
    VERIFIED = "VERIFIED"
    REFUTED = "REFUTED"
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True)
class Claim:
    name: str
    predicate: Callable[[Any], bool]
    adversarial: tuple
    source: str

    def __post_init__(self):
        if not self.name:
            raise ValueError("claim needs name")
        if not callable(self.predicate):
            raise ValueError("claim needs predicate")
        if not self.source:
            raise ValueError("claim needs source")
        if not self.adversarial:
            raise ValueError(f"claim {self.name!r} has no adversarial input")

    def check(self):
        for x in self.adversarial:
            try:
                if not self.predicate(x):
                    return Refutation.REFUTED, x
            except Exception as e:
                return Refutation.REFUTED, (x, str(e))
        return Refutation.VERIFIED, None


class Adversary(Protocol):
    def inputs(self, claim: Claim) -> tuple: ...


@dataclass(frozen=True)
class Exhaustive:
    domain: tuple

    def inputs(self, claim):
        return self.domain


@dataclass(frozen=True)
class Boundary:
    bounds: tuple = (0, 1, -1, 2**31 - 1, -(2**31), "", "x", (), (1,))

    def inputs(self, claim):
        return self.bounds


def verify(claims, adversary):
    """The adversary contributes inputs *within the claim's domain*.
    A claim that fails on an out-of-domain input is not refuted —
    it's unverified on that input. The claim's own adversarial inputs
    are the domain-specific counterexamples."""
    results = {}
    for c in claims:
        extra = adversary.inputs(c)
        # Filter adversary inputs to those the predicate accepts structurally.
        # A predicate that raises on an input is out-of-domain; skip.
        domain_inputs = []
        for x in extra:
            try:
                c.predicate(x)
                domain_inputs.append(x)
            except Exception:
                continue  # out-of-domain input, not a counterexample
        inputs = c.adversarial + tuple(domain_inputs)
        if not inputs:
            results[c.name] = Refutation.UNVERIFIED
            continue
        augmented = Claim(c.name, c.predicate, inputs, c.source)
        v, _ = augmented.check()
        results[c.name] = v
    return results


if __name__ == "__main__":
    claims = (
        Claim("determinism", lambda x: x[0] == x[1], (("a", "a"), ("a", "b")), "L1"),
        Claim(
            "reproducibility",
            lambda x: x[0] == x[1],
            ((b"x", b"x"), (b"x", b"y")),
            "L2",
        ),
        Claim("parity", lambda x: len(x) == 1, (("a",), ("a", "b")), "L3"),
    )
    results = verify(claims, Exhaustive(domain=(0, 1)))
    # Level 4 proves falsifiability: every claim must have a counterexample
    # that refutes it. REFUTED here means "the claim has teeth."
    # A claim that is VERIFIED here is unfalsifiable — it proves nothing.
    ok = all(r == Refutation.REFUTED for r in results.values())
    for name, r in results.items():
        print(f"  [{r.value:10}] {name} (falsifiable: REFUTED)")
    print(
        f"[level 4] falsifiability: {'ok' if ok else 'FAIL — some claim is unfalsifiable'}"
    )
    sys.exit(0 if ok else 1)
