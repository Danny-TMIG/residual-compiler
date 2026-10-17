import tempfile
from pathlib import Path
from src import bundle


def test_seal_and_verify(tmp_path, monkeypatch):
    monkeypatch.setattr(bundle, "DIR", tmp_path)
    r = bundle.seal(kind="test", config={"a": 1}, trace=[{"s": 1}], evidence_records=[])
    assert bundle.verify(r["path"]) is True


def test_verify_detects_tamper(tmp_path, monkeypatch):
    monkeypatch.setattr(bundle, "DIR", tmp_path)
    r = bundle.seal(kind="test", config={"a": 1}, trace=[], evidence_records=[])
    p = Path(r["path"])
    # bundle.seal uses indent=2, so the serialized form has spaces
    p.write_text(p.read_text().replace('"a": 1', '"a": 2'))
    assert bundle.verify(str(p)) is False
