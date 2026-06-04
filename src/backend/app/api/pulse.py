"""CDF Pulse API — /api/v1/pulse/* (INC-010).

Community monitors capture field evidence offline; the PWA queues submissions
and syncs them here. Exactly-once via client_uuid idempotency.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.rbac import Permission, require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.pulse import (
    AssignmentProject,
    AssignmentsResponse,
    SubmissionCreate,
    SubmissionListResponse,
    SubmissionOut,
    SyncBatch,
    SyncResult,
)
from app.services import pulse_service

router = APIRouter(prefix="/pulse", tags=["pulse"])

# Seed assignment data for the prototype (real assignments come from admin in INC-017)
_SEED_PROJECTS = [
    {"id": "proj-001", "title": "Borehole Drilling — Ward 3", "category": "Water", "status": "active"},
    {"id": "proj-002", "title": "Community Health Post", "category": "Health", "status": "active"},
    {"id": "proj-003", "title": "Market Stall Construction", "category": "Economic", "status": "active"},
    {"id": "proj-004", "title": "Solar Electrification — School", "category": "Energy", "status": "active"},
]
_SEED_CONSTITUENCY = {"id": "LPV-002", "name": "Milenge"}


@router.get("/assignments", response_model=AssignmentsResponse)
async def get_assignments(
    current_user: User = require_permission(Permission.CREATE_SUBMISSION),
):
    """M2 — the monitor's assigned constituency + project list."""
    projects = [
        AssignmentProject(
            id=p["id"], title=p["title"], category=p["category"], status=p["status"],
            constituency_id=_SEED_CONSTITUENCY["id"],
            constituency_name=_SEED_CONSTITUENCY["name"],
        )
        for p in _SEED_PROJECTS
    ]
    return AssignmentsResponse(
        constituency_id=_SEED_CONSTITUENCY["id"],
        constituency_name=_SEED_CONSTITUENCY["name"],
        projects=projects,
    )


@router.post("/submissions", response_model=SubmissionOut, status_code=201)
async def create_submission(
    body: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.CREATE_SUBMISSION),
):
    """M3/M4 — create a single submission (idempotent on client_uuid)."""
    submission, created = await pulse_service.create_submission(db, str(current_user.id), body)
    await db.commit()
    await db.refresh(submission)
    return submission


@router.post("/sync", response_model=SyncResult)
async def sync_submissions(
    body: SyncBatch,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.CREATE_SUBMISSION),
):
    """M5 — batch-sync queued offline submissions. Exactly-once per client_uuid."""
    result = await pulse_service.sync_batch(db, str(current_user.id), body)
    return SyncResult(
        synced=result["synced"],
        duplicates=result["duplicates"],
        submissions=result["submissions"],
    )


@router.get("/submissions", response_model=SubmissionListResponse)
async def list_submissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """M5 — list submissions. Monitors see only their own; officers see scoped set."""
    from app.core.rbac import has_permission
    is_officer = has_permission(current_user.role.key, Permission.READ_NAMED)
    monitor_filter = None if is_officer else str(current_user.id)
    subs = await pulse_service.list_submissions(db, monitor_filter)
    return SubmissionListResponse(submissions=subs, total=len(subs))


@router.get("/submissions/{submission_id}", response_model=SubmissionOut)
async def get_submission(
    submission_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """M6 — submission detail. Monitor can only see their own."""
    from app.core.rbac import has_permission
    sub = await pulse_service.get_submission(db, submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    is_officer = has_permission(current_user.role.key, Permission.READ_NAMED)
    if not is_officer and sub.monitor_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not your submission")
    return sub
