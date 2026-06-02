"""Check 3 — Time-gap: suspicious compression of tender evaluation timeline.

Flags when the gap between tender period close and award date is less than
the minimum evaluation period (default 1 day), suggesting dates were
auto-populated, backdated, or the evaluation was not genuinely conducted.

Also flags when multiple key stage dates are identical (e.g. tender close
== award date == signing date on the same calendar day), which is a strong
indicator of fabricated or copy-pasted procurement records.

Basis: ZPPA procurement guidelines require a defined evaluation period between
tender close and award. Zero-day evaluations are procedurally impossible.

False-positive safeguards:
- Framework call-offs are skipped (no open tender stage).
- Direct / single-source procurement is skipped (no tender period by design).
- If tender period dates are absent in raw_ocds, the check is SKIPPED.
"""
from datetime import date

from engine.base import CheckBase
from engine.config import DEFAULT_THRESHOLDS
from engine.models import CheckOutput, CheckResult


def _parse(d) -> date | None:
    if d is None:
        return None
    if isinstance(d, date):
        return d
    try:
        return date.fromisoformat(str(d)[:10])
    except (ValueError, TypeError):
        return None


def _extract_tender_dates(raw_ocds: dict) -> tuple[date | None, date | None]:
    """Pull tender period start/end from the most recent release."""
    releases = raw_ocds.get("releases", [])
    for release in reversed(releases):
        tp = release.get("tender", {}).get("tenderPeriod", {})
        start = _parse(tp.get("startDate"))
        end = _parse(tp.get("endDate"))
        if start or end:
            return start, end
    return None, None


def _procurement_method(raw_ocds: dict) -> str:
    releases = raw_ocds.get("releases", [])
    for release in reversed(releases):
        method = release.get("tender", {}).get("procurementMethod", "")
        if method:
            return method.lower()
    return ""


class TimeGapCheck(CheckBase):
    id = 3
    key = "time_gap"
    name = "Suspicious compression of tender timeline"
    basis = "ZPPA procurement guidelines — mandatory evaluation period"
    severity = "medium"
    default_weight = 15.0

    def run(self, contract: dict, config: dict) -> CheckOutput:
        weight = config.get("weights", {}).get(self.key, self.default_weight)
        min_days: int = config.get("thresholds", {}).get(
            "time_gap_min_days", DEFAULT_THRESHOLDS["time_gap_min_days"]
        )

        raw_ocds = contract.get("raw_ocds") or {}

        # Skip framework call-offs (no open tender stage)
        if contract.get("framework_parent"):
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.SKIP,
                evidence_note="Framework call-off — no open tender stage to evaluate.",
            )

        # Skip direct / single-source (no tender period by design)
        method = _procurement_method(raw_ocds)
        if method in ("direct", "limited", "single source"):
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.SKIP,
                evidence_note=f"Procurement method '{method}' has no open tender period.",
            )

        tender_start, tender_end = _extract_tender_dates(raw_ocds)
        award_date = _parse(contract.get("award_date"))
        signing_date = _parse(contract.get("signing_date"))

        # --- Sub-check B: identical key stage dates (checked first — stronger signal) ---
        key_dates = [d for d in [tender_end, award_date, signing_date] if d is not None]
        if len(key_dates) >= 2 and len(set(key_dates)) == 1:
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.FLAG,
                evidence_note=(
                    f"Multiple key procurement stage dates are identical ({key_dates[0]}): "
                    "tender close, award, and/or signing all on the same day — "
                    "suggests fabricated or auto-populated dates."
                ),
                weight_applied=weight,
            )

        # --- Sub-check A: tender close → award gap ---
        if tender_end is not None and award_date is not None:
            eval_gap = (award_date - tender_end).days
            if eval_gap < min_days:
                return CheckOutput(
                    check_id=self.id, check_key=self.key,
                    result=CheckResult.FLAG,
                    evidence_note=(
                        f"Award issued {eval_gap} day(s) after tender close "
                        f"(minimum evaluation period: {min_days} day(s)). "
                        f"Tender closed: {tender_end}, Award: {award_date}."
                    ),
                    weight_applied=weight,
                )

        if tender_end is None:
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.SKIP,
                evidence_note="Tender period close date absent — cannot evaluate timeline.",
            )

        return CheckOutput(
            check_id=self.id, check_key=self.key,
            result=CheckResult.OK,
            evidence_note=(
                f"Tender timeline acceptable. "
                f"Tender close: {tender_end}, Award: {award_date}, Signed: {signing_date}."
            ),
        )
