"""IPFS evidence service (INC-011).

Pins field-evidence photos to IPFS, stores the resulting CID on the
PulseSubmission, and retrieves evidence. The photo bytes are content-addressed,
so the stored CID is tamper-evident: any alteration yields a different CID.
"""
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pulse import PulseSubmission
from app.services.ipfs_client import compute_cid, get_ipfs_client

log = logging.getLogger(__name__)


async def pin_submission_photo(
    db: AsyncSession, submission_id: str, photo_bytes: bytes
) -> PulseSubmission:
    """Pin a photo to IPFS and store its CID on the submission.

    Idempotent: re-pinning the same bytes yields the same CID (content-addressed).
    Returns the updated submission.
    """
    result = await db.execute(select(PulseSubmission).where(PulseSubmission.id == submission_id))
    submission = result.scalar_one_or_none()
    if submission is None:
        raise ValueError(f"Submission {submission_id!r} not found")

    client = get_ipfs_client()
    cid = client.add(photo_bytes)

    submission.ipfs_cid = cid
    await db.commit()
    await db.refresh(submission)
    log.info("Pinned photo for submission %s → %s", submission_id, cid)
    return submission


def retrieve_photo(cid: str) -> bytes | None:
    """Fetch photo bytes from IPFS by CID."""
    client = get_ipfs_client()
    return client.cat(cid)


def verify_cid(cid: str, photo_bytes: bytes) -> bool:
    """True if the CID matches the SHA-256 content address of the given bytes.

    This proves tamper-evidence: feeding altered bytes produces a different CID,
    so this returns False.
    """
    return compute_cid(photo_bytes) == cid


async def get_project_evidence(db: AsyncSession, project_id: str) -> list[PulseSubmission]:
    """All submissions for a project that have a pinned photo (evidence)."""
    result = await db.execute(
        select(PulseSubmission)
        .where(PulseSubmission.project_id == project_id, PulseSubmission.ipfs_cid.isnot(None))
        .order_by(PulseSubmission.captured_at.desc())
    )
    return list(result.scalars().all())
