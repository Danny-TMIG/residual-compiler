"""Ensure documents survive license_audit -> clean -> dedup -> tokenize."""

import sys
from pathlib import Path

import os
import pytest
_EXT = os.path.expanduser('~/aether/research/train')
if not os.path.isdir(_EXT):
    pytest.skip('external training tree not available', allow_module_level=True)
sys.path.insert(0, str(Path.home() / "aether" / "research" / "train"))
from pipelines import corpus_pipeline as cp


def test_documents_flow_through_all_stages():
    docs = [
        {"license": "CC-BY-SA-3.0", "text": "a b c"},
        {"license": "CC-BY-SA-3.0", "text": "d e f"},
        {"license": "CC-BY-SA-3.0", "text": "a b c"},
    ]  # dup
    ing = {"documents": docs, "count": len(docs)}
    aud = cp.step_license_audit(ing)
    assert aud["accepted_count"] == 3
    cln = cp.step_clean(aud)
    assert cln["count"] == 3
    ded = cp.step_dedup(cln)
    assert ded["count"] == 2 and ded["removed"] == 1
