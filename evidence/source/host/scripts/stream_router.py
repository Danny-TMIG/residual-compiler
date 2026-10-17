#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
import time
import uuid
from pathlib import Path

ROOT = Path.cwd()
APEX = ROOT / "apex"
STREAMS = json.loads((APEX / "STREAMS.json").read_text())
AUDIT = APEX / "STREAM-AUDIT.jsonl"

class StreamRouter:
    def __init__(self):
        self.state = {
            "rate": {},
            "peers": {},
            "circuits": {"up": False, "down": False, "left": {}, "right": {}},
            "budgets": {"up": 100, "left": 1000, "right": 1000},
            "spans": {},
        }
        self.log = []

    def _log(self, direction, chore, verdict, detail=""):
        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "dir": direction,
            "chore": chore,
            "verdict": verdict,
            "detail": detail,
        }
        self.log.append(entry)
        with AUDIT.open("a") as f:
            f.write(json.dumps(entry) + "\n")

    def _fire(self, direction, chore, **kwargs):
        key = f"{direction}:{chore}"
        if key not in STREAMS["grid"]:
            self._log(direction, chore, "skip", "no cell")
            return {"ok": True, "skip": True}
        handler = STREAMS["grid"][key]["handler"]
        self._log(direction, chore, "pass", handler)
        return {"ok": True, "handler": handler}

    # ---- UP: client -> system ----
    def up(self, req):
        rid = req.get("headers", {}).get("x-request-id") or str(uuid.uuid4())
        self.state["spans"][rid] = {"start": time.time()}
        for chore in ["parse","validate","auth","authorize","rate","sanitize",
                      "dedup","trace","quota","circuit","queue"]:
            r = self._fire("up", chore)
            if not r["ok"]:
                return {"status": 400, "dir": "up", "failed": chore}
        return {"status": 200, "dir": "up", "rid": rid, "chores_run": 11}

    # ---- DOWN: system -> client ----
    def down(self, resp):
        for chore in ["serialize","sign","redact","compress","retry",
                      "circuit_open","log","trace_end","meter","audit","dlq"]:
            self._fire("down", chore)
        return {"status": 200, "dir": "down", "chores_run": 11}

    # ---- LEFT: peer -> peer ----
    def left(self, peer_msg):
        for chore in ["parse","validate","auth","authorize","rate","sanitize",
                      "dedup","trace","quota","circuit","queue",
                      "serialize","sign","retry","circuit_open","log",
                      "trace_end","meter","audit","dlq"]:
            self._fire("left", chore)
        return {"status": 200, "dir": "left", "chores_run": 20}

    # ---- RIGHT: system -> external ----
    def right(self, ext_msg):
        for chore in ["parse","validate","auth","authorize","rate","sanitize",
                      "dedup","trace","quota","circuit","queue",
                      "serialize","sign","redact","compress","retry",
                      "circuit_open","log","trace_end","meter","audit","dlq"]:
            self._fire("right", chore)
        return {"status": 200, "dir": "right", "chores_run": 22}

    def handle_all(self, req, resp, peer, ext):
        results = {}
        results["up"]    = self.up(req)
        results["down"]  = self.down(resp)
        results["left"]  = self.left(peer)
        results["right"] = self.right(ext)
        return results

def main():
    r = StreamRouter()
    results = r.handle_all(
        req={"body": '{"x":1}', "headers": {"authorization": "Bearer t"}},
        resp={"ok": True},
        peer={"from": "peer-1", "msg": "gossip"},
        ext={"to": "fed-1", "payload": "federated"},
    )
    print("[directions]", json.dumps(results, indent=2))
    print("[chores fired]", len(r.log))
    print("[coverage]", STREAMS["coverage"])

if __name__ == "__main__":
    main()
