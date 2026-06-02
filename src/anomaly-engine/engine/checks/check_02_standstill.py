"""Check 2 — Standstill: contract signed before the statutory standstill period expired.

Basis: Zambia Public Procurement Act — 14-day standstill between Notice of Award
and contract signing, allowing unsuccessful bidders to challenge the award.
Signing before standstill expires is a procedural violation.

False-positive safeguards:
- Framework agreement call-offs are excluded (framework_parent present) — they
  operate under the parent framework's standstill, not a fresh one.
- If either date is absent, the check is SKIPPED (not flagged).
- Emergency procurement is flagged only if justification document is absent
  (full emergency check is INC-004; here we apply the standstill threshold only).
"""
from datetime import date

from engine.base import CheckBase
from engine.config import DEFAULT_THRESHOLDS
from engine.models import CheckOutput, CheckResult


class StandstillCheck(CheckBase):
    id = 2
    key = "standstill"
    name = "Standstill period violation"
    basis = "Public Procurement Act §45 — 14-day challenge window post-award"
    severity = "high"
    default_weight = 20.0

    def run(self, contract: dict, config: dict) -> CheckOutput:
        weight = config.get("weights", {}).get(self.key, self.default_weight)
        min_days: int = config.get("thresholds", {}).get(
            "standstill_days", DEFAULT_THRESHOLDS["standstill_days"]
        )

        # False-positive: framework call-offs skip this check
        if contract.get("framework_parent"):
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.SKIP,
                evidence_note=(
                    f"Framework agreement call-off (parent: {contract['framework_parent']}) — "
                    "standstill requirement covered by parent framework."
                ),
            )

        award_date = contract.get("award_date")
        signing_date = contract.get("signing_date")

        if award_date is None or signing_date is None:
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.SKIP,
                evidence_note="Award date or signing date absent — cannot evaluate standstill.",
            )

        # Both dates present — compute gap
        if isinstance(award_date, str):
            award_date = date.fromisoformat(award_date)
        if isinstance(signing_date, str):
            signing_date = date.fromisoformat(signing_date)

        gap_days = (signing_date - award_date).days

        if gap_days < min_days:
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.FLAG,
                evidence_note=(
                    f"Contract signed {gap_days} day(s) after Notice of Award "
                    f"(minimum standstill: {min_days} days). "
                    f"Award: {award_date}, Signed: {signing_date}."
                ),
                weight_applied=weight,
            )

        return CheckOutput(
            check_id=self.id, check_key=self.key,
            result=CheckResult.OK,
            evidence_note=(
                f"Standstill observed: {gap_days} days between award ({award_date}) "
                f"and signing ({signing_date})."
            ),
        )
