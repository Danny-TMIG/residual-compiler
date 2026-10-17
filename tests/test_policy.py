from src.policy import evaluate, _match


def test_match_conjunction():
    assert _match(
        {"operation": "search", "target_env": "dev"},
        {"operation": "search", "target_env": "dev", "x": 1},
    )


def test_match_list():
    assert _match({"operation": ["search", "find"]}, {"operation": "search"})
    assert not _match({"operation": ["search", "find"]}, {"operation": "deploy"})


def test_match_regex():
    assert _match({"path": "re:\\.py$"}, {"path": "src/x.py"})
    assert not _match({"path": "re:\\.py$"}, {"path": "src/x.go"})


def test_evaluate_first_deny_wins():
    policy = {
        "rules": [
            {"id": "allow-all", "when": {}, "then": "ALLOW"},
            {"id": "deny-prod", "when": {"target_env": "prod"}, "then": "DENY", "reason": "no"},
        ],
        "default": "DENY",
    }
    r = evaluate({"target_env": "prod"}, policy=policy)
    assert r["decision"] == "DENY"


def test_evaluate_escalate_missing():
    policy = {
        "rules": [
            {"id": "ex", "when": {}, "then": "ESCALATE", "requires": ["change_approved"]},
        ],
        "default": "DENY",
    }
    r = evaluate({}, authorities=[], policy=policy)
    assert r["decision"] == "ESCALATE"
    r = evaluate({}, authorities=["change_approved"], policy=policy)
    assert r["decision"] == "ALLOW"


def test_evaluate_default_deny():
    assert evaluate({}, policy={"rules": [], "default": "DENY"})["decision"] == "DENY"
