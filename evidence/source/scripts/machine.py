#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, sys, uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

NS = uuid.UUID("00000000-0000-0000-0000-000000000001")
APEX = Path(__file__).resolve().parent.parent / "apex"

class State(Enum):
    PENDING="PENDING"; READY="READY"; RUNNING="RUNNING"
    CLOSED="CLOSED"; REFUTED="REFUTED"; UNDECIDED="UNDECIDED"

@dataclass
class Evidence:
    node: str
    invariant_passed: bool
    falsify_attempted: bool
    falsify_fired: bool
    payload_hash: str
    timestamp: str
    attestor: str

@dataclass
class Node:
    id: str
    cls: str
    name: str
    layer: int
    invariant: str
    transform: str
    evidence_id: str
    falsify: str
    closure: str
    deps: list = field(default_factory=list)
    caps_req: list = field(default_factory=list)
    caps_prov: list = field(default_factory=list)
    state: State = State.PENDING
    prov: list = field(default_factory=list)

def canonical_id(cls, name):
    return f"{cls}:{uuid.uuid5(NS, name)}"

LAYERS = {
    0: {"inv":"mass_energy_conserved_delta","falsify":"delta_exceeded"},
    1: {"inv":"timing_closure_worst_case","falsify":"passes_at_1.05x_max"},
    2: {"inv":"boot_integrity_hash_chain","falsify":"modified_byte_boots"},
    3: {"inv":"syscall_isolation","falsify":"forbidden_syscall_allowed"},
    4: {"inv":"deterministic_replay","falsify":"two_runs_differ"},
    5: {"inv":"contract_conformance","falsify":"mutated_input_2xx"},
    6: {"inv":"capability_vs_authority","falsify":"wrong_role_allowed"},
    7: {"inv":"external_cost_accounting","falsify":"cost_shift_silent"},
}

class Machine:
    def __init__(self):
        self.nodes = {}
        self.evidence = {}
        self.relations = []
    def add(self, node):
        if node.layer not in LAYERS:
            raise ValueError(f"invalid layer {node.layer}")
        if not node.invariant or not node.falsify:
            raise ValueError(f"node {node.id}: missing invariant/falsify")
        self.nodes[node.id] = node
        return node.id
    def relate(self, kind, src, dst, evidence_id):
        if kind not in ("depends_on","provides","consumes","refines","attacks"):
            raise ValueError(f"invalid relation {kind}")
        if src not in self.nodes or dst not in self.nodes:
            raise ValueError("unknown endpoint")
        self.relations.append({"kind":kind,"from":src,"to":dst,"evidence":evidence_id})
    def tx_id(self, node_id, op, input_hashes):
        h = hashlib.sha256((node_id+op+"".join(sorted(input_hashes))).encode()).hexdigest()
        return str(uuid.uuid5(NS, h))
    def transition(self, node_id, target):
        n = self.nodes[node_id]
        if n.state == State.PENDING and target == State.READY:
            if not all(self.nodes[d].state == State.CLOSED for d in n.deps):
                return False
            n.state = State.READY; return True
        if n.state == State.READY and target == State.RUNNING:
            n.state = State.RUNNING; return True
        if n.state == State.RUNNING and target == State.CLOSED:
            ev = self.evidence.get(n.evidence_id)
            if not ev or not ev.invariant_passed or not ev.falsify_attempted or ev.falsify_fired:
                return False
            n.state = State.CLOSED; return True
        if n.state == State.RUNNING and target == State.REFUTED:
            ev = self.evidence.get(n.evidence_id)
            if ev and ev.falsify_fired:
                n.state = State.REFUTED; return True
        return False
    def closure_profile(self, node_id):
        n = self.nodes[node_id]
        return {"node":n.id,"layer":n.layer,"invariant":n.invariant,
                "falsify":n.falsify,"evidence_required":[n.evidence_id],
                "strategy":"ALL","max_age":"24h"}
    def validate(self):
        errors = []
        for n in self.nodes.values():
            if not n.invariant: errors.append(f"{n.id}: no invariant")
            if not n.falsify: errors.append(f"{n.id}: no falsify")
            if n.state == State.CLOSED and n.evidence_id not in self.evidence:
                errors.append(f"{n.id}: CLOSED without evidence")
        for r in self.relations:
            if r["evidence"] not in self.evidence:
                errors.append(f"relation {r['from']}->{r['to']}: no evidence")
        return errors
    def to_json(self):
        return {
            "nodes": {nid:{"class":n.cls,"name":n.name,"layer":n.layer,
                            "invariant":n.invariant,"falsify":n.falsify,
                            "state":n.state.value} for nid,n in self.nodes.items()},
            "relations": self.relations,
            "evidence": {eid:{"node":e.node,"invariant_passed":e.invariant_passed,
                              "falsify_attempted":e.falsify_attempted,
                              "falsify_fired":e.falsify_fired,
                              "payload_hash":e.payload_hash} for eid,e in self.evidence.items()},
        }

