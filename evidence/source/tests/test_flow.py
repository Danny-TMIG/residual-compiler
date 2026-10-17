from src import flow


def test_pass():
    assert flow.flow([1, 2], [lambda x: x]) == [1, 2]


def test_chain():
    assert flow.flow([1, 2], [lambda x: x + 1, lambda x: x * 2]) == [4, 6]
