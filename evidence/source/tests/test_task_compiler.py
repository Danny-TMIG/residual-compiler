import pytest
from src.task_compiler import compile_task


def test_basic():
    r = compile_task({"id": "t1", "residuals": ["r1"]})
    assert r["id"] == "t1" and r["compiled"] is True and r["residuals"] == ["r1"]


def test_default():
    assert compile_task({})["id"] == "anonymous"


def test_reject():
    with pytest.raises(TypeError):
        compile_task("x")
