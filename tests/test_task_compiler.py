from src.task_compiler import compile_task


def test_classify_search():
    r = compile_task("search for TODOs in src/tools.py", policy_path=None)
    assert r["intent"]["operation"] == "search"


def test_classify_execute():
    r = compile_task("audit src for quality", policy_path=None)
    assert r["intent"]["operation"] == "execute"


def test_classify_deploy():
    r = compile_task("deploy to prod", policy_path=None)
    assert r["intent"]["operation"] == "deploy"


def test_classify_deploy_before_execute():
    # deploy regex must match before execute, or the DENY rule won't fire
    r = compile_task("deploy to prod", policy_path=None)
    assert r["intent"]["operation"] == "deploy", "deploy must beat execute"


def test_path_extraction():
    r = compile_task("audit src/tools.py", policy_path=None)
    assert r["default"]["path"] == "src/tools.py"
    assert r["default"]["root"] == "src"
