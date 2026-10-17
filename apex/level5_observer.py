"""Level 5 — observer: the three-state link between system and judge."""
from __future__ import annotations
import hashlib
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal

@dataclass(frozen=True)
class Disposition:
    judgment: Literal["ACCEPTED", "REJECTED", "UNDECIDED"]
    artifact_hash: str
    observer_id: str
    reason: str = ""
    def __post_init__(self):
        if self.judgment not in ("ACCEPTED", "REJECTED", "UNDECIDED"):
            raise ValueError(f"unknown judgment {self.judgment!r}")
        if not self.observer_id:
            raise ValueError("needs observer")
        if self.judgment == "REJECTED" and not self.reason:
            raise ValueError("REJECTED requires reason")
        if self.judgment == "UNDECIDED" and self.reason:
            raise ValueError("UNDECIDED carries no reason")
    def require_accepted(self) -> None:
        if self.judgment == "UNDECIDED":
            raise PermissionError(f"UNDECIDED by {self.observer_id}")
        if self.judgment == "REJECTED":
            raise PermissionError(f"REJECTED: {self.reason}")

def observe(artifact, observer, observer_id, log_path) -> Disposition:
    h = hashlib.sha256(json.dumps(artifact, sort_keys=True).encode()).hexdigest()
    judgment = observer(artifact)
    if judgment not in ("ACCEPTED", "REJECTED", "UNDECIDED"):
        raise ValueError(f"observer returned {judgment!r}")
    disp = Disposition(judgment, h, observer_id,
                       reason="" if judgment != "REJECTED" else "rejected by observer")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a") as f:
        f.write(json.dumps({"judgment": disp.judgment,
                            "artifact_hash": disp.artifact_hash,
                            "observer_id": disp.observer_id}) + "\n")
    return disp

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        log = td / "log.jsonl"

        # UNDECIDED blocks
        d = observe({"x": 1}, lambda a: "UNDECIDED", "obs-1", log)
        try:
            d.require_accepted()
            print("[level 5] UNDECIDED: FAIL")
            sys.exit(1)
        except PermissionError:
            print("  [ok] UNDECIDED blocks")

        # REJECTED blocks
        d = observe({"x": 1}, lambda a: "REJECTED", "obs-1", log)
        try:
            d.require_accepted()
            print("[level 5] REJECTED: FAIL")
            sys.exit(1)
        except PermissionError:
            print("  [ok] REJECTED blocks")

        # ACCEPTED passes
        d = observe({"x": 1}, lambda a: "ACCEPTED", "obs-1", log)
        d.require_accepted()
        print("  [ok] ACCEPTED passes")

        # log has 3 entries
        entries = log.read_text().strip().split("\n")
        print(f"  [ok] log has {len(entries)} entries")
    print("[level 5] observer: ok")
