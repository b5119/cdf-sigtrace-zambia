"""Integrated monitor API — /api/v1/monitor/* (INC-015).

Disbursement <-> contract <-> verified-completion matching. A disbursement
with no verified completion within the window appears in the ghost queue.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import Permission, require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.monitor import (
    ClearSignalRequest,
    ClearSignalResponse,
    DisbursementListResponse,
    GhostQueueResponse,
    MonitorRunRequest,
    MonitorRunResponse,
)
from app.services import monitor_service

router = APIRouter(prefix="/monitor", tags=["monitor"])


@router.get("/ghost-projects", response_model=GhostQueueResponse)
async def ghost_projects(
    state: str = "open",
    db: AsyncSession = Depends(get_db),
    _: User = require_permission(Permission.READ_NAMED),
):
    """O6 — the ghost-project queue: disbursements with no verified completion."""
    signals = await monitor_service.get_ghost_queue(db, state)
    return GhostQueueResponse(total=len(signals), signals=signals)


@router.get("/disbursements", response_model=DisbursementListResponse)
async def disbursements(
    db: AsyncSession = Depends(get_db),
    _: User = require_permission(Permission.READ_NAMED),
):
    """O7 — all disbursements + match status."""
    rows = await monitor_service.get_disbursements(db)
    return DisbursementListResponse(total=len(rows), disbursements=rows)


@router.get("/mismatches", response_model=DisbursementListResponse)
async def mismatches(
    db: AsyncSession = Depends(get_db),
    _: User = require_permission(Permission.READ_NAMED),
):
    """O7 — disbursements with no verified completion (the mismatch list)."""
    rows = await monitor_service.get_mismatches(db)
    return DisbursementListResponse(total=len(rows), disbursements=rows)


@router.post("/run", response_model=MonitorRunResponse)
async def run_monitor(
    body: MonitorRunRequest,
    db: AsyncSession = Depends(get_db),
    _: User = require_permission(Permission.SYSTEM_ADMIN),
):
    """Run a monitor sweep (matches disbursements, raises/clears ghost signals)."""
    from datetime import date as _date
    as_of = _date.fromisoformat(body.as_of) if body.as_of else None
    result = await monitor_service.run_sweep(db, as_of)
    return MonitorRunResponse(**result)


@router.post("/ghost-projects/{signal_id}/clear", response_model=ClearSignalResponse)
async def clear_ghost(
    signal_id: str,
    body: ClearSignalRequest,
    db: AsyncSession = Depends(get_db),
    _: User = require_permission(Permission.GHOST_ACTION),
):
    """Clear a ghost signal with a written justification."""
    try:
        result = await monitor_service.clear_ghost_signal(db, signal_id, body.justification)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ClearSignalResponse(**result)
