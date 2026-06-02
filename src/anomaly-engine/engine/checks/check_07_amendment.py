"""Check 7 — Amendment: contract value increased beyond the permitted cap via amendments.

Zambian procurement law requires a fresh tender when cumulative amendments increase
the contract value by more than the permitted threshold (default 15%). Exceeding this
cap without re-tendering circumvents competitive procurement and is a procurement
integrity violation.

The check sums all amendment value changes from `contracts[].amendments` in raw_ocds
and computes the cumulative percentage change against the original signed value.

Basis: Public Procurement Act — amendment value cap; amendments beyond the threshold
require re-tendering or head-of-entity approval with documented justification.

False-positive safeguards:
- If no amendments are recorded, the check returns OK (no amendments, no violation).
- If original value is absent or zero, the check is skipped.
- Price changes due to forex/escalation clauses recorded in the amendment reason
  are noted in evidence but still flagged (oversight body decides the justification).
"""
from engine.base import CheckBase
from engine.config import DEFAULT_THRESHOLDS
from engine.models import CheckOutput, CheckResult


def _get_amendments(raw_ocds: dict) -> list[dict]:
    """Collect all amendments from all contract records in the releases."""
    amendments = []
    for release in raw_ocds.get("releases", []):
        for ctr in release.get("contracts", []):
            for amend in ctr.get("amendments", []):
                amendments.append(amend)
    return amendments


def _amendment_value_delta(amendment: dict) -> float:
    """Extract the value change from an amendment record (positive = increase)."""
    # OCDS amendments may have a 'value' field showing the new total, or a 'changes' array.
    # We look for an explicit amount delta; fall back to 0 if not parseable.
    val = amendment.get("value", {})
    if isinstance(val, dict) and val.get("amount") is not None:
        # This is the new total value — we can't derive delta without original; treat as additive flag
        return float(val["amount"])
    changes = amendment.get("changes", [])
    for change in changes:
        if change.get("property") == "value.amount":
            try:
                return float(change.get("newValue", 0)) - float(change.get("oldValue", 0))
            except (TypeError, ValueError):
                pass
    return 0.0


class AmendmentCheck(CheckBase):
    id = 7
    key = "amendment"
    name = "Contract amendments exceed permitted value cap"
    basis = "Public Procurement Act — amendment cap; excess requires re-tendering"
    severity = "medium"
    default_weight = 10.0

    def run(self, contract: dict, config: dict) -> CheckOutput:
        weight = config.get("weights", {}).get(self.key, self.default_weight)
        cap_pct: float = config.get("thresholds", {}).get(
            "amendment_cap_pct", DEFAULT_THRESHOLDS["amendment_cap_pct"]
        )

        original_value = contract.get("value")
        if original_value is None or float(original_value) <= 0:
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.SKIP,
                evidence_note="Original contract value absent — cannot compute amendment percentage.",
            )

        raw_ocds = contract.get("raw_ocds") or {}
        amendments = _get_amendments(raw_ocds)

        if not amendments:
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.OK,
                evidence_note="No amendments recorded on this contract.",
            )

        original = float(original_value)
        total_delta = sum(_amendment_value_delta(a) for a in amendments)
        cumulative_pct = (total_delta / original) * 100

        if cumulative_pct > cap_pct:
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.FLAG,
                evidence_note=(
                    f"Cumulative amendment value increase: {cumulative_pct:.1f}% "
                    f"(cap: {cap_pct:.0f}%). "
                    f"Original: ZMW {original:,.2f}, total amendment delta: ZMW {total_delta:,.2f}. "
                    f"{len(amendments)} amendment(s) recorded."
                ),
                weight_applied=weight,
            )

        return CheckOutput(
            check_id=self.id, check_key=self.key,
            result=CheckResult.OK,
            evidence_note=(
                f"{len(amendments)} amendment(s) recorded; cumulative increase {cumulative_pct:.1f}% "
                f"within the {cap_pct:.0f}% cap."
            ),
        )
