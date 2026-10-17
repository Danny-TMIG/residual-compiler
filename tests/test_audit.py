import os, tempfile
from pathlib import Path
from src import audit


def test_chain_empty_ok(tmp_path, monkeypatch):
    p = tmp_path / "ev.log"
    monkeypatch.setattr(audit, "LOG", p)
    assert audit.verify_chain(p) == {"ok": True, "records": 0}


def test_chain_append_and_verify(tmp_path, monkeypatch):
    p = tmp_path / "ev.log"
    monkeypatch.setattr(audit, "LOG", p)
    monkeypatch.setattr(
        audit,
        "_last_hash",
        lambda: audit._last_hash_from(p) if hasattr(audit, "_last_hash_from") else audit.GENESIS,
    )
    # append manually without relying on module state
    a = {"ts": 1.0, "kind": "test", "payload": {"x": 1}, "prev": audit.GENESIS}
    a["hash"] = audit._hash(a)
    p.write_text(audit._canon(a) + "\n")
    r = audit.verify_chain(p)
    assert r["ok"] is True
    assert r["records"] == 1


def test_chain_tamper_detected(tmp_path):
    p = tmp_path / "ev.log"
    a = {"ts": 1.0, "kind": "test", "payload": {"x": 1}, "prev": audit.GENESIS}
    a["hash"] = audit._hash(a)
    p.write_text(audit._canon(a) + "\n")
    # tamper payload
    p.write_text(p.read_text().replace('"x":1', '"x":2'))
    r = audit.verify_chain(p)
    assert r["ok"] is False
    assert "hash mismatch" in r["reason"]
