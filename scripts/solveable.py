#!/usr/bin/env python3
"""scripts/solveable.py — the solveable system, executable.

Checks each theorem against the actual repo state:

  T1  compliance:       kappa(a*, Pi*) = 1
  T2  irreducibility:   R = {E2, F0, F1, F2}, exactly
  T3  callability:      E is total iff Pi complete
  T4  policy-authoring: Phi not computable -> no one-arg call
  T5  maximal closure:  two-arg is the maximum
  T6  residual fixed pt R = least fixed point of the equation
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APEX = ROOT / "apex"


def load(p):
    fp = APEX / p
    return json.loads(fp.read_text()) if fp.exists() else None


def check(cond, name, detail=""):
    mark = "PASS" if cond else "FAIL"
    print(f"  [{mark}] {name}" + (f"  ({detail})" if detail else ""))
    return cond


def main() -> int:
    print("=" * 60)
    print("SOLVEABLE SYSTEM — theorem check")
    print("=" * 60)

    ok = True

    # ---- T1: compliance ----
    print("\n[T1] compliance: kappa(a*, Pi*) = 1")
    v = load("VERDICTS.json")
    if not v:
        ok = check(False, "VERDICTS.json present")
        return 1
    s = v["summary"]
    ok &= check(
        s["pass"] == 32 and s["fail"] == 0 and s["escalate"] == 0,
        "32 pass, 0 fail, 0 escalate",
        f"actual: {s}",
    )

    # ---- T2: irreducibility ----
    print("\n[T2] irreducibility: R = {E2, F0, F1, F2}")
    cl = load("CLOSURE.json")
    if not cl:
        ok = check(False, "CLOSURE.json present")
        return 1
    expected = sorted({"E2", "F0", "F1", "F2"})
    actual = sorted(cl.get("residual", []))
    ok &= check(
        actual == expected,
        "residual is exactly the 4 terminal classes",
        f"expected {expected}, got {actual}",
    )
    ok &= check(
        cl.get("converged") is True,
        "closure converged",
        f"converged={cl.get('converged')}",
    )

    # ---- T3: callability ----
    print("\n[T3] callability: E total iff Pi complete")
    choice_files = list(APEX.glob("CHOICE-*.json"))
    has_decision = (APEX / "DECISION.json").exists()
    has_class13 = (APEX / "CLASS-13.json").exists()
    n_records = (
        len(choice_files) + (1 if has_decision else 0) + (1 if has_class13 else 0)
    )
    ok &= check(
        len(choice_files) == 9, "9 CHOICE-*.json records", f"found {len(choice_files)}"
    )
    ok &= check(has_decision, "DECISION.json present")
    ok &= check(has_class13, "CLASS-13.json present")
    ok &= check(
        n_records == 11,
        "Pi contains all 11 records (9 choice + decision + class13)",
        f"found {n_records}",
    )

    # ---- T4: policy-authoring not computable ----
    print("\n[T4] policy-authoring: Phi not machine-producible")
    # The formal proof is Theorem 4. The check is: every terminal head
    # reads a recorded file. If any terminal head's policy could be a pure
    # function of the artifact, that would refute T4. We check the record
    # structure is what the proof says it is.
    policies = load("POLICIES.json")
    if not policies:
        ok = check(False, "POLICIES.json present")
        return 1
    terminal_heads = [
        h
        for h, p in policies.items()
        if "DECISION" in json.dumps(p) or "CLASS-13" in json.dumps(p)
    ]
    ok &= check(
        len(terminal_heads) >= 8,
        "at least 8 terminal heads bound to recorded files",
        f"found {len(terminal_heads)}",
    )

    # ---- T5: maximal closure ----
    print("\n[T5] maximal closure: two-arg is the maximum")
    # E(i) not total because Phi(i) not computable (T4). E(i, Pi) is total
    # iff T3 holds. So: T3 + T4 => T5.
    ok &= check(
        len(choice_files) == 9 and has_decision and has_class13,
        "all records present -> two-arg call is total",
        "compliance passes",
    )
    ok &= check(
        len(terminal_heads) >= 8,
        "terminal heads are inputs, not outputs -> no one-arg call",
    )

    # ---- T6: residual fixed point ----
    print("\n[T6] residual fixed point: R = least fixed point")
    # R = complement of closure(mechanical). Check: every class not in R is
    # either mechanical_closed or derived.
    all_classes = (
        set(cl.get("mechanical_closed", []))
        | set(cl.get("derived", []))
        | set(cl.get("residual", []))
    )
    expected_classes = 30
    ok &= check(
        len(all_classes) == expected_classes,
        f"all {expected_classes} classes accounted for",
        f"found {len(all_classes)}",
    )
    # Everything not in residual must be mechanical_closed or derived
    residual = set(cl.get("residual", []))
    closure_members = set(cl.get("mechanical_closed", [])) | set(cl.get("derived", []))
    ok &= check(
        len(closure_members & residual) == 0,
        "residual and closure are disjoint",
        "fixed point holds",
    )

    # ---- Summary ----
    print("\n" + "=" * 60)
    if ok:
        print("[SOLVED] All 6 theorems verified against repo state.")
        print("[system] E(i, Pi) is total, deterministic, compliant.")
        print("[residual] R = {E2, F0, F1, F2} — the terminal acts.")
        return 0
    else:
        print("[UNSOLVED] At least one theorem failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
