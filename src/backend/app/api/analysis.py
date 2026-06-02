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
    if body.ocids:
        # Score only the specified contracts
        high = medium = low = flagged = errors = 0
        for ocid in body.ocids:
            try:
                s = await score_contract(db, ocid)
                if s["flag_count"] > 0:
                    flagged += 1
                t = s["tier"]
                if t == "high":
                    high += 1
                elif t == "medium":
                    medium += 1
                else:
                    low += 1
            except Exception:
                errors += 1
        total = len(body.ocids)
    else:
        result = await score_all_contracts(db)
        total = result["total"]
        flagged = result["high_risk"] + result["medium_risk"]
        high = result["high_risk"]
        medium = result["medium_risk"]
        low = result["low_risk"]
        errors = result["errors"]

    return AnalysisRunResponse(
        total=total,
        flagged=flagged,
        high_risk=high,
        medium_risk=medium,
        low_risk=low,
        errors=errors,
    )
