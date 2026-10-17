from src import audit


def test_clean():
    assert audit.audit([{"id": "a"}, {"id": "b"}]) == []


def test_dup():
    assert any(
        p["issue"] == "duplicate id" for p in audit.audit([{"id": "a"}, {"id": "a"}])
    )


def test_missing():
    assert any(p["issue"] == "missing id" for p in audit.audit([{}]))
