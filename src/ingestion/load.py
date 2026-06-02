"""Upsert normalised OCDS data into the database. Idempotent on OCID + content hash."""
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contract import Contract, IngestionRun, Supplier

log = logging.getLogger(__name__)


async def _upsert_supplier(db: AsyncSession, supplier_dict: dict) -> uuid.UUID:
    """Insert or update a supplier by name+tpin; return its UUID."""
    tpin = supplier_dict.get("tpin")
    name = supplier_dict["name"]

    # Find by TPIN (most stable identifier) or fall back to name
    existing = None
    if tpin:
        result = await db.execute(select(Supplier).where(Supplier.tpin == tpin))
        existing = result.scalar_one_or_none()
    if existing is None:
        result = await db.execute(select(Supplier).where(Supplier.name == name))
        existing = result.scalar_one_or_none()

    if existing:
        # Update mutable fields
        if supplier_dict.get("address"):
            existing.address = supplier_dict["address"]
        if supplier_dict.get("phone"):
            existing.phone = supplier_dict["phone"]
        return existing.id
    else:
        new_supplier = Supplier(
            id=uuid.uuid4(),
            name=name,
            tpin=tpin,
            address=supplier_dict.get("address"),
            phone=supplier_dict.get("phone"),
            shareholders=supplier_dict.get("shareholders"),
        )
        db.add(new_supplier)
        await db.flush()
        return new_supplier.id


async def upsert_contract(
    db: AsyncSession,
    contract_dict: dict,
    supplier_dict: dict | None,
) -> str:
    """
    Insert or update a contract by OCID.
    If content_hash unchanged, skip the update (no-op).
    Returns 'created' | 'updated' | 'skipped'.
    """
    ocid = contract_dict["ocid"]
    new_hash = contract_dict.get("content_hash")

    result = await db.execute(select(Contract).where(Contract.ocid == ocid))
    existing = result.scalar_one_or_none()

    # Resolve supplier ID
    supplier_id: uuid.UUID | None = None
    if supplier_dict:
        supplier_id = await _upsert_supplier(db, supplier_dict)

    if existing:
        if existing.content_hash == new_hash:
            return "skipped"
        # Update the contract
        existing.procuring_entity = contract_dict["procuring_entity"]
        existing.supplier_id = supplier_id
        existing.value = contract_dict.get("value")
        existing.currency = contract_dict.get("currency", "ZMW")
        existing.award_date = contract_dict.get("award_date")
        existing.signing_date = contract_dict.get("signing_date")
        existing.framework_parent = contract_dict.get("framework_parent")
        existing.status = contract_dict.get("status", "active")
        existing.content_hash = new_hash
        existing.raw_ocds = contract_dict["raw_ocds"]
        return "updated"
    else:
        new_contract = Contract(
            ocid=ocid,
            procuring_entity=contract_dict["procuring_entity"],
            supplier_id=supplier_id,
            value=contract_dict.get("value"),
            currency=contract_dict.get("currency", "ZMW"),
            award_date=contract_dict.get("award_date"),
            signing_date=contract_dict.get("signing_date"),
            framework_parent=contract_dict.get("framework_parent"),
            status=contract_dict.get("status", "active"),
            content_hash=new_hash,
            raw_ocds=contract_dict["raw_ocds"],
        )
        db.add(new_contract)
        return "created"


async def run_load(
    db: AsyncSession,
    normalised: list[tuple[dict, dict | None]],
    run: IngestionRun,
) -> None:
    """Load all normalised records into the DB, updating the IngestionRun as we go."""
    created = updated = skipped = 0
    errors: list[dict] = []

    for contract_dict, supplier_dict in normalised:
        ocid = contract_dict.get("ocid", "unknown")
        try:
            outcome = await upsert_contract(db, contract_dict, supplier_dict)
            if outcome == "created":
                created += 1
            elif outcome == "updated":
                updated += 1
            else:
                skipped += 1
        except Exception as e:
            log.error("Error loading contract %s: %s", ocid, e)
            errors.append({"ocid": ocid, "error": str(e)})

    await db.flush()

    run.records_loaded = created
    run.records_updated = updated
    run.records_skipped = skipped
    run.errors = errors
    run.status = "failed" if errors and (created + updated) == 0 else "complete"
    run.finished_at = datetime.now(timezone.utc)
    await db.commit()

    log.info(
        "Ingestion complete — created=%d updated=%d skipped=%d errors=%d",
        created, updated, skipped, len(errors),
    )
