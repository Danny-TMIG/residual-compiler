from dataclasses import dataclass, field, asdict
from enum import Enum


class ResultState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"
    NOT_RUN = "NOT_RUN"
    BLOCKED = "BLOCKED"
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    UNSUPPORTED = "UNSUPPORTED"
    INCOMPATIBLE = "INCOMPATIBLE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"
    RESOURCE_EXHAUSTED = "RESOURCE_EXHAUSTED"
    POLICY_DENIED = "POLICY_DENIED"
    SECURITY_DENIED = "SECURITY_DENIED"
    QUALIFICATION_DENIED = "QUALIFICATION_DENIED"
    DEPENDENCY_FAILURE = "DEPENDENCY_FAILURE"
    ENVIRONMENT_FAILURE = "ENVIRONMENT_FAILURE"
    TOOL_FAILURE = "TOOL_FAILURE"
    MODEL_FAILURE = "MODEL_FAILURE"
    EXECUTION_FAILURE = "EXECUTION_FAILURE"
    VERIFICATION_FAILURE = "VERIFICATION_FAILURE"
    EXPIRED = "EXPIRED"
    DEPRECATED = "DEPRECATED"


@dataclass
class SkillContract:
    identifier: str
    version: str = "0.0.1"
    description: str = ""
    capability: str = ""
    domain: str = ""
    operation: str = ""
    input_types: dict = field(default_factory=dict)
    output_types: dict = field(default_factory=dict)
    preconditions: list = field(default_factory=list)
    postconditions: list = field(default_factory=list)
    permissions: list = field(default_factory=list)
    retries: dict = field(default_factory=dict)
    rollback: str = "none"
    evidence_produced: list = field(default_factory=list)
    result_states: list = field(default_factory=lambda: [s.value for s in ResultState])
    impl: str = ""

    def as_dict(self):
        return asdict(self)


def validate_contract(c):
    e = []
    if not c.identifier:
        e.append("identifier required")
    # impl is optional: an unbound skill is a valid registry entry that
    # dispatches to NOT_RUN (see §07). Only malformed contracts are rejected.
    for s in c.result_states:
        if s not in {r.value for r in ResultState}:
            e.append(f"bad state {s!r}")
    return e


def normalize_result(x):
    if isinstance(x, ResultState):
        return x
    if isinstance(x, str) and x in {r.value for r in ResultState}:
        return ResultState(x)
    if isinstance(x, dict):
        for k in ("result_state", "result", "state", "status"):
            if k in x:
                return normalize_result(x[k])
    return ResultState.FAIL
