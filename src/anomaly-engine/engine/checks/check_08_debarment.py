"""Check 8 — Debarment: contract awarded to a supplier on the ZPPA debarment register.

A debarred supplier is legally ineligible to participate in public procurement during
the debarment period. Awarding a contract to a debarred supplier is a serious
procurement integrity violation — the award should be invalidated.

The debarment status is supplied via the contract context dict under the key
`supplier_debarred_until` (a date object or ISO string). The anomaly service
populates this from the `Supplier.debarred_until` DB field before running checks.

Basis: ZPPA debarment register; Public Procurement Act — debarred suppliers
are ineligible for contract award during the debarment period.

False-positive safeguards:
- If debarment information is absent (supplier not in DB or not checked), the
  check is SKIPPED rather than falsely flagging — absence of data ≠ debarment.
- If award date is absent, we compare against today (conservative approach:
  if still debarred now, flag it).
"""
from datetime import date

from engine.base import CheckBase
from engine.models import CheckOutput, CheckResult


def _parse_date(d) -> date | None:
    if d is None:
        return None
    if isinstance(d, date):
        return d
    try:
        return date.fromisoformat(str(d)[:10])
    except (ValueError, TypeError):
        return None


class DebarmentCheck(CheckBase):
    id = 8
    key = "debarment"
    name = "Contract awarded to debarred supplier"
    basis = "ZPPA debarment register; Public Procurement Act — ineligible suppliers"
    severity = "high"
    default_weight = 10.0

    def run(self, contract: dict, config: dict) -> CheckOutput:
        weight = config.get("weights", {}).get(self.key, self.default_weight)

        debarred_until_raw = contract.get("supplier_debarred_until")
        if debarred_until_raw is None:
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.SKIP,
                evidence_note=(
                    "Supplier debarment status not available — "
                    "manual check against ZPPA register required."
                ),
            )

        debarred_until = _parse_date(debarred_until_raw)
        if debarred_until is None:
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.SKIP,
                evidence_note="Could not parse debarment date — manual check required.",
            )

        # Use award date as reference; fall back to today
        reference_date = _parse_date(contract.get("award_date")) or date.today()

        if debarred_until >= reference_date:
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.FLAG,
                evidence_note=(
                    f"Supplier was debarred until {debarred_until} at the time of award "
                    f"({reference_date}) — ineligible for contract award."
                ),
                weight_applied=weight,
            )

        return CheckOutput(
            check_id=self.id, check_key=self.key,
            result=CheckResult.OK,
            evidence_note=(
                f"Supplier debarment ended {debarred_until}, "
                f"before award date {reference_date} — eligible."
            ),
        )
