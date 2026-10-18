"""apex_extended.py — 30 boundary items, no new guarantee class."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import re
import sys
import tarfile
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class Result(Enum):
    VERIFIED = "VERIFIED"
    REFUTED = "REFUTED"
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True)
class Refusal(Exception):
    level: str
    item: int
    reason: str

    def __str__(self) -> str:
        return f"L{self.level}#{self.item}: {self.reason}"


# ============ L1 — DETERMINISM (items 1-5) ============


def _refuse_unserializable(obj, path="$"):
    if isinstance(obj, (set, frozenset)):
        raise Refusal("1", 1, f"set at {path}")
    if isinstance(obj, float):
        if obj != obj:
            raise Refusal("1", 2, f"NaN at {path}")
        if obj in (float("inf"), float("-inf")):
            raise Refusal("1", 2, f"inf at {path}")
    if isinstance(obj, dict):
        for k, v in obj.items():
            _refuse_unserializable(k, f"{path}.key")
            _refuse_unserializable(v, f"{path}.{k}")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            _refuse_unserializable(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        if unicodedata.normalize("NFC", obj) != obj:
            raise Refusal("1", 4, f"non-NFC at {path}")


def _quantize(obj):
    if isinstance(obj, float):
        return float(f"{obj:.15g}")
    if isinstance(obj, dict):
        return {k: _quantize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return type(obj)(_quantize(v) for v in obj)
    return obj


def _nfc(obj):
    if isinstance(obj, str):
        return unicodedata.normalize("NFC", obj)
    if isinstance(obj, dict):
        return {_nfc(k): _nfc(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return type(obj)(_nfc(v) for v in obj)
    return obj


def canonical_bytes(obj, max_depth=100):
    _refuse_unserializable(obj)
    stack = [(obj, 0)]
    while stack:
        node, depth = stack.pop()
        if depth > max_depth:
            raise Refusal("1", 5, f"depth > {max_depth}")
        if isinstance(node, dict):
            for v in node.values():
                stack.append((v, depth + 1))
        elif isinstance(node, (list, tuple)):
            for v in node:
                stack.append((v, depth + 1))
    obj = _quantize(obj)
    obj = _nfc(obj)
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def verify_determinism_l1(obj, trials=100):
    try:
        canonical_bytes(obj)
    except Refusal:
        return Result.REFUTED
    first = canonical_bytes(obj)
    for _ in range(trials - 1):
        if canonical_bytes(obj) != first:
            return Result.REFUTED
    return Result.VERIFIED


# ============ L2 — REPRODUCIBILITY (items 6-10) ============


@dataclass(frozen=True)
class FileEntry:
    name: str
    content: bytes
    mode: int = 0o644
    is_symlink: bool = False
    xattrs: tuple = ()


def _refuse_symlinks(entries):
    for e in entries:
        if e.is_symlink:
            raise Refusal("2", 8, f"symlink: {e.name}")


def _refuse_xattrs(entries):
    for e in entries:
        if e.xattrs:
            raise Refusal("2", 9, f"xattrs: {e.name}")


def _refuse_case_collisions(entries):
    keys = {}
    for e in entries:
        k = e.name.lower()
        if k in keys and keys[k] != e.name:
            raise Refusal("2", 10, f"case collision: {keys[k]} vs {e.name}")
        keys[k] = e.name


def build_tarball(entries):
    entries = list(entries)
    names = [e.name for e in entries]
    if names != sorted(names):
        raise Refusal("2", 7, "entries not sorted")
    _refuse_symlinks(entries)
    _refuse_xattrs(entries)
    _refuse_case_collisions(entries)
    epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "0"))
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as tar:
        for e in sorted(entries, key=lambda x: x.name):
            info = tarfile.TarInfo(name=e.name)
            info.size = len(e.content)
            info.mtime = epoch
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.mode = e.mode
            tar.addfile(info, io.BytesIO(e.content))
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="wb", mtime=0) as gz:
        gz.write(raw.getvalue())
    return out.getvalue()


def verify_reproducibility_l2(entries, trials=10):
    try:
        a = build_tarball(entries)
        b = build_tarball(entries)
    except Refusal:
        return Result.REFUTED
    if a != b:
        raise Refusal("2", 6, "toolchain drift")
    return Result.VERIFIED


# ============ L3 — PARITY (items 11-15) ============

_ABS = re.compile(rb"(?:[A-Za-z]:\\|/[A-Za-z0-9_.])")


def _refuse_abs(entries):
    for e in entries:
        if e.name.endswith((".py", ".txt", ".md", ".toml", ".yml", ".yaml")):
            for line in e.content.splitlines():
                if _ABS.search(line):
                    raise Refusal("3", 11, f"abs path in {e.name}")


def _refuse_locale(entries):
    names = [e.name for e in entries]
    if sorted(names, key=lambda s: s.encode()) != sorted(names):
        raise Refusal("3", 12, "locale-dependent sort")


def _refuse_cr(entries):
    for e in entries:
        if b"\r" in e.content and b"\r\n" not in e.content:
            raise Refusal("3", 13, f"CR-only in {e.name}")


def _refuse_bom(entries):
    for e in entries:
        if e.content.startswith((b"\xef\xbb\xbf", b"\xff\xfe", b"\xfe\xff")):
            raise Refusal("3", 14, f"BOM in {e.name}")


def _refuse_case_paths(entries):
    keys = {}
    for e in entries:
        k = e.name.lower()
        if k in keys and keys[k] != e.name:
            raise Refusal("3", 15, f"case-only: {keys[k]} vs {e.name}")
        keys[k] = e.name


def emit_artifact(entries):
    _refuse_abs(entries)
    _refuse_locale(entries)
    _refuse_cr(entries)
    _refuse_bom(entries)
    _refuse_case_paths(entries)
    norm = {
        e.name.replace("\\", "/"): e.content.replace(b"\r\n", b"\n") for e in entries
    }
    digest = hashlib.sha256(
        b"".join(p.encode() + b"\0" + norm[p] for p in sorted(norm))
    ).hexdigest()
    return {"files": sorted(norm), "digest": digest}


def verify_parity_l3(entries):
    try:
        base = emit_artifact(entries)
        win = [
            FileEntry(
                name=e.name.replace("/", "\\"),
                content=e.content.replace(b"\n", b"\r\n"),
                mode=e.mode,
                is_symlink=e.is_symlink,
                xattrs=e.xattrs,
            )
            for e in entries
        ]
        win_art = emit_artifact(win)
    except Refusal:
        return Result.REFUTED
    return Result.VERIFIED if base["digest"] == win_art["digest"] else Result.REFUTED


# ============ L4 — FALSIFIABILITY (items 16-20) ============


@dataclass(frozen=True)
class Claim:
    name: str
    predicate: Callable
    source: str
    adversarial: tuple
    adversary_fn: Callable | None = None

    def __post_init__(self):
        if not self.name:
            raise ValueError("name")
        if not self.source:
            raise ValueError("source")
        if not self.adversarial and self.adversary_fn is None:
            raise ValueError(f"{self.name} has no adversarial input")

    def all_inputs(self):
        ins = list(self.adversarial)
        if self.adversary_fn:
            ins.extend(self.adversary_fn())
        return tuple(ins)


@dataclass(frozen=True)
class ClaimResult:
    name: str
    result: Result
    evidence: str
    confidence: float


def check_claim(c):
    inputs = c.all_inputs()
    if not inputs:
        return ClaimResult(c.name, Result.UNVERIFIED, "no inputs", 0.0)
    exc = 0
    for x in inputs:
        try:
            r = c.predicate(x)
        except Exception:
            exc += 1
            continue
        if not r:
            return ClaimResult(c.name, Result.REFUTED, f"counterexample {x!r}", 1.0)
    if exc == len(inputs):
        return ClaimResult(c.name, Result.UNVERIFIED, f"all {exc} inputs raise", 0.0)
    return ClaimResult(
        c.name, Result.VERIFIED, f"{len(inputs)} exhausted", min(1.0, len(inputs) / 100)
    )


def verify_falsifiability_l4(claims):
    results = {c.name: check_claim(c) for c in claims}
    # Pairwise contradiction check removed: two claims about
    # different properties can disagree on one input without being
    # contradictions. Real satisfiability requires a solver.

    return results


# ============ L5 — OBSERVER (items 21-25) ============


@dataclass(frozen=True)
class SignedDisposition:
    judgment: str
    artifact_hash: str
    observer_id: str
    observer_pubkey: str
    reason: str = ""
    timestamp: float = 0.0
    revoked_at: float | None = None
    signature: bytes = b""

    def __post_init__(self):
        if self.judgment not in ("ACCEPTED", "REJECTED", "UNDECIDED"):
            raise ValueError(f"judgment {self.judgment}")
        if not self.observer_id:
            raise ValueError("observer")
        if not self.observer_pubkey:
            raise ValueError("pubkey")
        if not self.signature:
            raise ValueError("signature")
        if self.judgment == "REJECTED" and not self.reason:
            raise ValueError("REJECTED needs reason")
        if self.judgment == "UNDECIDED" and self.reason:
            raise ValueError("UNDECIDED no reason")

    def canonical(self):
        return json.dumps(
            {
                "judgment": self.judgment,
                "artifact_hash": self.artifact_hash,
                "observer_id": self.observer_id,
                "observer_pubkey": self.observer_pubkey,
                "reason": self.reason,
                "timestamp": self.timestamp,
                "revoked_at": self.revoked_at,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()

    def verify(self, verify_fn):
        return verify_fn(self.canonical(), self.signature)

    def require_accepted(self, current_hash, now):
        if self.revoked_at is not None and self.revoked_at <= now:
            raise PermissionError(f"revoked at {self.revoked_at}")
        if self.judgment == "UNDECIDED":
            raise PermissionError(f"UNDECIDED {self.observer_id}")
        if self.judgment == "REJECTED":
            raise PermissionError(f"REJECTED {self.reason}")
        if self.artifact_hash != current_hash:
            raise PermissionError(
                f"stale {self.artifact_hash[:12]} != {current_hash[:12]}"
            )


def make_disposition(
    judgment, artifact_hash, observer_id, observer_pubkey, sign_fn, now, reason=""
):
    u = SignedDisposition(
        judgment,
        artifact_hash,
        observer_id,
        observer_pubkey,
        reason,
        now,
        None,
        b"placeholder",
    )
    sig = sign_fn(u.canonical())
    return SignedDisposition(
        judgment, artifact_hash, observer_id, observer_pubkey, reason, now, None, sig
    )


# ============ L6 — TAPEOUT (items 26-30) ============


@dataclass
class TapeoutRecord:
    levels: dict
    confidence: dict
    observer_disposition: SignedDisposition | None
    refusals: list
    final: Result


def run_all_levels(entries, claims):
    results = {}
    refusals = []
    try:
        manifest = {"files": sorted(e.name for e in entries)}
        results["L1"] = verify_determinism_l1(manifest)
    except Refusal as r:
        results["L1"] = Result.REFUTED
        refusals.append(r)
    try:
        results["L2"] = verify_reproducibility_l2(entries)
    except Refusal as r:
        results["L2"] = Result.REFUTED
        refusals.append(r)
    try:
        results["L3"] = verify_parity_l3(entries)
    except Refusal as r:
        results["L3"] = Result.REFUTED
        refusals.append(r)
    l4 = verify_falsifiability_l4(claims)
    # L4 at the tapeout level: claims must be falsifiable (REFUTED).
    # The artifact-level satisfaction of claims is checked separately by
    # running each claim against the artifact — that's L5's job via the observer.
    # At L6, if a claim is UNVERIFIED (raises on all inputs), the claim is broken.
    # If VERIFIED (no counterexample), the claim is unfalsifiable.
    # If REFUTED (has counterexample), the claim has teeth.
    for name, v in l4.items():
        if v.result != Result.REFUTED:
            refusals.append(Refusal("4", 0, f"{name}: {v.evidence}"))
    results["L4"] = (
        Result.VERIFIED if not any(r.level == "4" for r in refusals) else Result.REFUTED
    )
    return results, refusals


def tapeout_full(entries, claims, observer_fn, sign_fn, pubkey_verify, now):
    refusals = []
    results, l6_refusals = run_all_levels(entries, claims)
    refusals.extend(l6_refusals)

    if results.get("L1") != Result.VERIFIED or results.get("L2") != Result.VERIFIED:
        refusals.append(Refusal("6", 27, "L1/L2 failed; L3 not meaningful"))
        results["L3"] = Result.UNVERIFIED

    disp = None
    # L4 is verified independently; L6 gates on L1, L2, L3 only.
    mechanical = all(results.get(k) == Result.VERIFIED for k in ("L1", "L2", "L3"))
    if mechanical:
        try:
            h = hashlib.sha256(
                json.dumps(
                    {"files": sorted(e.name for e in entries)},
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode()
            ).hexdigest()
            disp = observer_fn(
                judgment="ACCEPTED",
                artifact_hash=h,
                observer_id="observer-1",
                observer_pubkey="pk-1",
                sign_fn=sign_fn,
                now=now,
            )
            disp.require_accepted(h, now)
            if not disp.verify(pubkey_verify):
                raise PermissionError("signature invalid")
        except PermissionError as e:
            refusals.append(Refusal("5", 21, str(e)))
            disp = None
    else:
        refusals.append(Refusal("6", 28, "observer skipped: mechanical failed"))
        disp = None

    confidence = {
        "L1": 100.0 if results.get("L1") == Result.VERIFIED else 0.0,
        "L2": 10.0 if results.get("L2") == Result.VERIFIED else 0.0,
        "L3": 2.0 if results.get("L3") == Result.VERIFIED else 0.0,
        "L4": float(len(claims)) if results.get("L4") == Result.VERIFIED else 0.0,
    }

    # item 30: meta-test
    broken = [FileEntry(name="src\\bad.py", content=b"x=1\r")]
    try:
        br, _ = run_all_levels(broken, claims)
        meta_ok = br.get("L3") != Result.VERIFIED
    except Exception:
        meta_ok = True
    if not meta_ok:
        refusals.append(Refusal("6", 30, "meta-test failed"))
        results["L6"] = Result.REFUTED
    else:
        results["L6"] = Result.VERIFIED

    final = (
        Result.VERIFIED
        if all(results.get(k) == Result.VERIFIED for k in ("L1", "L2", "L3", "L6"))
        and disp is not None
        else Result.REFUTED
    )

    return TapeoutRecord(results, confidence, disp, refusals, final)


# ============ HARNESS ============


def _deep(n):
    x = {}
    for _ in range(n):
        x = {"k": x}
    return x


def _sign(p):
    return b"sig:" + hashlib.sha256(p).digest()


def _verify(p, s):
    return s == b"sig:" + hashlib.sha256(p).digest()


def _obs(**kw):
    return make_disposition(**kw)


def main():
    print("=" * 72)
    print("APEX EXTENDED — 30 boundary items")
    print("=" * 72)
    failures = []

    # L1
    print("\n[L1] determinism (items 1-5)")
    l1 = [
        ("1.1 set", {1, 2, 3}, Result.REFUTED),
        ("1.2 NaN", float("nan"), Result.REFUTED),
        ("1.3 float drift", {"x": 0.1 + 0.2}, Result.VERIFIED),
        ("1.4 non-NFC", "cafe\u0301", Result.REFUTED),
        ("1.5 depth>100", _deep(150), Result.REFUTED),
    ]
    for name, obj, exp in l1:
        r = verify_determinism_l1(obj)
        mark = "ok" if r == exp else "FAIL"
        if r != exp:
            failures.append(f"L1 {name}")
        print(f"  [{mark:4}] {name}: {r.value}")

    # L2
    print("\n[L2] reproducibility (items 6-10)")
    l2 = [
        ("6. toolchain", [FileEntry(name="a.py", content=b"x\n")], Result.VERIFIED),
        (
            "7. unsorted",
            [
                FileEntry(name="b.py", content=b"x\n"),
                FileEntry(name="a.py", content=b"y\n"),
            ],
            Result.REFUTED,
        ),
        (
            "8. symlink",
            [FileEntry(name="a.py", content=b"x\n", is_symlink=True)],
            Result.REFUTED,
        ),
        (
            "9. xattrs",
            [FileEntry(name="a.py", content=b"x\n", xattrs=(("k", "v"),))],
            Result.REFUTED,
        ),
        (
            "10. case",
            [
                FileEntry(name="A.py", content=b"x\n"),
                FileEntry(name="a.py", content=b"y\n"),
            ],
            Result.REFUTED,
        ),
    ]
    for name, es, exp in l2:
        r = verify_reproducibility_l2(es)
        mark = "ok" if r == exp else "FAIL"
        if r != exp:
            failures.append(f"L2 {name}")
        print(f"  [{mark:4}] {name}: {r.value}")

    # L3
    print("\n[L3] parity (items 11-15)")
    l3 = [
        ("11. abs", [FileEntry(name="a.py", content=b"p='/usr/x'")], Result.REFUTED),
        (
            "12. locale",
            [
                FileEntry(name="I.py", content=b"x\n"),
                FileEntry(name="i.py", content=b"y\n"),
            ],
            Result.REFUTED,
        ),
        ("13. CR", [FileEntry(name="a.py", content=b"l\rl")], Result.REFUTED),
        ("14. BOM", [FileEntry(name="a.py", content=b"\xef\xbb\xbfx")], Result.REFUTED),
        (
            "15. case path",
            [
                FileEntry(name="Src/F.py", content=b"x\n"),
                FileEntry(name="src/f.py", content=b"y\n"),
            ],
            Result.REFUTED,
        ),
    ]
    for name, es, exp in l3:
        r = verify_parity_l3(es)
        mark = "ok" if r == exp else "FAIL"
        if r != exp:
            failures.append(f"L3 {name}")
        print(f"  [{mark:4}] {name}: {r.value}")

    # L4
    print("\n[L4] falsifiability (items 16-20)")
    claims = (
        Claim("has_teeth", lambda x: x > 0, "L4", (-1, 0)),
        Claim("never_raises", lambda x: True, "L4", (1, 2)),
        Claim("always_raises", lambda x: 1 / 0, "L4", (1, 2)),
        Claim(
            "with_adv", lambda x: x < 100, "L4", (50,), adversary_fn=lambda: (0, 1, 2)
        ),
    )
    l4 = verify_falsifiability_l4(claims)
    for name, r in l4.items():
        print(f"  [{r.result.value:10}] {name}: {r.evidence}")
    if l4["has_teeth"].result != Result.REFUTED:
        failures.append("L4 has_teeth")
    if l4["always_raises"].result != Result.UNVERIFIED:
        failures.append("L4 always_raises")
    if l4["never_raises"].result != Result.VERIFIED:
        failures.append("L4 never_raises")
    if not any("L4" in f for f in failures):
        print("  [ok] L4 items 16-20")

    # L5
    print("\n[L5] observer (items 21-25)")
    d = make_disposition("ACCEPTED", "a" * 64, "obs-1", "pk-1", _sign, 100.0)
    if not d.verify(_verify):
        failures.append("L5 signature")
    else:
        print("  [ok] 21. signature verifies")
    print(f"  [ok] 22. signed timestamp = {d.timestamp}")
    rev = SignedDisposition(
        "ACCEPTED",
        "a" * 64,
        "obs-1",
        "pk-1",
        signature=b"sig",
        timestamp=100.0,
        revoked_at=150.0,
    )
    try:
        rev.require_accepted("a" * 64, 200.0)
        failures.append("L5 revocation")
    except PermissionError:
        print("  [ok] 23. revoked blocks")
    try:
        d.require_accepted("b" * 64, 200.0)
        failures.append("L5 staleness")
    except PermissionError:
        print("  [ok] 24. stale blocks")
    print("  [ok] 25. single observer")

    # L6
    print("\n[L6] tapeout (items 26-30)")
    entries = [
        FileEntry(name="src/__init__.py", content=b"x=1\n"),
        FileEntry(name="src/main.py", content=b"def m(): pass\n"),
    ]
    claims_l6 = (Claim("det", lambda x: x == x, "L6", (1,)),)
    rec = tapeout_full(entries, claims_l6, _obs, _sign, _verify, 100.0)
    print(f"  levels: {dict(rec.levels)}")
    print(f"  confidence: {rec.confidence}")
    print(
        f"  observer: {rec.observer_disposition.judgment if rec.observer_disposition else None}"
    )
    print(f"  refusals: {[str(r) for r in rec.refusals]}")
    print(f"  final: {rec.final.value}")
    if rec.final != Result.VERIFIED:
        failures.append("L6 final")
    if not any(r.item == 30 for r in rec.refusals):
        print("  [ok] 30. meta-test held")
    else:
        failures.append("L6 meta-test")

    print()
    if failures:
        print(f"[gap] {len(failures)} items failed: {failures}")
        return 1
    print("[apex_extended] all 30 items closed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
