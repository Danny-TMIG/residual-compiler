from src import dispatch, tools
from src.contracts import ResultState


def test_dispatch_unbound_returns_not_run():
    r = dispatch.dispatch("definitely-not-a-real-skill-xyz", {})
    assert r["result_state"] == ResultState.NOT_RUN.value


def test_dispatch_missing_inputs_returns_insufficient_data(skills_db):
    r = dispatch.dispatch("evidence-hash", {})
    assert r["result_state"] == ResultState.INSUFFICIENT_DATA.value


def test_dispatch_bound_runs(skills_db, tmp_path):
    p = tmp_path / "f.txt"
    p.write_text("hello")
    r = dispatch.dispatch("evidence-hash", {"path": str(p)})
    assert r["result_state"] == ResultState.PASS.value
    assert "digest" in r
