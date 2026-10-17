import json

from src.cli import _seed


def test_schema():
    s = _seed()
    assert s["schema"] == 1 and isinstance(s["items"], list) and len(s["items"]) == 3


def test_ser():
    json.dumps(_seed())
