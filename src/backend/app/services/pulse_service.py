"""Pulse field-evidence service (INC-010).

Core invariant: exactly-once sync. Each submission carries a client-generated
client_uuid. Re-syncing the same submission (offline retry, flaky network) must
NOT create a duplicate — the unique client_uuid is the idempotency key.
"""
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pulse import PulseSubmission

log = logging.getLogger(__name__)


async def create_submission(
    db: AsyncSession,
    monitor_id: str,
    data,  # SubmissionCreate
    mark_synced: bool = True,
) -> tuple[PulseSubmission, bool]:
    """Create one submission idempotently.

    Returns (submission, created) — created=False if the client_uuid already
    existed (idempotent hit, no duplicate written).
    """
    existing = await db.execute(
        select(PulseSubmission).where(PulseSubmission.client_uuid == data.client_uuid)
    )
    found = existing.scalar_one_or_none()
    if found:
        return found, False

    submission = PulseSubmission(
        id=str(uuid.uuid4()),
        client_uuid=data.client_uuid,
        project_id=data.project_id,
        constituency_id=data.constituency_id,
        monitor_id=monitor_id,
        lat=data.lat,
        lng=data.lng,
        category=data.category,
        note=data.note,
        captured_at=data.captured_at,
        synced_at=datetime.now(timezone.utc) if mark_synced else None,
        status="pending",
    )
    db.add(submission)
    await db.flush()
    return submission, True


async def sync_batch(db: AsyncSession, monitor_id: str, batch) -> dict:
    """Sync a batch of queued offline submissions. Idempotent per client_uuid."""
    synced = 0
    duplicates = 0
    results = []
    for sub in batch.submissions:
        submission, created = await create_submission(db, monitor_id, sub, mark_synced=True)
        results.append(submission)
        if created:
            synced += 1
        else:
            duplicates += 1
    await db.commit()
    for s in results:
        await db.refresh(s)
    log.info("Pulse sync for monitor %s: %d new, %d duplicates", monitor_id, synced, duplicates)
    return {"synced": synced, "duplicates": duplicates, "submissions": results}


async def list_submissions(db: AsyncSession, monitor_id: str | None = None) -> list[PulseSubmission]:
    """List submissions. If monitor_id given, scope to that monitor's own submissions."""
    query = select(PulseSubmission).order_by(PulseSubmission.captured_at.desc())
    if monitor_id:
        query = query.where(PulseSubmission.monitor_id == monitor_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_submission(db: AsyncSession, submission_id: str) -> PulseSubmission | None:
    result = await db.execute(select(PulseSubmission).where(PulseSubmission.id == submission_id))
    return result.scalar_one_or_none()
