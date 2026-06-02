"""Contracts API — /api/v1/contracts/* (INC-005 subset; extended in INC-009).

INC-005 delivers:
  GET  /contracts                — risk list (restricted, de-identified score in public tier)
  GET  /contracts/{ocid}         — full contract record (restricted)
  GET  /contracts/{ocid}/risk    — score + breakdown (restricted)
  GET  /contracts/{ocid}/checks  — per-check results (restricted)
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_current_user_optional
from app.core.rbac import Permission, require_permission
from app.core.scoping import is_restricted
from app.db.session import get_db
from app.models.anomaly import AnomalyFlag, CheckDefinition
from app.models.contract import Contract
from app.models.risk import RiskScore
from app.models.user import User
from app.schemas.contract import (
    CheckResultOut,
    ContractPublic,
    ContractPublicList,
    ContractRestricted,
    ContractRestrictedList,
    RiskScoreOut,
)
from app.services.scoring_service import risk_tier

router = APIRouter(prefix="/contracts", tags=["contracts"])


# ── List contracts ─────────────────────────────────────────────────────────────

@router.get("")
async def list_contracts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    min_score: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    List contracts with risk scores.
    - Public callers: de-identified (no names), score only.
    - Restricted callers: full named data.
    """
    query = select(Contract)
    if status:
        query = query.where(Contract.status == status)
    if min_score is not None:
        query = query.where(Contract.risk_score >= min_score)

    count_q = select(func.count()).select_from(Contract)
    if status:
        count_q = count_q.where(Contract.status == status)
    if min_score is not None:
        count_q = count_q.where(Contract.risk_score >= min_score)

    query = query.order_by(Contract.risk_score.desc().nulls_last()).offset((page - 1) * size).limit(size)

    result = await db.execute(query)
    contracts = result.scalars().all()
    total_result = await db.execute(count_q)
    total = total_result.scalar_one()

    role_key = current_user.role.key if current_user else "anonymous"
    restricted = is_restricted(role_key)

    if restricted:
        items = [ContractRestricted.model_validate(c) for c in contracts]
        return ContractRestrictedList(contracts=items, total=total, page=page, size=size)

    items = [
        ContractPublic(
            ocid=c.ocid,
            status=c.status,
            risk_score=c.risk_score,
            risk_tier=risk_tier(c.risk_score) if c.risk_score is not None else None,
            award_date=c.award_date,
            signing_date=c.signing_date,
            framework_parent=c.framework_parent,
        )
        for c in contracts
    ]
    return ContractPublicList(contracts=items, total=total, page=page, size=size)


# ── Single contract ────────────────────────────────────────────────────────────

@router.get("/{ocid}", response_model=ContractRestricted)
async def get_contract(
    ocid: str,
    db: AsyncSession = Depends(get_db),
    _: User = require_permission(Permission.READ_NAMED),
):
    result = await db.execute(select(Contract).where(Contract.ocid == ocid))
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


# ── Risk score ────────────────────────────────────────────────────────────────

@router.get("/{ocid}/risk", response_model=RiskScoreOut)
async def get_risk_score(
    ocid: str,
    db: AsyncSession = Depends(get_db),
    _: User = require_permission(Permission.READ_NAMED),
):
    result = await db.execute(select(RiskScore).where(RiskScore.contract_ocid == ocid))
    rs = result.scalar_one_or_none()
    if not rs:
        raise HTTPException(status_code=404, detail="Risk score not yet computed for this contract")
    return RiskScoreOut(
        contract_ocid=rs.contract_ocid,
        score=rs.score,
        normalised_score=rs.normalised_score,
        tier=risk_tier(rs.normalised_score),
        flag_count=rs.flag_count,
        applicable_max=rs.applicable_max,
        weights_version=rs.weights_version,
        breakdown=rs.breakdown,
        computed_at=rs.computed_at,
    )


# ── Check results ─────────────────────────────────────────────────────────────

@router.get("/{ocid}/checks", response_model=list[CheckResultOut])
async def get_contract_checks(
    ocid: str,
    db: AsyncSession = Depends(get_db),
    _: User = require_permission(Permission.READ_NAMED),
):
    # Verify contract exists
    c_result = await db.execute(select(Contract.ocid).where(Contract.ocid == ocid))
    if not c_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Contract not found")

    result = await db.execute(
        select(AnomalyFlag)
        .where(AnomalyFlag.contract_ocid == ocid)
        .order_by(AnomalyFlag.check_id)
    )
    flags = result.scalars().all()
    return [
        CheckResultOut(
            check_id=f.check_id,
            check_key=f.check.key if f.check else str(f.check_id),
            result=f.result,
            evidence_note=f.evidence_note,
            weight_applied=f.weight_applied,
        )
        for f in flags
    ]
