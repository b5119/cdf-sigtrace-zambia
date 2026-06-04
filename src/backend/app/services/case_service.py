"""Cases & notifications service (INC-016).

Cases open from a contract or a ghost-project signal. Opening, assigning, and
escalating a case fires a notification to the assignee (alerts).
"""
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case, CaseNote, Notification

log = logging.getLogger(__name__)


async def _notify(db: AsyncSession, user_id: str | None, ntype: str, payload: dict) -> None:
    """Fire a notification to a user (no-op if user_id is None)."""
    if not user_id:
        return
    db.add(Notification(id=str(uuid.uuid4()), user_id=user_id, type=ntype, payload=payload))


async def open_case(
    db: AsyncSession, subject_type: str, subject_ref: str, title: str,
    created_by: str, assignee_id: str | None = None, priority: str = "medium",
) -> Case:
    """Open a case from a contract or ghost-project signal; notify the assignee."""
    if subject_type not in ("contract", "ghost_project"):
        raise ValueError("subject_type must be 'contract' or 'ghost_project'")
    case = Case(
        id=str(uuid.uuid4()), subject_type=subject_type, subject_ref=subject_ref,
        title=title, created_by=created_by, assignee_id=assignee_id, priority=priority,
        status="open",
    )
    db.add(case)
    await db.flush()
    await _notify(db, assignee_id, "case_opened",
                  {"case_id": case.id, "title": title, "subject_type": subject_type})
    from app.services.audit_service import log_action
    await log_action(db, created_by, "case_opened", "case", case.id,
                     {"subject_type": subject_type, "subject_ref": subject_ref})
    await db.commit()
    await db.refresh(case)
    log.info("Case %s opened (%s:%s) by %s", case.id, subject_type, subject_ref, created_by)
    return case


async def list_cases(db: AsyncSession, status: str | None = None) -> list[Case]:
    query = select(Case).order_by(Case.created_at.desc())
    if status:
        query = query.where(Case.status == status)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_case(db: AsyncSession, case_id: str) -> Case | None:
    result = await db.execute(select(Case).where(Case.id == case_id))
    return result.scalar_one_or_none()


async def update_case(db: AsyncSession, case_id: str, **fields) -> Case:
    case = await get_case(db, case_id)
    if not case:
        raise ValueError("Case not found")
    for k in ("status", "priority", "assignee_id"):
        if k in fields and fields[k] is not None:
            setattr(case, k, fields[k])
    if fields.get("status") == "closed" and not case.closed_at:
        case.closed_at = datetime.now(timezone.utc)
    # Notify a newly assigned user
    if fields.get("assignee_id"):
        await _notify(db, fields["assignee_id"], "case_assigned",
                      {"case_id": case.id, "title": case.title})
    await db.commit()
    await db.refresh(case)
    return case


async def add_note(db: AsyncSession, case_id: str, author_id: str, body: str) -> CaseNote:
    case = await get_case(db, case_id)
    if not case:
        raise ValueError("Case not found")
    note = CaseNote(id=str(uuid.uuid4()), case_id=case_id, author_id=author_id, body=body)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


async def escalate_case(db: AsyncSession, case_id: str, actor_id: str, target: str = "ACC") -> Case:
    """Escalate a case (e.g. to ACC); fires a notification."""
    case = await get_case(db, case_id)
    if not case:
        raise ValueError("Case not found")
    case.status = "escalated"
    await _notify(db, case.assignee_id or actor_id, "case_escalated",
                  {"case_id": case.id, "title": case.title, "target": target})
    from app.services.audit_service import log_action
    await log_action(db, actor_id, "case_escalated", "case", case.id, {"target": target})
    await db.commit()
    await db.refresh(case)
    log.info("Case %s escalated to %s by %s", case_id, target, actor_id)
    return case


# ── Notifications ──────────────────────────────────────────────────────────────

async def list_notifications(db: AsyncSession, user_id: str, unread_only: bool = False) -> list[Notification]:
    query = select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc())
    if unread_only:
        query = query.where(Notification.read == False)
    result = await db.execute(query)
    return list(result.scalars().all())


async def mark_read(db: AsyncSession, notification_id: str, user_id: str) -> Notification:
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
    )
    n = result.scalar_one_or_none()
    if not n:
        raise ValueError("Notification not found")
    n.read = True
    await db.commit()
    await db.refresh(n)
    return n
