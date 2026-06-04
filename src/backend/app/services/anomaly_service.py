"""Service: run the anomaly engine against a contract and persist flags (INC-003)."""
import uuid
import logging
from datetime import datetime, timezone

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.anomaly import AnomalyFlag, CheckDefinition
from app.models.contract import Contract

log = logging.getLogger(__name__)


def _contract_to_dict(contract: Contract) -> dict:
    """Convert a Contract ORM object into the dict the engine expects."""
    return {
        "ocid": contract.ocid,
        "procuring_entity": contract.procuring_entity,
        "value": float(contract.value) if contract.value else None,
        "currency": contract.currency,
        "award_date": contract.award_date,
        "signing_date": contract.signing_date,
        "framework_parent": contract.framework_parent,
        "status": contract.status,
        "raw_ocds": contract.raw_ocds or {},
    }


async def _load_config(db: AsyncSession) -> dict:
    """Load weights from check_definitions and thresholds from the Config table.

    Both are admin-tunable (INC-017) — updating them changes how contracts score
    on the next analysis run.
    """
    result = await db.execute(select(CheckDefinition))
    definitions = result.scalars().all()
    weights = {d.key: d.weight for d in definitions}
    enabled = {d.id for d in definitions if d.enabled}

    # Load admin-tuned thresholds (falls back to engine defaults if unset)
    thresholds: dict = {}
    try:
        from app.models.config import Config
        cfg_result = await db.execute(select(Config).where(Config.key == "thresholds"))
        cfg = cfg_result.scalar_one_or_none()
        if cfg and cfg.value:
            thresholds = dict(cfg.value)
    except Exception:
        thresholds = {}

    return {"weights": weights, "enabled": enabled, "thresholds": thresholds}


async def analyse_contract(db: AsyncSession, ocid: str) -> dict:
    """
    Run all enabled checks against one contract and persist/replace its AnomalyFlag rows.
    Returns a summary dict of the engine output.
    """
    from engine.runner import run_checks, build_config

    result = await db.execute(select(Contract).where(Contract.ocid == ocid))
    contract = result.scalar_one_or_none()
    if contract is None:
        raise ValueError(f"Contract {ocid!r} not found")

    config = await _load_config(db)
    contract_dict = _contract_to_dict(contract)

    engine_out = run_checks(contract_dict, config)

    # Replace existing flags for this contract
    await db.execute(delete(AnomalyFlag).where(AnomalyFlag.contract_ocid == ocid))

    flag_rows = []
    for output in engine_out.outputs:
        flag = AnomalyFlag(
            id=str(uuid.uuid4()),
            contract_ocid=ocid,
            check_id=output.check_id,
            result=output.result,
            weight_applied=output.weight_applied,
            evidence_note=output.evidence_note,
            created_at=datetime.now(timezone.utc),
        )
        db.add(flag)
        flag_rows.append(flag)

    # Update the contract's risk_score (raw score for now; normalised scoring in INC-005)
    contract.risk_score = int(round(engine_out.raw_score))
    await db.commit()

    log.info(
        "Analysed contract %s — flags=%d raw_score=%.1f",
        ocid, engine_out.flag_count, engine_out.raw_score,
    )

    return {
        "ocid": ocid,
        "flag_count": engine_out.flag_count,
        "raw_score": engine_out.raw_score,
        "checks": [
            {
                "check_id": o.check_id,
                "check_key": o.check_key,
                "result": str(o.result),
                "evidence_note": o.evidence_note,
                "weight_applied": o.weight_applied,
            }
            for o in engine_out.outputs
        ],
    }


async def analyse_all_contracts(db: AsyncSession) -> dict:
    """Run the engine over all contracts in the DB. Returns aggregate counts."""
    result = await db.execute(select(Contract.ocid))
    ocids = [row[0] for row in result.all()]

    flagged = 0
    errors = []
    for ocid in ocids:
        try:
            out = await analyse_contract(db, ocid)
            if out["flag_count"] > 0:
                flagged += 1
        except Exception as e:
            log.error("Failed to analyse %s: %s", ocid, e)
            errors.append({"ocid": ocid, "error": str(e)})

    return {"total": len(ocids), "flagged": flagged, "errors": errors}
