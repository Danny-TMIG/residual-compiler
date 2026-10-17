from dataclasses import dataclass
from enum import Enum


class ResultState(str, Enum):
    OK = "OK"
    ERROR = "ERROR"
    PENDING = "PENDING"


@dataclass(frozen=True)
class SkillContract:
    name: str
    version: int

    def validate(self) -> bool:
        return bool(self.name) and self.version >= 1


def normalize_result(state):
    if isinstance(state, ResultState):
        return state
    return ResultState(str(state).upper())


def validate_contract(c) -> bool:
    return isinstance(c, SkillContract) and c.validate()
