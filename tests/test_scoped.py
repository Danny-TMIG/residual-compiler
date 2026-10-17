from src import scoped, tools, bind_all


def test_def():
    assert scoped.scoped([1, 2]) == {"s:1": 1, "s:2": 2}


def test_custom():
    assert scoped.scoped([1], prefix="p:") == {"p:1": 1}


def test_bind():
    assert bind_all.bind_all([{"id": "a"}], {"ident": tools.ident}) == {
        "a": {"ident": {"id": "a"}}
    }
