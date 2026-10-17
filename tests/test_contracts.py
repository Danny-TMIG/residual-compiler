from src.contracts import SkillContract, ResultState, normalize_result, validate_contract


def test_normalize_result_identity():
    assert normalize_result("PASS") == ResultState.PASS
    assert normalize_result(ResultState.FAIL) == ResultState.FAIL


def test_normalize_result_from_dict():
    assert normalize_result({"result_state": "TIMEOUT"}) == ResultState.TIMEOUT


def test_normalize_result_fallback():
    assert normalize_result("not-a-state") == ResultState.FAIL


def test_validate_contract_ok():
    c = SkillContract(identifier="x", impl="x")
    assert validate_contract(c) == []


def test_validate_contract_missing_identifier():
    c = SkillContract(identifier="", impl="x")
    assert any("identifier" in e for e in validate_contract(c))
