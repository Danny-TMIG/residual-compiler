import os
import sys
from pathlib import Path

import pytest

_EXT = os.path.expanduser("~/aether/research/train")
if not os.path.isdir(_EXT):
    pytest.skip("external training tree not available", allow_module_level=True)
sys.path.insert(0, str(Path.home() / "aether" / "research" / "train"))


def _load_cp():
    """Lazy import — sidesteps E402 and RUF100."""
    from pipelines import corpus_pipeline as cp

    return cp


cp = _load_cp()


def test_cc_by_sa_3_0_allowed():
    assert "CC-BY-SA-3.0" in cp.PERMISSIVE


def test_dolly_doc_accepted():
    out = cp.step_license_audit(
        {"documents": [{"license": "CC-BY-SA-3.0", "text": "hello"}]}
    )
    assert out["accepted_count"] == 1
    assert out["rejected_count"] == 0
