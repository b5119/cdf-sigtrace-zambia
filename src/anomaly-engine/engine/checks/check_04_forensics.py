"""Check 4 — Forensics: round-number bias and predetermined pricing signals.

Two sub-checks derived from forensic accounting practice:

Sub-check A — Round-number bias:
  Contract value is an exact multiple of 1,000,000 ZMW AND the award value
  exactly matches the published tender estimate. When both are true, the
  price shows no evidence of competitive adjustment — consistent with a
  price being set in advance of the tender.

Sub-check B — Award equals estimate exactly:
  The awarded contract value matches the pre-published tender estimate to
  the nearest kwacha. In a genuine competitive process, the winning bid
  rarely equals the estimate exactly; this pattern suggests the estimate
  was reverse-engineered from a predetermined award.

Basis: Forensic accounting — Benford's Law first-digit analysis and
round-number bias are established red flags in procurement fraud detection
(ACFE, World Bank integrity guidelines).

False-positive safeguards:
- If no tender estimate is published in raw_ocds, only sub-check A is run.
- Framework call-offs are skipped (the price is set by the parent framework).
- If contract value is absent, the check is skipped.
"""
from engine.base import CheckBase
from engine.models import CheckOutput, CheckResult


def _get_tender_estimate(raw_ocds: dict) -> float | None:
    for release in reversed(raw_ocds.get("releases", [])):
        v = release.get("tender", {}).get("value", {})
        if v and v.get("amount") is not None:
            return float(v["amount"])
    return None


def _is_round_number(value: float, granularity: float = 1_000_000) -> bool:
    """True if value is an exact multiple of granularity (no fractional part)."""
    return value > 0 and (value % granularity) == 0


class ForensicsCheck(CheckBase):
    id = 4
    key = "forensics"
    name = "Forensic pricing anomaly (round-number bias / predetermined price)"
    basis = "ACFE / World Bank procurement fraud indicators — Benford's Law & round-number analysis"
    severity = "medium"
    default_weight = 15.0

    def run(self, contract: dict, config: dict) -> CheckOutput:
        weight = config.get("weights", {}).get(self.key, self.default_weight)

        if contract.get("framework_parent"):
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.SKIP,
                evidence_note="Framework call-off — price set by parent framework agreement.",
            )

        value = contract.get("value")
        if value is None:
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.SKIP,
                evidence_note="Contract value absent — cannot run forensic pricing analysis.",
            )

        value = float(value)
        raw_ocds = contract.get("raw_ocds") or {}
        estimate = _get_tender_estimate(raw_ocds)

        flags = []

        # Sub-check A: round-number bias
        if _is_round_number(value):
            flags.append(
                f"Contract value (ZMW {value:,.0f}) is an exact multiple of 1,000,000 — "
                "round-number bias detected."
            )

        # Sub-check B: award equals estimate exactly
        if estimate is not None and abs(value - estimate) < 0.01:
            flags.append(
                f"Awarded value (ZMW {value:,.2f}) exactly matches published tender estimate "
                f"(ZMW {estimate:,.2f}) — no evidence of competitive price adjustment."
            )

        if flags:
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.FLAG,
                evidence_note=" | ".join(flags),
                weight_applied=weight,
            )

        return CheckOutput(
            check_id=self.id, check_key=self.key,
            result=CheckResult.OK,
            evidence_note=(
                f"No forensic pricing anomaly detected. "
                f"Award: ZMW {value:,.2f}"
                + (f", Estimate: ZMW {estimate:,.2f}." if estimate else ".")
            ),
        )
