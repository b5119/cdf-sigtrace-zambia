"""Anchoring service (INC-006).

Computes SHA-256 of a document, writes it to Hyperledger Fabric,
and persists the AnchorRecord. The document bytes NEVER leave this service
— only the hash goes on-chain.

Key invariants:
- Idempotency: anchoring the same contract+hash twice returns the existing
  record without a second Fabric transaction.
- Re-anchoring with a different hash IS allowed (document re-signed/corrected)
  and creates a new record; full history is preserved.
- The document itself is stored separately in object storage (INC-007),
  never on-chain.
"""
import hashlib
import logging
from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.anchor import AnchorRecord
from app.models.contract import Contract
from app.services.fabric_client import get_fabric_client

log = logging.getLogger(__name__)


class VerifyVerdict(StrEnum):
    MATCH = "match"
    MISMATCH = "mismatch"
    NOT_REGISTERED = "not_registered"


def compute_sha256(data: bytes) -> str:
    """Return the hex SHA-256 digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()


async def anchor_contract(
    db: AsyncSession,
    ocid: str,
    document_bytes: bytes,
    anchored_by: Optional[str] = None,
) -> AnchorRecord:
    """
    Hash the document and anchor it to Fabric. Idempotent on (ocid, sha256).

    Args:
        db:             async DB session.
        ocid:           contract OCID being anchored.
        document_bytes: raw PDF/document bytes (never stored or sent on-chain).
        anchored_by:    user ID of the officer triggering the anchor.

    Returns:
        The AnchorRecord (newly created or existing if same hash).

    Raises:
        ValueError: if the contract OCID is not found in the DB.
    """
    # Verify contract exists
    c_result = await db.execute(select(Contract).where(Contract.ocid == ocid))
    if not c_result.scalar_one_or_none():
        raise ValueError(f"Contract {ocid!r} not found")

    sha256 = compute_sha256(document_bytes)

    # Idempotency: return existing record if same hash already anchored
    existing = await db.execute(
        select(AnchorRecord)
        .where(AnchorRecord.contract_ocid == ocid, AnchorRecord.sha256 == sha256)
        .order_by(AnchorRecord.anchored_at.desc())
        .limit(1)
    )
    existing_record = existing.scalar_one_or_none()
    if existing_record:
        log.info("Anchor idempotent hit for %s sha256=%s", ocid, sha256[:8])
        return existing_record

    # Submit to Fabric (or mock)
    client = get_fabric_client()
    is_mock = hasattr(client, "clear")  # MockFabricClient has .clear()

    try:
        fabric_result = client.submit_set_hash(ocid, sha256)
        tx_id = fabric_result["tx_id"]
        block_ref = fabric_result["block_ref"]
        log.info(
            "Anchored %s sha256=%s tx=%s block=%s%s",
            ocid, sha256[:8], tx_id, block_ref, " [MOCK]" if is_mock else "",
        )
    except Exception as e:
        log.error("Fabric submission failed for %s: %s", ocid, e)
        raise

    record = AnchorRecord(
        contract_ocid=ocid,
        sha256=sha256,
        ledger="fabric",
        ledger_tx=tx_id,
        block_ref=block_ref,
        anchored_by=anchored_by,
        anchored_at=datetime.now(timezone.utc),
        is_mock=is_mock,
    )
    db.add(record)

    # Keep contract.signing_doc_ref in sync (using anchor record id as object-store key)
    c_result2 = await db.execute(select(Contract).where(Contract.ocid == ocid))
    contract = c_result2.scalar_one_or_none()
    if contract:
        contract.signing_doc_ref = str(record.id)

    from app.services.audit_service import log_action
    await log_action(db, anchored_by, "contract_anchored", "contract", ocid, {"sha256": sha256})
    await db.commit()
    await db.refresh(record)
    return record


async def verify_document(
    db: AsyncSession,
    ocid: str,
    document_bytes: bytes,
) -> dict:
    """
    Verify a document against the latest anchor for a given OCID.

    Returns a dict with:
      verdict:      "match" | "mismatch" | "not_registered"
      provided_hash: the SHA-256 of the uploaded bytes
      anchored_hash: the on-chain hash (if registered)
      anchor_record: the latest AnchorRecord (if registered)
    """
    provided_hash = compute_sha256(document_bytes)

    result = await db.execute(
        select(AnchorRecord)
        .where(AnchorRecord.contract_ocid == ocid)
        .order_by(AnchorRecord.anchored_at.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()

    if not latest:
        return {
            "verdict": VerifyVerdict.NOT_REGISTERED,
            "provided_hash": provided_hash,
            "anchored_hash": None,
            "anchor": None,
        }

    verdict = VerifyVerdict.MATCH if provided_hash == latest.sha256 else VerifyVerdict.MISMATCH
    return {
        "verdict": verdict,
        "provided_hash": provided_hash,
        "anchored_hash": latest.sha256,
        "anchor": latest,
    }


async def get_anchor_history(db: AsyncSession, ocid: str) -> list[AnchorRecord]:
    """Return all anchor records for a contract, newest first."""
    result = await db.execute(
        select(AnchorRecord)
        .where(AnchorRecord.contract_ocid == ocid)
        .order_by(AnchorRecord.anchored_at.desc())
    )
    return list(result.scalars().all())
