from src import dispatch, tools


def test_ident():
    assert dispatch.dispatch([1, 2, 3], tools.ident) == [1, 2, 3]


def test_upper():
    assert dispatch.dispatch(["a", "b"], tools.upper) == ["A", "B"]
