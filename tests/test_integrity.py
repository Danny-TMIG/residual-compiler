from src.cli import _bytes, _sha


def test_det():
    assert _bytes() == _bytes()


def test_hash():
    assert _sha(_bytes()) == _sha(_bytes())
