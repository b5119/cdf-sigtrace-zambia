"""Ingestion management endpoints (INC-002) — /api/v1/ingestion/runs"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import Permission, require_permission
from app.db.session import get_db
from app.models.contract import IngestionRun
from app.schemas.ingestion import IngestionRunListResponse, IngestionRunOut, TriggerRunRequest

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.get("/runs", response_model=IngestionRunListResponse)
async def list_runs(
    page: int = 1,
    size: int = 20,
    db: AsyncSession = Depends(get_db),
    _: None = require_permission(Permission.SYSTEM_ADMIN),
):
    """List ingestion run history (most recent first)."""
    offset = (page - 1) * size
    result = await db.execute(
        select(IngestionRun).order_by(IngestionRun.started_at.desc()).offset(offset).limit(size)
    )
    runs = result.scalars().all()
    count_result = await db.execute(select(func.count()).select_from(IngestionRun))
    total = count_result.scalar_one()
    return IngestionRunListResponse(runs=list(runs), total=total)


@router.post("/runs", response_model=IngestionRunOut, status_code=status.HTTP_202_ACCEPTED)
async def trigger_run(
    body: TriggerRunRequest,
    db: AsyncSession = Depends(get_db),
    _: None = require_permission(Permission.SYSTEM_ADMIN),
):
    """Trigger an ingestion run asynchronously. Returns the run record immediately."""
    run = IngestionRun(
        id=uuid.uuid4(),
        source=body.source,
        status="running",
        started_at=datetime.now(timezone.utc),
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    # Dispatch async Celery task — worker executes the pipeline
    from app.tasks.ingestion_tasks import run_ingestion
    run_ingestion.delay(str(run.id), body.source, body.since)

    return run


@router.get("/runs/{run_id}", response_model=IngestionRunOut)
async def get_run(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: None = require_permission(Permission.SYSTEM_ADMIN),
):
    """Get detail for a specific ingestion run."""
    result = await db.execute(select(IngestionRun).where(IngestionRun.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
