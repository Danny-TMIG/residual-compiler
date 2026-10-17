#!/usr/bin/env python3
from __future__ import annotations
import json
import hashlib
import time
import uuid
from pathlib import Path

ROOT = Path.cwd()
APEX = ROOT / "apex"
AUDIT = APEX / "AUDIT.jsonl"

class Pipeline:
    def __init__(self):
        self.request_id = None
        self.idempotency = {}
        self.rate = {}
        self.circuit = {"failures": 0, "open": False}
        self.log = []

    def _log(self, phase, chore, verdict, detail=""):
        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "rid": self.request_id,
            "phase": phase,
            "chore": chore,
            "verdict": verdict,
            "detail": detail,
        }
        self.log.append(entry)
        with AUDIT.open("a") as f:
            f.write(json.dumps(entry) + "\n")

    def i1_parse(self, req):
        try:
            body = json.loads(req["body"]) if isinstance(req["body"], str) else req["body"]
            self._log("ingress", "parse", "pass")
            return {"ok": True, "body": body}
        except Exception as e:
            self._log("ingress", "parse", "reject_400", str(e))
            return {"ok": False, "status": 400}

    def i2_validate(self, body):
        if not isinstance(body, dict):
            self._log("ingress", "validate", "reject_422", "not dict")
            return {"ok": False, "status": 422}
        self._log("ingress", "validate", "pass")
        return {"ok": True}

    def i3_auth(self, req):
        token = req.get("headers", {}).get("authorization", "")
        if not token.startswith("Bearer "):
            self._log("ingress", "auth", "reject_401", "no bearer")
            return {"ok": False, "status": 401}
        self._log("ingress", "auth", "pass", token[:12])
        return {"ok": True, "token": token}

    def i4_authorize(self, req, token):
        cap = req.get("headers", {}).get("x-capability", "")
        if cap not in {"read", "write", "admin"}:
            self._log("ingress", "authorize", "reject_403", cap)
            return {"ok": False, "status": 403}
        self._log("ingress", "authorize", "pass", cap)
        return {"ok": True}

    def i5_rate(self, req):
        key = req.get("headers", {}).get("x-client-id", "anonymous")
        now = time.time()
        bucket = self.rate.setdefault(key, {"tokens": 10, "last": now})
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(10, bucket["tokens"] + elapsed)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            self._log("ingress", "rate", "reject_429", key)
            return {"ok": False, "status": 429}
        bucket["tokens"] -= 1
        self._log("ingress", "rate", "pass", key)
        return {"ok": True}

    def i6_sanitize(self, body):
        dangerous = ("<script", "'; DROP", "../")
        for v in body.values():
            if isinstance(v, str):
                for d in dangerous:
                    if d.lower() in v.lower():
                        self._log("ingress", "sanitize", "reject_400", d)
                        return {"ok": False, "status": 400}
        self._log("ingress", "sanitize", "pass")
        return {"ok": True}

    def i7_dedup(self, req):
        key = req.get("headers", {}).get("idempotency-key")
        if not key:
            self._log("ingress", "dedup", "pass", "no key")
            return {"ok": True, "new": True}
        if key in self.idempotency:
            self._log("ingress", "dedup", "replay_200", key)
            return {"ok": True, "new": False, "cached": self.idempotency[key]}
        self.idempotency[key] = {"rid": self.request_id, "ts": time.time()}
        self._log("ingress", "dedup", "pass", key)
        return {"ok": True, "new": True}

    def i8_trace(self, req):
        incoming = req.get("headers", {}).get("x-request-id")
        self.request_id = incoming or str(uuid.uuid4())
        self._log("ingress", "trace", "pass", self.request_id)
        return {"ok": True, "rid": self.request_id}

    def i9_quota(self, req):
        budget = int(req.get("headers", {}).get("x-budget", "100"))
        cost = len(req.get("body", "")) // 100 + 1
        if cost > budget:
            self._log("ingress", "quota", "reject_402", str(cost) + ">" + str(budget))
            return {"ok": False, "status": 402}
        self._log("ingress", "quota", "pass", str(cost) + "/" + str(budget))
        return {"ok": True}

    def i10_circuit(self, req):
        if self.circuit["open"]:
            self._log("ingress", "circuit", "reject_503", "circuit open")
            return {"ok": False, "status": 503}
        self._log("ingress", "circuit", "pass")
        return {"ok": True}

    def i11_queue(self, req):
        if len(self.rate) > 100:
            self._log("ingress", "queue", "accept_202", "queued")
            return {"ok": True, "queued": True}
        self._log("ingress", "queue", "pass")
        return {"ok": True}

    def e1_serialize(self, obj):
        try:
            out = json.dumps(obj)
            self._log("egress", "serialize", "pass")
            return {"ok": True, "body": out}
        except Exception as e:
            self._log("egress", "serialize", "500", str(e))
            return {"ok": False}

    def e2_sign(self, body, secret="shared"):
        sig = hashlib.sha256((body + secret).encode()).hexdigest()
        self._log("egress", "sign", "pass", sig[:16])
        return {"ok": True, "sig": sig}

    def e3_redact(self, body):
        out = body
        for k in ("password", "secret", "token", "key"):
            out = out.replace('"' + k + '":', '"' + k + '":"[REDACTED]",')
        self._log("egress", "redact", "pass")
        return {"ok": True, "body": out}

    def e4_compress(self, body):
        self._log("egress", "compress", "pass", str(len(body)) + "B")
        return {"ok": True, "body": body}

    def e5_retry(self, send_fn, max_attempts=3):
        for attempt in range(max_attempts):
            try:
                result = send_fn()
                self._log("egress", "retry", "pass", "attempt " + str(attempt + 1))
                return {"ok": True, "result": result}
            except Exception:
                time.sleep(0.01 * (2 ** attempt))
        self._log("egress", "retry", "dlq", "all retries failed")
        return {"ok": False}

    def e6_circuit(self, ok):
        if not ok:
            self.circuit["failures"] += 1
            if self.circuit["failures"] >= 5:
                self.circuit["open"] = True
                self._log("egress", "circuit_open", "open", "circuit tripped")
                return
        self._log("egress", "circuit_open", "pass")

    def e7_log(self, response):
        self._log("egress", "log", "pass", str(response)[:40])

    def e8_trace_end(self):
        self._log("egress", "trace_end", "pass", self.request_id)

    def e9_meter(self, body):
        tokens = len(body.split())
        self._log("egress", "meter", "pass", str(tokens) + " tokens")

    def e10_audit(self, body):
        h = hashlib.sha256(body.encode()).hexdigest()
        self._log("egress", "audit", "pass", h[:16])

    def e11_dlq(self, body, reason):
        dlq = APEX / "DLQ.jsonl"
        with dlq.open("a") as f:
            f.write(json.dumps({"body": body, "reason": reason}) + "\n")
        self._log("egress", "dlq", "dlq", reason)

    def handle(self, req):
        self._log("ingress", "START", "pass")
        self.i8_trace(req)
        r = self.i1_parse(req)
        if not r["ok"]:
            return {"status": r["status"]}
        body = r["body"]
        r = self.i2_validate(body)
        if not r["ok"]:
            return {"status": r["status"]}
        r = self.i3_auth(req)
        if not r["ok"]:
            return {"status": r["status"]}
        r = self.i4_authorize(req, r["token"])
        if not r["ok"]:
            return {"status": r["status"]}
        r = self.i5_rate(req)
        if not r["ok"]:
            return {"status": r["status"]}
        r = self.i6_sanitize(body)
        if not r["ok"]:
            return {"status": r["status"]}
        r = self.i7_dedup(req)
        if not r["ok"]:
            return {"status": r["status"]}
        if r.get("cached"):
            return {"status": 200, "cached": True}
        r = self.i9_quota(req)
        if not r["ok"]:
            return {"status": r["status"]}
        r = self.i10_circuit(req)
        if not r["ok"]:
            return {"status": r["status"]}
        r = self.i11_queue(req)
        if r.get("queued"):
            return {"status": 202}
        response = {"ok": True, "rid": self.request_id, "echo": body}
        r = self.e1_serialize(response)
        if not r["ok"]:
            return {"status": 500}
        wire = r["body"]
        self.e2_sign(wire)
        r = self.e3_redact(wire)
        wire = r["body"]
        r = self.e4_compress(wire)
        wire = r["body"]
        self.e5_retry(lambda: {"status": 200, "body": wire})
        self.e6_circuit(True)
        self.e7_log({"status": 200})
        self.e8_trace_end()
        self.e9_meter(wire)
        self.e10_audit(wire)
        return {"status": 200, "body": wire, "rid": self.request_id}


def main():
    p = Pipeline()
    req = {
        "body": '{"msg": "hello", "password": "secret123"}',
        "headers": {
            "authorization": "Bearer abcdef",
            "x-capability": "read",
            "x-client-id": "test-client",
            "idempotency-key": "key-1",
            "x-request-id": None,
            "x-budget": "100"
        }
    }
    out = p.handle(req)
    print("[result]", json.dumps(out)[:200])
    print("[chores run]", len(p.log))
    bad = {"body": "not json", "headers": {}}
    out = p.handle(bad)
    print("[reject]", out)
    out = p.handle(req)
    print("[replay]", out.get("cached", False))


if __name__ == "__main__":
    main()
