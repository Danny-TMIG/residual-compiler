from src import scoped, tools, bind_all


def test_write_scope(tmp_path, monkeypatch):
    monkeypatch.setattr(scoped, "SCOPE_PATH", tmp_path / "scope.json")
    bind_all.register_all(tools_mod=tools)
    bound = scoped.write_scope(tools.REG)
    assert len(bound) == len(tools.REG)
    assert scoped.load_scope() == set(tools.REG.keys())
