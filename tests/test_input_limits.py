from src import compile_cli


def test_importable():
    assert hasattr(compile_cli, "main")
