"""Check 1 — Signing: contract has no recorded signing date.

Basis: e-GP / CPMS requires a signed contract document before execution.
A missing signing date means either the contract was executed without being
signed, or the signing was not recorded — both are integrity gaps.

False-positive safeguard:
- Cancelled contracts are excluded (they are never expected to be signed).
"""
from engine.base import CheckBase
from engine.models import CheckOutput, CheckResult


class SigningCheck(CheckBase):
    id = 1
    key = "signing"
    name = "Missing contract signing date"
    basis = "Public Procurement Act; e-GP CPMS signing requirement"
    severity = "high"
    default_weight = 15.0

    def run(self, contract: dict, config: dict) -> CheckOutput:
        weight = config.get("weights", {}).get(self.key, self.default_weight)

        status = (contract.get("status") or "active").lower()
        if status == "cancelled":
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.SKIP,
                evidence_note="Contract is cancelled — signing date not required.",
            )

        signing_date = contract.get("signing_date")
        if signing_date is None:
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.FLAG,
                evidence_note="No contract signing date recorded in e-GP/CPMS.",
                weight_applied=weight,
            )

        return CheckOutput(
            check_id=self.id, check_key=self.key,
            result=CheckResult.OK,
            evidence_note=f"Contract signed on {signing_date}.",
        )
