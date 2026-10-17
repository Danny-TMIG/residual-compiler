from src.contracts import (
    SkillContract,
    ResultState,
    normalize_result,
    validate_contract,
)


def test_norm_ok():
    assert normalize_result("ok") is ResultState.OK


def test_norm_case():
    assert normalize_result("error") is ResultState.ERROR


def test_valid():
    assert validate_contract(SkillContract(name="c", version=1)) is True


def test_invalid():
    assert validate_contract({"name": "c"}) is False
