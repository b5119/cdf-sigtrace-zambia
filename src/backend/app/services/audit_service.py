"""Audit logging service (INC-018).

Every privileged action appends an append-only AuditLog entry. A periodic batch
of unanchored entries is hashed (SHA-256 over a canonical serialisation) and the
batch hash is anchored to Hyperledger Fabric — making the audit trail
tamper-evident.
"""
import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog

log = logging.getLogger(__name__)


async def log_action(
    db: AsyncSession,
    actor_id: str | None,
    action: str,
    target_type: str | None = None,
    target_ref: str | None = None,
    meta: dict | None = None,
) -> AuditLog:
    """Append one audit entry. Does NOT commit — caller commits with its txn so
    the audit entry is atomic with the action it records."""
    entry = AuditLog(
        id=str(uuid.uuid4()), actor_id=actor_id, action=action,
        target_type=target_type, target_ref=target_ref, meta=meta or {},
        created_at=datetime.now(timezone.utc),
    )
    db.add(entry)
    return entry


def _canonical(entry: AuditLog) -> str:
    """Deterministic serialisation of an audit entry for hashing."""
    return json.dumps({
        "id": entry.id, "actor_id": entry.actor_id, "action": entry.action,
        "target_type": entry.target_type, "target_ref": entry.target_ref,
        "meta": entry.meta, "created_at": entry.created_at.isoformat() if entry.created_at else None,
    }, sort_keys=True, ensure_ascii=False)


def compute_batch_hash(entries: list[AuditLog]) -> str:
    """SHA-256 over the canonical concatenation of all entries in the batch."""
    blob = "\n".join(_canonical(e) for e in entries)
    return hashlib.sha256(blob.encode()).hexdigest()


async def anchor_batch(db: AsyncSession) -> dict:
    """Hash all unanchored audit entries and anchor the batch hash to Fabric.

    Idempotent: entries already anchored are skipped. Returns the batch summary.
    """
    result = await db.execute(
        select(AuditLog).where(AuditLog.anchor_hash.is_(None)).order_by(AuditLog.created_at)
    )
    entries = list(result.scalars().all())
    if not entries:
        return {"anchored": 0, "batch_hash": None, "anchor_tx": None}

    batch_hash = compute_batch_hash(entries)

    # Anchor the batch hash to Fabric (mock or real)
    from app.services.fabric_client import get_fabric_client
    client = get_fabric_client()
    fabric_result = client.submit_set_hash(f"audit-batch-{batch_hash[:12]}", batch_hash)
    anchor_tx = fabric_result["tx_id"]

    # Stamp every entry in the batch
    for e in entries:
        e.anchor_hash = batch_hash
        e.anchor_tx = anchor_tx

    await db.commit()
    log.info("Anchored audit batch: %d entries, hash=%s tx=%s", len(entries), batch_hash[:12], anchor_tx)
    return {"anchored": len(entries), "batch_hash": batch_hash, "anchor_tx": anchor_tx}


async def get_audit(
    db: AsyncSession,
    actor_id: str | None = None,
    action: str | None = None,
    limit: int = 100,
) -> list[dict]:
    query = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    if actor_id:
        query = query.where(AuditLog.actor_id == actor_id)
    if action:
        query = query.where(AuditLog.action == action)
    result = await db.execute(query)
    return [
        {
            "id": e.id, "actor_id": e.actor_id, "action": e.action,
            "target_type": e.target_type, "target_ref": e.target_ref, "meta": e.meta,
            "created_at": e.created_at.isoformat() if e.created_at else None,
            "anchored": e.anchor_hash is not None,
            "anchor_tx": e.anchor_tx,
        }
        for e in result.scalars().all()
    ]


async def verify_integrity(db: AsyncSession) -> dict:
    """Verify the audit trail's integrity: recompute each anchored batch's hash
    from the stored entries and confirm it matches the anchor_hash. Detects any
    tampering with past entries."""
    from collections import defaultdict
    result = await db.execute(
        select(AuditLog).where(AuditLog.anchor_hash.isnot(None)).order_by(AuditLog.created_at)
    )
    anchored = list(result.scalars().all())
    if not anchored:
        return {"verified": True, "batches": 0, "tampered": []}

    batches: dict[str, list[AuditLog]] = defaultdict(list)
    for e in anchored:
        batches[e.anchor_hash].append(e)

    tampered = []
    for stored_hash, entries in batches.items():
        recomputed = compute_batch_hash(entries)
        if recomputed != stored_hash:
            tampered.append({"batch_hash": stored_hash, "recomputed": recomputed})

    return {"verified": len(tampered) == 0, "batches": len(batches), "tampered": tampered}
