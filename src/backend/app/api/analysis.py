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

    Scores synchronously so the result is immediately reflected (no Celery worker
    needed for the prototype/local run). For large-scale production, dispatch to
    Celery instead — but synchronous keeps the admin "change a weight → re-score"
    loop working in any environment.
    """
    high = medium = low = flagged = errors = 0

    if body.ocids:
        for ocid in body.ocids:
            try:
                s = await score_contract(db, ocid)
                if s["flag_count"] > 0:
                    flagged += 1
                tier = s["tier"]
                if tier == "high":
                    high += 1
                elif tier == "medium":
                    medium += 1
                else:
                    low += 1
            except Exception:
                errors += 1
        total = len(body.ocids)
    else:
        result = await score_all_contracts(db)
        total = result["total"]
        high = result["high_risk"]
        medium = result["medium_risk"]
        low = result["low_risk"]
        flagged = high + medium
        errors = result["errors"]

    return AnalysisRunResponse(
        total=total, flagged=flagged, high_risk=high,
        medium_risk=medium, low_risk=low, errors=errors,
    )
