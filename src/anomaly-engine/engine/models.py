"""Data structures for check results (INC-003)."""
from dataclasses import dataclass, field
from enum import StrEnum


class CheckResult(StrEnum):
    FLAG = "flag"
    OK   = "ok"
    SKIP = "skip"   # prerequisites missing — don't count against the contract


@dataclass
class CheckOutput:
    check_id: int
    check_key: str
    result: CheckResult
    evidence_note: str
    weight_applied: float = 0.0  # weight only counts when result == FLAG


@dataclass
class EngineOutput:
    contract_ocid: str
    outputs: list[CheckOutput] = field(default_factory=list)

    @property
    def flag_count(self) -> int:
        return sum(1 for o in self.outputs if o.result == CheckResult.FLAG)

    @property
    def raw_score(self) -> float:
        """Sum of weights of all flagged checks (0–100)."""
        return sum(o.weight_applied for o in self.outputs if o.result == CheckResult.FLAG)
