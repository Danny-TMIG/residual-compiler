from src import flow, contracts


def test_flow_steps_present(atlas_db):
    steps = flow.flow_steps()
    assert len(steps) == 31
    assert steps[0] == "Interpret"
    assert steps[-1] == "Learn"


def test_flow_role_for_known():
    assert flow.role_for("Interpret") == "Intent Listener"
    assert flow.role_for("Learn") == "Knowledge Curator"


def test_flow_role_for_unknown():
    assert flow.role_for("NotAStage") is None
