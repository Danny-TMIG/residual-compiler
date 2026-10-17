"""Input-size limits. Asserts clean rejection, not crashes."""

import pytest
from src import compile_cli


MAX_QUERY_BYTES = 64 * 1024


def _run(argv):
    """Invoke compile_cli.main with an argv list (the real signature)."""
    return compile_cli.main(argv)


def test_oversized_query_rejected():
    huge = "prove " + ("terminates " * (MAX_QUERY_BYTES // 8))
    assert len(huge) > MAX_QUERY_BYTES
    with pytest.raises((ValueError, SystemExit, RuntimeError)):
        _run([huge])


def test_empty_query_rejected():
    with pytest.raises((ValueError, SystemExit, RuntimeError)):
        _run([""])


def test_normal_query_accepted():
    # Should not raise; return value may be None.
    _run(["search for TODOs in src/tools.py"])


def test_max_size_boundary():
    """A query just under the limit must not fail for size reasons."""
    near = "x" * (MAX_QUERY_BYTES - 1)
    try:
        _run([near])
    except SystemExit as e:
        # exit code 2 = argparse error; 0/1 = app-level, still acceptable
        if e.code == 2:
            pytest.fail("argparse rejected near-limit query")
    except (ValueError, RuntimeError) as e:
        assert "too large" not in str(e).lower()
