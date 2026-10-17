import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "aether" / "research" / "train"))
from pipelines import corpus_pipeline as cp


def test_cc_by_sa_3_0_allowed():
    assert "CC-BY-SA-3.0" in cp.PERMISSIVE


def test_dolly_doc_accepted():
    out = cp.step_license_audit({"documents": [{"license": "CC-BY-SA-3.0", "text": "hello"}]})
    assert out["accepted_count"] == 1
    assert out["rejected_count"] == 0
