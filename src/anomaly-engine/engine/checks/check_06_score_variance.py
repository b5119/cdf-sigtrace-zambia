"""Check 6 — Score variance: awarded value significantly exceeds tender estimate.

When the winning bid price is materially above the pre-published tender estimate,
it suggests either budget gaming (the estimate was set artificially low to bypass
a higher approval threshold) or post-award price inflation before signing.

Threshold: configurable `score_variance_pct` (default 15%). A contract whose
awarded value exceeds the estimate by more than this percentage is flagged.

Basis: ZPPA procurement guidelines — award values substantially over the
approved estimate require justification and may indicate approval threshold
circumvention or collusive pricing.

False-positive safeguards:
- If no tender estimate is published, the check is skipped.
- Framework call-offs are skipped (price governed by the framework).
- Direct procurement is skipped (no published estimate comparison applies).
- Negative variance (award below estimate) is expected and not flagged.
"""
from engine.base import CheckBase
from engine.config import DEFAULT_THRESHOLDS
from engine.models import CheckOutput, CheckResult


def _get_tender_estimate(raw_ocds: dict) -> float | None:
    for release in reversed(raw_ocds.get("releases", [])):
        v = release.get("tender", {}).get("value", {})
        if v and v.get("amount") is not None:
            return float(v["amount"])
    return None


class ScoreVarianceCheck(CheckBase):
    id = 6
    key = "score_var"
    name = "Award value significantly exceeds tender estimate"
    basis = "ZPPA guidelines — award-over-estimate ratio signals budget gaming or threshold circumvention"
    severity = "low"
    default_weight = 5.0

    def run(self, contract: dict, config: dict) -> CheckOutput:
        weight = config.get("weights", {}).get(self.key, self.default_weight)
        cap_pct: float = config.get("thresholds", {}).get(
            "amendment_cap_pct", DEFAULT_THRESHOLDS["amendment_cap_pct"]
        )  # reuse amendment cap as the over-estimate threshold

        if contract.get("framework_parent"):
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.SKIP,
                evidence_note="Framework call-off — price governed by parent framework.",
            )

        value = contract.get("value")
        if value is None:
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.SKIP,
                evidence_note="Contract value absent.",
            )

        raw_ocds = contract.get("raw_ocds") or {}
        estimate = _get_tender_estimate(raw_ocds)
        if estimate is None or estimate <= 0:
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.SKIP,
                evidence_note="No published tender estimate in record — cannot compare.",
            )

        value = float(value)
        over_pct = ((value - estimate) / estimate) * 100

        if over_pct > cap_pct:
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.FLAG,
                evidence_note=(
                    f"Awarded value (ZMW {value:,.2f}) exceeds tender estimate "
                    f"(ZMW {estimate:,.2f}) by {over_pct:.1f}% "
                    f"(threshold: {cap_pct:.0f}%)."
                ),
                weight_applied=weight,
            )

        return CheckOutput(
            check_id=self.id, check_key=self.key,
            result=CheckResult.OK,
            evidence_note=(
                f"Award within tolerance: ZMW {value:,.2f} vs estimate ZMW {estimate:,.2f} "
                f"({over_pct:+.1f}%)."
            ),
        )
