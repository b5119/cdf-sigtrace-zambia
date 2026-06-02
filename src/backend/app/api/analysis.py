"""Analysis trigger endpoint — POST /api/v1/analysis/run (INC-005)."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import Permission, require_permission
from app.db.session import get_db
from app.models.contract import Contract
from app.models.user import User
from app.schemas.contract import AnalysisRunRequest, AnalysisRunResponse
from app.services.scoring_service import score_contract, score_all_contracts

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/run", response_model=AnalysisRunResponse)
async def run_analysis(
    body: AnalysisRunRequest,
    db: AsyncSession = Depends(get_db),
    _: User = require_permission(Permission.SYSTEM_ADMIN),
):
    """
    Run the anomaly engine + risk scorer over all contracts (or a subset by OCID).
    Synchronous for prototype — Celery async dispatch added at INC-020.
    """
    from app.tasks.analysis_tasks import score_all_task

    target_ocids = body.ocids or None
    score_all_task.delay(target_ocids)

    # Return an immediate summary (counts are best-effort from DB state)
    from sqlalchemy import func, select
    from app.models.contract import Contract
    from app.models.risk import RiskScore

    total_result = await db.execute(select(func.count()).select_from(Contract))
    total = total_result.scalar_one()

    high_result = await db.execute(
        select(func.count()).select_from(RiskScore).where(RiskScore.normalised_score >= 60)
    )
    high = high_result.scalar_one()

    med_result = await db.execute(
        select(func.count()).select_from(RiskScore).where(
            RiskScore.normalised_score >= 30, RiskScore.normalised_score < 60
        )
    )
    medium = med_result.scalar_one()

    flag_result = await db.execute(
        select(func.count()).select_from(RiskScore).where(RiskScore.flag_count > 0)
    )
    flagged = flag_result.scalar_one()

    return AnalysisRunResponse(
        total=total if not target_ocids else len(target_ocids),
        flagged=flagged,
        high_risk=high,
        medium_risk=medium,
        low_risk=total - high - medium,
        errors=0,
    )
