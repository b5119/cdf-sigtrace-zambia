"""CDF Pulse API — /api/v1/pulse/* (INC-010 + INC-011).

Community monitors capture field evidence offline; the PWA queues submissions
and syncs them here. Exactly-once via client_uuid idempotency.
INC-011 adds IPFS photo pinning + evidence retrieval (content-addressed CID).
"""
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_current_user
from app.core.rbac import Permission, has_permission, require_permission
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
from app.services import ipfs_service, pulse_service

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


# ── INC-011: IPFS evidence ─────────────────────────────────────────────────────

_MAX_PHOTO_BYTES = settings.IPFS_MAX_PHOTO_MB * 1024 * 1024


@router.post("/submissions/{submission_id}/photo", response_model=SubmissionOut)
async def upload_photo(
    submission_id: str,
    file: UploadFile = File(..., description="Field evidence photo"),
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.CREATE_SUBMISSION),
):
    """Pin a field-evidence photo to IPFS and store its content-addressed CID.

    Only the owning monitor may attach a photo. Re-uploading the same bytes
    yields the same CID (content-addressed, idempotent).
    """
    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Only image files are accepted")

    data = await file.read()
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(data) > _MAX_PHOTO_BYTES:
        raise HTTPException(status_code=413, detail=f"Photo exceeds {settings.IPFS_MAX_PHOTO_MB} MB")

    sub = await pulse_service.get_submission(db, submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    if sub.monitor_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not your submission")

    try:
        updated = await ipfs_service.pin_submission_photo(db, submission_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return updated


@router.get("/submissions/{submission_id}/photo")
async def get_photo(
    submission_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve the pinned evidence photo bytes from IPFS by the submission's CID."""
    sub = await pulse_service.get_submission(db, submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    is_officer = has_permission(current_user.role.key, Permission.READ_NAMED)
    if not is_officer and sub.monitor_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not your submission")
    if not sub.ipfs_cid:
        raise HTTPException(status_code=404, detail="No photo pinned for this submission")

    data = ipfs_service.retrieve_photo(sub.ipfs_cid)
    if data is None:
        raise HTTPException(status_code=404, detail="Photo not found on IPFS")
    return Response(content=data, media_type="image/jpeg",
                    headers={"X-IPFS-CID": sub.ipfs_cid})


@router.get("/projects/{project_id}/evidence", response_model=SubmissionListResponse)
async def project_evidence(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List evidence (submissions with pinned photos) for a project."""
    subs = await ipfs_service.get_project_evidence(db, project_id)
    return SubmissionListResponse(submissions=subs, total=len(subs))