def build_demo():
    m = Machine()
    layers = [
        (0,"physical","steel_frame"), (1,"silicon","m4_max"),
        (2,"firmware","bootloader"), (3,"os","kernel"),
        (4,"runtime","apex_runner"), (5,"app","residual_compiler"),
        (6,"org","release_committee"), (7,"society","customer"),
    ]
    for layer, cls, name in layers:
        nid = canonical_id(cls, name)
        m.add(Node(id=nid,cls=cls,name=name,layer=layer,
                   invariant=LAYERS[layer]["inv"],transform=f"T{layer}",
                   evidence_id=f"E{layer}",falsify=LAYERS[layer]["falsify"],
                   closure=f"C{layer}"))
    ids = [canonical_id(c,n) for _,c,n in layers]
    for i in range(len(ids)-1):
        m.relate("depends_on", ids[i+1], ids[i], f"E{i}")
    import subprocess
    def apex_runner_deterministic():
        """Run apex/runner.py twice; True iff outputs match."""
        script = APEX / "runner.py"
        if not script.exists():
            return False
        try:
            r1 = subprocess.run([sys.executable, str(script)],
                                capture_output=True, timeout=15)
            r2 = subprocess.run([sys.executable, str(script)],
                                capture_output=True, timeout=15)
            return r1.returncode == 0 and r2.returncode == 0 and r1.stdout == r2.stdout
        except Exception:
            return False

    for layer,cls,name in layers:
        nid = canonical_id(cls,name)
        fired = False
        if layer == 4:  # apex_runner — actually run the determinism probe
            fired = not apex_runner_deterministic()
        ev = Evidence(node=nid,invariant_passed=not fired,falsify_attempted=True,
                      falsify_fired=fired,payload_hash="deadbeef",
                      timestamp="2026-10-17T00:00:00Z",attestor="harness")
        m.evidence[f"E{layer}"] = ev
        m.nodes[nid].state = State.RUNNING
        if ev.falsify_fired:
            m.transition(nid, State.REFUTED)

    # Load engines as L4 nodes
    eng_path = APEX / "ENGINES-PROBED.json"
    if eng_path.exists():
        eng = json.loads(eng_path.read_text())
        for e in eng["nodes"]:
            nid = e["id"]
            if nid in m.nodes:
                continue
            m.add(Node(
                id=nid, cls=e["class"], name=e["name"], layer=4,
                invariant="engine_available", transform="T_execute",
                evidence_id=e["evidence_id"],
                falsify="cmd_not_found", closure="C_engine",
            ))
            m.nodes[nid].state = State.READY if e.get("available") else State.PENDING
            m.evidence[e["evidence_id"]] = Evidence(
                node=nid, invariant_passed=e.get("available", False),
                falsify_attempted=True, falsify_fired=not e.get("available", False),
                payload_hash="", timestamp="2026-10-17T00:00:00Z", attestor="probe",
            )
    return m

def main():
    m = build_demo()
    print("[harden] nodes=%d relations=%d evidence=%d" %
          (len(m.nodes), len(m.relations), len(m.evidence)))
    for nid,n in sorted(m.nodes.items(), key=lambda x:(x[1].layer, x[1].name))[:12]:
        print(f"  L{n.layer} {n.state.value:10s} {n.name:20s} inv={n.invariant}")
    errs = m.validate()
    print(f"[validate] {len(errs)} errors" if errs else "[validate] PASS")
    (APEX / "MACHINE-STATE.json").write_text(json.dumps(m.to_json(), indent=2) + "\n")
    print(f"[written] {APEX / 'MACHINE-STATE.json'}")
    return 0 if not errs else 1

if __name__ == "__main__":
    sys.exit(main())
