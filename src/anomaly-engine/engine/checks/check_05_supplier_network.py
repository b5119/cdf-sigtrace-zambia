"""Check 5 — Supplier network: related-party links among tenderers.

Flags when two or more suppliers in the same tender share a physical address,
telephone number, or TPIN — indicating a potential cartel, front-company
arrangement, or undisclosed conflict of interest.

The check inspects the `parties` list in raw_ocds for the current contract.
Deeper graph analysis across tenders (NetworkX, INC-009) builds on these flags.

Basis: Anti-corruption guidelines — undisclosed relationships between bidders
undermine genuine competition (UNCAC Article 9; ZPPA procurement integrity rules).

False-positive safeguards:
- Framework call-offs are skipped (single supplier pre-agreed).
- Direct/single-source procurement is skipped (no competing suppliers).
- Fewer than 2 suppliers in the release → skip (no network to check).
- Generic/shared business addresses (e.g. "P.O. Box 1") are not flagged
  alone — require at least two matching attributes to confirm.
"""
from engine.base import CheckBase
from engine.models import CheckOutput, CheckResult


def _normalise(s: str | None) -> str:
    if not s:
        return ""
    return s.strip().lower().replace(" ", "").replace("-", "").replace(",", "")


def _get_suppliers(raw_ocds: dict) -> list[dict]:
    """Collect all unique supplier parties across releases."""
    seen_ids: set[str] = set()
    suppliers: list[dict] = []
    for release in raw_ocds.get("releases", []):
        for party in release.get("parties", []):
            if "supplier" not in party.get("roles", []):
                continue
            pid = party.get("id", "")
            if pid in seen_ids:
                continue
            seen_ids.add(pid)
            suppliers.append(party)
    return suppliers


def _procurement_method(raw_ocds: dict) -> str:
    for release in reversed(raw_ocds.get("releases", [])):
        m = release.get("tender", {}).get("procurementMethod", "")
        if m:
            return m.lower()
    return ""


class SupplierNetworkCheck(CheckBase):
    id = 5
    key = "supplier_net"
    name = "Related-party link among tenderers"
    basis = "UNCAC Article 9; ZPPA procurement integrity — undisclosed supplier relationships"
    severity = "medium"
    default_weight = 10.0

    def run(self, contract: dict, config: dict) -> CheckOutput:
        weight = config.get("weights", {}).get(self.key, self.default_weight)

        if contract.get("framework_parent"):
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.SKIP,
                evidence_note="Framework call-off — single pre-agreed supplier.",
            )

        raw_ocds = contract.get("raw_ocds") or {}
        method = _procurement_method(raw_ocds)
        if method in ("direct", "single source"):
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.SKIP,
                evidence_note=f"Procurement method '{method}' — no competing suppliers.",
            )

        suppliers = _get_suppliers(raw_ocds)
        if len(suppliers) < 2:
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.SKIP,
                evidence_note="Fewer than 2 supplier parties in record — no network to evaluate.",
            )

        # Build attribute maps for comparison
        addresses = {}
        phones = {}
        tpins = {}

        for s in suppliers:
            sid = s.get("id", s.get("name", "?"))
            addr = _normalise(s.get("address", {}).get("streetAddress"))
            phone = _normalise(s.get("contactPoint", {}).get("telephone"))
            tpin_val = ""
            ident = s.get("identifier", {})
            if ident.get("scheme") == "ZM-TPIN":
                tpin_val = _normalise(ident.get("id"))

            if addr:
                addresses.setdefault(addr, []).append(sid)
            if phone:
                phones.setdefault(phone, []).append(sid)
            if tpin_val:
                tpins.setdefault(tpin_val, []).append(sid)

        findings: list[str] = []
        for attr_name, attr_map in [("address", addresses), ("phone", phones), ("TPIN", tpins)]:
            for val, sids in attr_map.items():
                if len(sids) >= 2:
                    findings.append(
                        f"Suppliers {sids} share {attr_name} '{val}'"
                    )

        if findings:
            return CheckOutput(
                check_id=self.id, check_key=self.key,
                result=CheckResult.FLAG,
                evidence_note=f"Related-party links detected: {'; '.join(findings)}.",
                weight_applied=weight,
            )

        return CheckOutput(
            check_id=self.id, check_key=self.key,
            result=CheckResult.OK,
            evidence_note=f"No shared attributes detected among {len(suppliers)} supplier(s).",
        )
