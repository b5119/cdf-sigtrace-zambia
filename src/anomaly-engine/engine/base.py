"""Abstract base class for all anomaly checks."""
from abc import ABC, abstractmethod

from engine.models import CheckOutput


class CheckBase(ABC):
    id: int
    key: str
    name: str
    basis: str          # legal / regulatory basis for the check
    severity: str       # "high" | "medium" | "low"
    default_weight: float

    @abstractmethod
    def run(self, contract: dict, config: dict) -> CheckOutput:
        """
        Evaluate one check against a normalised contract dict.

        Args:
            contract: normalised contract dict (keys match Contract model fields
                      plus 'raw_ocds' for deep inspection).
            config:   runtime thresholds/weights dict (overrides defaults).

        Returns:
            CheckOutput with result FLAG | OK | SKIP.
        """
