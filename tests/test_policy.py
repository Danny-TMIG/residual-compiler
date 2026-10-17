from src.policy import _match, evaluate


def test_exact():
    assert _match("a", "a") is True


def test_star():
    assert _match("*", "any") is True


def test_miss():
    assert _match("a", "b") is False


def test_eval():
    assert [
        i["id"] for i in evaluate([{"id": "a"}, {"id": "b"}, {"id": "c"}], ["a", "c"])
    ] == ["a", "c"]
