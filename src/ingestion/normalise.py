"""Normalise an OCDS record into domain-model dicts for Contract and Supplier."""
import hashlib
import json
import logging
from datetime import date
from typing import Any

log = logging.getLogger(__name__)


def _parse_date(value: str | None) -> date | None:
    """Parse an ISO-8601 date/datetime string to a Python date, returning None on failure."""
    if not value:
        return None
    try:
        # Accept both "2024-03-15" and "2024-03-15T10:00:00Z"
        return date.fromisoformat(value[:10])
    except (ValueError, TypeError):
        log.warning("Could not parse date: %r", value)
        return None


def _get_party(releases: list[dict], role: str) -> dict | None:
    """Find the first party with the given role across all releases."""
    for release in releases:
        for party in release.get("parties", []):
            if role in party.get("roles", []):
                return party
    return None


def _get_latest_contract(releases: list[dict]) -> dict | None:
    """Find the latest contract record across releases."""
    for release in reversed(releases):
        contracts = release.get("contracts", [])
        if contracts:
            return contracts[0]
    return None


def _get_latest_award(releases: list[dict]) -> dict | None:
    for release in reversed(releases):
        awards = release.get("awards", [])
        if awards:
            return awards[0]
    return None


def _framework_parent(record: dict) -> str | None:
    """Extract the OCID of the parent framework agreement if this is a call-off."""
    releases = record.get("releases", [])
    for release in releases:
        for rp in release.get("relatedProcesses", []):
            if "framework" in rp.get("relationship", []):
                return rp.get("identifier")
    return None


def _content_hash(raw: dict) -> str:
    """SHA-256 of the canonical JSON representation of a raw OCDS record."""
    serialised = json.dumps(raw, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialised.encode()).hexdigest()


def normalise_record(record: dict) -> tuple[dict, dict | None]:
    """
    Normalise one OCDS record into (contract_dict, supplier_dict | None).

    Returns raw dicts — not ORM objects — for easier testing and bulk loading.
    """
    ocid: str = record.get("ocid", "")
    releases: list[dict] = record.get("releases", [])

    procuring_party = _get_party(releases, "procuringEntity")
    supplier_party = _get_party(releases, "supplier")
    latest_contract = _get_latest_contract(releases)
    latest_award = _get_latest_award(releases)

    # Procuring entity name (fall back to OCID if not found)
    procuring_entity = (procuring_party or {}).get("name", f"Unknown ({ocid})")

    # Contract value and currency
    value: float | None = None
    currency: str = "ZMW"
    if latest_contract:
        cv = latest_contract.get("value") or {}
        value = cv.get("amount")
        currency = cv.get("currency", "ZMW")
    elif latest_award:
        av = latest_award.get("value") or {}
        value = av.get("amount")
        currency = av.get("currency", "ZMW")

    # Dates
    award_date = _parse_date((latest_award or {}).get("date"))
    signing_date = _parse_date((latest_contract or {}).get("dateSigned"))

    # Contract status
    contract_status = (latest_contract or {}).get("status", "active")
    if contract_status not in ("active", "complete", "cancelled"):
        contract_status = "active"

    # Framework call-off detection
    framework_parent = _framework_parent(record)

    contract = {
        "ocid": ocid,
        "procuring_entity": procuring_entity,
        "value": value,
        "currency": currency,
        "award_date": award_date,
        "signing_date": signing_date,
        "framework_parent": framework_parent,
        "status": contract_status,
        "raw_ocds": record,
        "content_hash": _content_hash(record),
    }

    # Supplier dict (None if no supplier party found)
    supplier: dict | None = None
    if supplier_party:
        identifier = supplier_party.get("identifier") or {}
        tpin = identifier.get("id") if identifier.get("scheme") == "ZM-TPIN" else None
        address = supplier_party.get("address", {})
        contact = supplier_party.get("contactPoint", {})
        supplier = {
            "_party_id": supplier_party.get("id", ""),
            "name": supplier_party.get("name", "Unknown"),
            "tpin": tpin,
            "address": address.get("streetAddress"),
            "phone": contact.get("telephone"),
            "shareholders": None,
        }

    return contract, supplier


def normalise_records(records: list[dict]) -> list[tuple[dict, dict | None]]:
    results = []
    for record in records:
        try:
            results.append(normalise_record(record))
        except Exception as e:
            log.error("Failed to normalise record %s: %s", record.get("ocid"), e)
    return results
