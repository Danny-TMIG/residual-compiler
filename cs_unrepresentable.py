"""cs_unrepresentable.py — every CS primitive, wrong state unrepresentable."""
from __future__ import annotations
import math
import re
import sys
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


@dataclass(frozen=True)
class BoundedIndex:
    i: int
    length: int
    def __post_init__(self) -> None:
        if self.length < 0:
            raise ValueError("length cannot be negative")
        if not (0 <= self.i < self.length):
            raise ValueError(f"index {self.i} not in [0,{self.length})")


@dataclass(frozen=True)
class Lookup(Generic[K, V]):
    key: K
    value: V
    @classmethod
    def of(cls, m: dict[K, V], key: K) -> "Lookup[K, V]":
        if key not in m:
            raise KeyError(f"key {key!r} not present")
        return cls(key, m[key])


@dataclass(frozen=True)
class SortedKeys(Generic[K]):
    keys: tuple[K, ...]
    def __post_init__(self) -> None:
        for a, b in zip(self.keys, self.keys[1:]):
            if a >= b:
                raise ValueError(f"keys not strictly increasing: {a!r} >= {b!r}")


@dataclass(frozen=True)
class MinHeap(Generic[T]):
    items: tuple[T, ...]
    def __post_init__(self) -> None:
        n = len(self.items)
        for i in range(n // 2):
            left, right = 2 * i + 1, 2 * i + 2
            if left < n and self.items[i] > self.items[left]:
                raise ValueError(f"heap violated at {i} vs left {left}")
            if right < n and self.items[i] > self.items[right]:
                raise ValueError(f"heap violated at {i} vs right {right}")


@dataclass(frozen=True)
class DAG:
    nodes: frozenset[str]
    edges: frozenset[tuple[str, str]]
    def __post_init__(self) -> None:
        for src, dst in self.edges:
            if src not in self.nodes:
                raise ValueError(f"edge source {src!r} unknown")
            if dst not in self.nodes:
                raise ValueError(f"edge target {dst!r} unknown")
        adj: dict[str, list[str]] = {n: [] for n in self.nodes}
        for src, dst in self.edges:
            adj[src].append(dst)
        WHITE, GREY, BLACK = 0, 1, 2
        color = {n: WHITE for n in self.nodes}
        def visit(n: str) -> None:
            color[n] = GREY
            for m in adj[n]:
                if color[m] == GREY:
                    raise ValueError(f"cycle through {m!r}")
                if color[m] == WHITE:
                    visit(m)
            color[n] = BLACK
        for n in self.nodes:
            if color[n] == WHITE:
                visit(n)


@dataclass
class UnionFind:
    parent: dict[str, str]
    def __post_init__(self) -> None:
        for k, v in self.parent.items():
            if v not in self.parent:
                raise ValueError(f"dangling parent {v!r} for {k!r}")
        for start in self.parent:
            seen: set[str] = set()
            cur = start
            while cur != self.parent[cur]:
                if cur in seen:
                    raise ValueError(f"cycle through {cur!r}")
                seen.add(cur)
                cur = self.parent[cur]
    def find(self, x: str) -> str:
        while self.parent[x] != x:
            x = self.parent[x]
        return x


@dataclass(frozen=True)
class PowerOfTwo:
    n: int
    def __post_init__(self) -> None:
        if self.n <= 0 or (self.n & (self.n - 1)) != 0:
            raise ValueError(f"{self.n} is not a positive power of two")


@dataclass(frozen=True)
class TrieKey:
    key: str
    max_depth: int
    def __post_init__(self) -> None:
        if self.max_depth < 0:
            raise ValueError("max_depth cannot be negative")
        if len(self.key) > self.max_depth:
            raise ValueError(f"key length {len(self.key)} > depth {self.max_depth}")


@dataclass(frozen=True)
class SuffixArray:
    sa: tuple[int, ...]
    def __post_init__(self) -> None:
        prev = -1
        for i in self.sa:
            if i < 0:
                raise ValueError("negative suffix index")
            if i <= prev:
                raise ValueError(f"suffix array not strictly increasing at {i}")
            prev = i


@dataclass(frozen=True)
class BloomFilter:
    bits: frozenset[int]
    hashes: int
    def __post_init__(self) -> None:
        if self.hashes <= 0:
            raise ValueError("needs >= 1 hash function")
        if any(b < 0 for b in self.bits):
            raise ValueError("negative bit index")


@dataclass(frozen=True)
class HyperLogLog:
    registers: tuple[int, ...]
    def __post_init__(self) -> None:
        if not self.registers:
            raise ValueError("empty registers")
        if any(r < 0 for r in self.registers):
            raise ValueError("negative register")
    def estimate(self) -> float:
        s = sum(2.0 ** -r for r in self.registers)
        return (len(self.registers) ** 2) / s if s else 0.0


@dataclass(frozen=True)
class CountMinSketch:
    counts: tuple[tuple[int, ...], ...]
    def __post_init__(self) -> None:
        for row in self.counts:
            for c in row:
                if c < 0:
                    raise ValueError("negative count in sketch")


@dataclass(frozen=True)
class MerkleLeaf:
    hex_digest: str
    def __post_init__(self) -> None:
        if not re.fullmatch(r"[0-9a-f]{64}", self.hex_digest):
            raise ValueError("not a sha256")


@dataclass(frozen=True)
class MerklePath:
    siblings: tuple[MerkleLeaf, ...]
    tree_size: int
    def __post_init__(self) -> None:
        if self.tree_size <= 0:
            raise ValueError("empty tree")
        if (self.tree_size & (self.tree_size - 1)) != 0:
            raise ValueError("tree_size must be a power of two")
        expected = self.tree_size.bit_length() - 1
        if len(self.siblings) != expected:
            raise ValueError(
                f"path length {len(self.siblings)} != log2({self.tree_size})={expected}"
            )


@dataclass(frozen=True)
class VectorClock:
    vc: tuple[tuple[str, int], ...]
    def __post_init__(self) -> None:
        names = [n for n, _ in self.vc]
        if names != sorted(set(names)):
            raise ValueError("vector clock keys must be unique and sorted")
        if any(c < 0 for _, c in self.vc):
            raise ValueError("negative clock component")


@dataclass(frozen=True)
class SortedList(Generic[T]):
    items: tuple[T, ...]
    def __post_init__(self) -> None:
        for a, b in zip(self.items, self.items[1:]):
            if a > b:
                raise ValueError(f"not sorted: {a!r} > {b!r}")


@dataclass(frozen=True)
class TraversalStep:
    visited: frozenset[str]
    current: str
    def __post_init__(self) -> None:
        if self.current in self.visited:
            raise ValueError(f"{self.current!r} already visited")


@dataclass(frozen=True)
class NonNegativeWeight:
    w: float
    def __post_init__(self) -> None:
        if not math.isfinite(self.w):
            raise ValueError("weight must be finite")
        if self.w < 0:
            raise ValueError("Dijkstra requires non-negative weights")


@dataclass(frozen=True)
class AdmissibleHeuristic:
    h: float
    true_cost: float
    def __post_init__(self) -> None:
        if self.h > self.true_cost:
            raise ValueError(f"heuristic {self.h} > true cost {self.true_cost}")


@dataclass(frozen=True)
class ShortestPaths:
    distances: tuple[tuple[str, float], ...]
    def __post_init__(self) -> None:
        for k, d in self.distances:
            if not k:
                raise ValueError("empty vertex name")
            if math.isnan(d):
                raise ValueError("NaN distance")


@dataclass(frozen=True)
class DistanceMatrix:
    n: int
    entries: tuple[tuple[float, ...], ...]
    def __post_init__(self) -> None:
        if self.n < 0:
            raise ValueError("negative size")
        if len(self.entries) != self.n:
            raise ValueError("wrong row count")
        for i, row in enumerate(self.entries):
            if len(row) != self.n:
                raise ValueError(f"row {i} wrong length")
            if row[i] != 0:
                raise ValueError(f"diagonal [{i}][{i}] must be 0")


@dataclass(frozen=True)
class Flow:
    edge: tuple[str, str]
    amount: float
    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("negative flow")


@dataclass(frozen=True)
class FlowNetwork:
    source: str
    sink: str
    flows: tuple[Flow, ...]
    def __post_init__(self) -> None:
        if self.source == self.sink:
            raise ValueError("source == sink")
        in_out: dict[str, list[float]] = {}
        for f in self.flows:
            in_out.setdefault(f.edge[0], [0.0, 0.0])[1] += f.amount
            in_out.setdefault(f.edge[1], [0.0, 0.0])[0] += f.amount
        for node, (i, o) in in_out.items():
            if node in (self.source, self.sink):
                continue
            if abs(i - o) > 1e-9:
                raise ValueError(f"flow not conserved at {node!r}: in={i} out={o}")


@dataclass(frozen=True)
class Matrix:
    rows: int
    cols: int
    data: tuple[tuple[float, ...], ...]
    def __post_init__(self) -> None:
        if self.rows < 0 or self.cols < 0:
            raise ValueError("negative shape")
        if len(self.data) != self.rows:
            raise ValueError("row count mismatch")
        for r in self.data:
            if len(r) != self.cols:
                raise ValueError("column count mismatch")
    def __matmul__(self, other: "Matrix") -> "Matrix":
        if self.cols != other.rows:
            raise ValueError(
                f"shape mismatch: {self.rows}x{self.cols} @ {other.rows}x{other.cols}"
            )
        out = [
            [
                sum(self.data[i][k] * other.data[k][j] for k in range(self.cols))
                for j in range(other.cols)
            ]
            for i in range(self.rows)
        ]
        return Matrix(self.rows, other.cols, tuple(tuple(r) for r in out))


@dataclass(frozen=True)
class FFTSignal:
    samples: tuple[complex, ...]
    def __post_init__(self) -> None:
        n = len(self.samples)
        if n == 0 or (n & (n - 1)) != 0:
            raise ValueError(f"FFT length {n} not a power of two")


@dataclass(frozen=True)
class Kernel:
    weights: tuple[float, ...]
    def __post_init__(self) -> None:
        if not self.weights:
            raise ValueError("empty kernel")


@dataclass(frozen=True)
class Assignment:
    literal_to_bool: tuple[tuple[int, bool], ...]
    def __post_init__(self) -> None:
        lits = [lit for lit, _ in self.literal_to_bool]
        if len(lits) != len(set(lits)):
            raise ValueError("duplicate literal")
        seen: dict[int, bool] = {}
        for lit, b in self.literal_to_bool:
            v = abs(lit)
            if v in seen and seen[v] != b:
                raise ValueError(f"variable {v} assigned both true and false")
            seen[v] = b


@dataclass(frozen=True)
class Solved(Generic[T]):
    subproblem: str
    value: T
    def __post_init__(self) -> None:
        if not self.subproblem:
            raise ValueError("empty subproblem identifier")


@dataclass(frozen=True)
class GreedyChoice:
    chosen: Any
    locally_optimal: bool
    def __post_init__(self) -> None:
        if not self.locally_optimal:
            raise ValueError("greedy choice must be locally optimal")


@dataclass(frozen=True)
class Constraint:
    name: str
    satisfied: bool
    def __post_init__(self) -> None:
        if not self.satisfied:
            raise ValueError(f"constraint {self.name!r} not satisfied")


@dataclass(frozen=True)
class Solution:
    assignment: tuple[tuple[str, Any], ...]
    constraints: tuple[Constraint, ...]
    def __post_init__(self) -> None:
        for c in self.constraints:
            if not c.satisfied:
                raise ValueError(f"unsatisfied constraint {c.name!r}")


@dataclass(frozen=True)
class Bound:
    value: float
    incumbent: float
    def __post_init__(self) -> None:
        if self.value > self.incumbent:
            raise ValueError(f"bound {self.value} exceeds incumbent {self.incumbent}")


@dataclass(frozen=True)
class AST:
    source: str
    root: Any
    def __post_init__(self) -> None:
        if not self.source:
            raise ValueError("empty source")
        if self.root is None:
            raise ValueError("no root node")


@dataclass(frozen=True)
class Typed:
    term: str
    ty: str
    def __post_init__(self) -> None:
        if not self.ty:
            raise ValueError("term has no type")


@dataclass(frozen=True)
class Proof:
    theorem: str
    term: str
    checks: bool
    def __post_init__(self) -> None:
        if not self.theorem:
            raise ValueError("empty theorem")
        if not self.checks:
            raise ValueError("proof does not check")


@dataclass(frozen=True)
class LockOrder:
    order: tuple[str, ...]
    def __post_init__(self) -> None:
        if len(set(self.order)) != len(self.order):
            raise ValueError("duplicate lock in order")


@dataclass(frozen=True)
class BoundedPointer:
    offset: int
    size: int
    def __post_init__(self) -> None:
        if self.size < 0:
            raise ValueError("negative size")
        if not (0 <= self.offset < self.size):
            raise ValueError(f"offset {self.offset} not in [0,{self.size})")


@dataclass(frozen=True)
class Message:
    sender: str
    clock: VectorClock
    payload: Any
    def __post_init__(self) -> None:
        if not self.sender:
            raise ValueError("empty sender")


@dataclass(frozen=True)
class Decided:
    value: Any
    decided_at: int
    def __post_init__(self) -> None:
        if self.decided_at < 0:
            raise ValueError("negative consensus round")


@dataclass(frozen=True)
class Linearizable:
    operations: tuple[tuple[int, Any], ...]
    def __post_init__(self) -> None:
        seqs = [s for s, _ in self.operations]
        if seqs != sorted(seqs):
            raise ValueError("operations not in order")
        if len(set(seqs)) != len(seqs):
            raise ValueError("duplicate sequence number")


@dataclass(frozen=True)
class Verified:
    message_hash: str
    signature_valid: bool
    def __post_init__(self) -> None:
        if not re.fullmatch(r"[0-9a-f]{64}", self.message_hash):
            raise ValueError("not a sha256")
        if not self.signature_valid:
            raise ValueError("signature not valid — cannot construct Verified")


@dataclass(frozen=True)
class ZKProof:
    statement: str
    verified: bool
    def __post_init__(self) -> None:
        if not self.statement:
            raise ValueError("empty statement")
        if not self.verified:
            raise ValueError("proof not verified")


@dataclass(frozen=True)
class Decompressed:
    data: bytes
    expected_length: int
    def __post_init__(self) -> None:
        if len(self.data) != self.expected_length:
            raise ValueError(f"length {len(self.data)} != {self.expected_length}")


def _held(fn) -> bool:
    try:
        fn()
    except Exception:
        return True
    return False


def murmuration_holds() -> dict[str, bool]:
    r: dict[str, bool] = {}
    r["bounded_index"] = _held(lambda: BoundedIndex(-1, 5)) and _held(lambda: BoundedIndex(5, 5)) and not _held(lambda: BoundedIndex(0, 5))
    r["lookup"] = _held(lambda: Lookup.of({"a": 1}, "b")) and not _held(lambda: Lookup.of({"a": 1}, "a"))
    r["sorted_keys"] = _held(lambda: SortedKeys((1, 2, 1))) and _held(lambda: SortedKeys((1, 1))) and not _held(lambda: SortedKeys((1, 2, 3)))
    r["min_heap"] = _held(lambda: MinHeap((3, 1, 2))) and not _held(lambda: MinHeap((1, 2, 3)))
    r["dag"] = _held(lambda: DAG(frozenset({"a"}), frozenset({("a", "b")}))) and _held(lambda: DAG(frozenset({"a", "b"}), frozenset({("a", "b"), ("b", "a")}))) and not _held(lambda: DAG(frozenset({"a", "b"}), frozenset({("a", "b")})))
    r["union_find"] = _held(lambda: UnionFind({"a": "b"})) and _held(lambda: UnionFind({"a": "b", "b": "a"})) and not _held(lambda: UnionFind({"a": "a"}))
    r["power_of_two"] = _held(lambda: PowerOfTwo(3)) and _held(lambda: PowerOfTwo(0)) and not _held(lambda: PowerOfTwo(4))
    r["trie_key"] = _held(lambda: TrieKey("abc", 2)) and not _held(lambda: TrieKey("ab", 2))
    r["suffix_array"] = _held(lambda: SuffixArray((3, 2, 1))) and not _held(lambda: SuffixArray((1, 2, 3)))
    r["bloom_filter"] = _held(lambda: BloomFilter(frozenset({-1}), 1)) and not _held(lambda: BloomFilter(frozenset({0, 1}), 2))
    r["hyperloglog"] = _held(lambda: HyperLogLog((-1, 0))) and not _held(lambda: HyperLogLog((0, 1, 2)))
    r["count_min_sketch"] = _held(lambda: CountMinSketch(((1, -1),))) and not _held(lambda: CountMinSketch(((1, 2),)))
    r["merkle_path"] = _held(lambda: MerkleLeaf("not-hex")) and _held(lambda: MerklePath((), 4)) and not _held(lambda: MerklePath((MerkleLeaf("0" * 64), MerkleLeaf("1" * 64)), 4))
    r["vector_clock"] = _held(lambda: VectorClock((("b", 1), ("a", 0)))) and not _held(lambda: VectorClock((("a", 0), ("b", 1))))
    r["sorted_list"] = _held(lambda: SortedList((3, 1, 2))) and not _held(lambda: SortedList((1, 2, 3)))
    r["traversal_step"] = _held(lambda: TraversalStep(frozenset({"a"}), "a")) and not _held(lambda: TraversalStep(frozenset({"a"}), "b"))
    r["non_negative_weight"] = _held(lambda: NonNegativeWeight(-1.0)) and _held(lambda: NonNegativeWeight(float("inf"))) and not _held(lambda: NonNegativeWeight(0.0))
    r["admissible_heuristic"] = _held(lambda: AdmissibleHeuristic(10.0, 5.0)) and not _held(lambda: AdmissibleHeuristic(5.0, 10.0))
    r["shortest_paths"] = _held(lambda: ShortestPaths((("a", float("nan")),))) and not _held(lambda: ShortestPaths((("a", 1.0),)))
    r["distance_matrix"] = _held(lambda: DistanceMatrix(2, ((0, 1), (1, 1)))) and not _held(lambda: DistanceMatrix(2, ((0, 1), (1, 0))))
    r["flow_network"] = _held(lambda: FlowNetwork("s", "s", ())) and _held(lambda: FlowNetwork("s", "t", (Flow(("s", "a"), 1.0), Flow(("a", "b"), 1.0)))) and not _held(lambda: FlowNetwork("s", "t", ()))
    r["matrix"] = _held(lambda: Matrix(2, 2, ((1, 2), (3,)))) and not _held(lambda: Matrix(2, 2, ((1, 2), (3, 4))))
    r["fft_signal"] = _held(lambda: FFTSignal((1 + 0j, 2 + 0j, 3 + 0j))) and not _held(lambda: FFTSignal((1 + 0j, 2 + 0j)))
    r["kernel"] = _held(lambda: Kernel(())) and not _held(lambda: Kernel((1.0, 2.0)))
    r["assignment"] = _held(lambda: Assignment(((1, True), (1, False)))) and not _held(lambda: Assignment(((1, True), (2, False))))
    r["solved"] = _held(lambda: Solved("", 42)) and not _held(lambda: Solved("dp[0]", 42))
    r["greedy_choice"] = _held(lambda: GreedyChoice("x", False)) and not _held(lambda: GreedyChoice("x", True))
    r["solution"] = _held(lambda: Solution((("x", 1),), (Constraint("c1", False),))) and not _held(lambda: Solution((("x", 1),), (Constraint("c1", True),)))
    r["bound"] = _held(lambda: Bound(10.0, 5.0)) and not _held(lambda: Bound(3.0, 5.0))
    r["ast"] = _held(lambda: AST("", "root")) and _held(lambda: AST("x", None)) and not _held(lambda: AST("x", "root"))
    r["typed"] = _held(lambda: Typed("x", "")) and not _held(lambda: Typed("x", "Int"))
    r["proof"] = _held(lambda: Proof("", "t", True)) and _held(lambda: Proof("T", "t", False)) and not _held(lambda: Proof("T", "t", True))
    r["lock_order"] = _held(lambda: LockOrder(("a", "b", "a"))) and not _held(lambda: LockOrder(("a", "b")))
    r["bounded_pointer"] = _held(lambda: BoundedPointer(-1, 10)) and _held(lambda: BoundedPointer(10, 10)) and not _held(lambda: BoundedPointer(0, 10))
    r["message"] = _held(lambda: Message("", VectorClock(()), None)) and not _held(lambda: Message("n1", VectorClock(()), None))
    r["decided"] = _held(lambda: Decided("v", -1)) and not _held(lambda: Decided("v", 0))
    r["linearizable"] = _held(lambda: Linearizable(((2, "a"), (1, "b")))) and not _held(lambda: Linearizable(((1, "a"), (2, "b"))))
    r["verified"] = _held(lambda: Verified("not-hex", True)) and _held(lambda: Verified("0" * 64, False)) and not _held(lambda: Verified("0" * 64, True))
    r["zk_proof"] = _held(lambda: ZKProof("", True)) and _held(lambda: ZKProof("stmt", False)) and not _held(lambda: ZKProof("stmt", True))
    r["decompressed"] = _held(lambda: Decompressed(b"abc", 5)) and not _held(lambda: Decompressed(b"abc", 3))
    return r


if __name__ == "__main__":
    results = murmuration_holds()
    print("=" * 64)
    print(f"MURMURATION — {len(results)} agents, wrong state unrepresentable")
    print("=" * 64)
    failed = []
    for agent, held in sorted(results.items()):
        status = "ok" if held else "FAIL"
        print(f"  [{status:4}] {agent}")
        if not held:
            failed.append(agent)
    print()
    if failed:
        print(f"[gap] {len(failed)} agent(s) do not refuse their wrong state:")
        for name in failed:
            print(f"  missing: {name}")
        sys.exit(1)
    print(f"[held] all {len(results)} agents refuse their wrong states")
    print("  No job verifies what cannot exist.")
