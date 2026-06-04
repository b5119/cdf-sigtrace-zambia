"""Cases & notifications API — /api/v1/cases/*, /notifications/* (INC-016)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.rbac import Permission, require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.case import (
    CaseCreate, CaseListResponse, CaseNoteOut, CaseOut, CaseUpdate,
    EscalateRequest, NoteCreate, NotificationListResponse, NotificationOut,
)
from app.services import case_service

router = APIRouter(tags=["cases"])


@router.get("/cases", response_model=CaseListResponse)
async def list_cases(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = require_permission(Permission.CASE_MGMT),
):
    cases = await case_service.list_cases(db, status)
    return CaseListResponse(total=len(cases), cases=cases)


@router.post("/cases", response_model=CaseOut, status_code=201)
async def create_case(
    body: CaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.CASE_MGMT),
):
    """Open a case from a contract or a ghost-project signal (fires notification)."""
    try:
        case = await case_service.open_case(
            db, body.subject_type, body.subject_ref, body.title,
            created_by=str(current_user.id),
            assignee_id=body.assignee_id or str(current_user.id),
            priority=body.priority,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return case


@router.get("/cases/{case_id}", response_model=CaseOut)
async def get_case(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = require_permission(Permission.CASE_MGMT),
):
    case = await case_service.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.patch("/cases/{case_id}", response_model=CaseOut)
async def update_case(
    case_id: str, body: CaseUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = require_permission(Permission.CASE_MGMT),
):
    try:
        case = await case_service.update_case(db, case_id, **body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return case


@router.post("/cases/{case_id}/notes", response_model=CaseNoteOut, status_code=201)
async def add_note(
    case_id: str, body: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.CASE_MGMT),
):
    try:
        note = await case_service.add_note(db, case_id, str(current_user.id), body.body)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return note


@router.post("/cases/{case_id}/escalate", response_model=CaseOut)
async def escalate_case(
    case_id: str, body: EscalateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.CASE_MGMT),
):
    try:
        case = await case_service.escalate_case(db, case_id, str(current_user.id), body.target)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return case


# ── Notifications ──────────────────────────────────────────────────────────────

@router.get("/notifications", response_model=NotificationListResponse)
async def list_notifications(
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notes = await case_service.list_notifications(db, str(current_user.id), unread_only)
    unread = sum(1 for n in notes if not n.read)
    return NotificationListResponse(total=len(notes), unread=unread, notifications=notes)


@router.post("/notifications/{notification_id}/read", response_model=NotificationOut)
async def mark_notification_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        n = await case_service.mark_read(db, notification_id, str(current_user.id))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return n
