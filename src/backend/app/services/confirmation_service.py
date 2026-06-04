"""Confirmation workflow service (INC-013).

Wires PulseSubmission confirmation to the Polygon CDFConfirmation contract
(via polygon_client). Enforces the same multi-party guarantees on-chain:
  - N distinct confirmations required before a submission is "confirmed"
  - a single party cannot complete alone (duplicate confirm rejected)
  - the recording monitor cannot self-confirm

On the Nth distinct confirmation the submission status flips to "confirmed"
and the completion tx is stored on the submission.
"""
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.confirmation import Confirmation
from app.models.pulse import PulseSubmission
from app.services.polygon_client import get_polygon_client, submission_key

log = logging.getLogger(__name__)


class ConfirmationError(Exception):
    """Raised on invalid confirmation attempts (maps to 400/409 in the API)."""


async def _ensure_on_chain(client, sub: PulseSubmission) -> None:
    """Record the submission on-chain on first interaction (lazy)."""
    key = submission_key(sub.id)
    if client.confirmation_count(key) == 0 and not client.is_complete(key):
        try:
            client.record_submission(
                key,
                sub.ipfs_cid or "",
                settings.CONFIRMATIONS_REQUIRED,
                monitor=sub.monitor_id,
            )
        except ValueError:
            # Already recorded — fine
            pass


async def confirm_submission(
    db: AsyncSession,
    submission_id: str,
    confirmer_id: str,
    signature: str | None = None,
) -> dict:
    """Record a distinct confirmation on-chain and off-chain.

    Returns a summary dict with the updated submission status, confirmation
    count, completion flag, and the on-chain tx.
    """
    result = await db.execute(select(PulseSubmission).where(PulseSubmission.id == submission_id))
    sub = result.scalar_one_or_none()
    if not sub:
        raise ConfirmationError("Submission not found")
    if sub.status == "rejected":
        raise ConfirmationError("Submission was rejected")

    client = get_polygon_client()
    await _ensure_on_chain(client, sub)
    key = submission_key(sub.id)

    # On-chain confirm enforces distinctness, monitor-self-confirm, completion
    try:
        chain_result = client.confirm(key, confirmer_id)
    except ValueError as e:
        raise ConfirmationError(str(e))

    # Persist the confirmation off-chain (mirror)
    confirmation = Confirmation(
        id=str(uuid.uuid4()),
        submission_id=submission_id,
        confirmer_id=confirmer_id,
        decision="confirm",
        signature=signature,
        onchain_tx=chain_result["tx"],
        confirmed_at=datetime.now(timezone.utc),
    )
    db.add(confirmation)

    if chain_result["complete"]:
        sub.status = "confirmed"
        sub.onchain_tx = chain_result["tx"]

    await db.commit()
    await db.refresh(sub)
    log.info(
        "Confirmation for %s by %s — count=%d complete=%s",
        submission_id, confirmer_id, chain_result["count"], chain_result["complete"],
    )
    return {
        "submission_id": submission_id,
        "status": sub.status,
        "confirmation_count": chain_result["count"],
        "required": settings.CONFIRMATIONS_REQUIRED,
        "complete": chain_result["complete"],
        "onchain_tx": chain_result["tx"],
    }


async def reject_submission(
    db: AsyncSession,
    submission_id: str,
    confirmer_id: str,
    reason: str,
) -> dict:
    """Reject a submission with a reason. Sets status to 'rejected'."""
    result = await db.execute(select(PulseSubmission).where(PulseSubmission.id == submission_id))
    sub = result.scalar_one_or_none()
    if not sub:
        raise ConfirmationError("Submission not found")
    if sub.status == "confirmed":
        raise ConfirmationError("Submission already confirmed")

    confirmation = Confirmation(
        id=str(uuid.uuid4()),
        submission_id=submission_id,
        confirmer_id=confirmer_id,
        decision="reject",
        reason=reason,
        confirmed_at=datetime.now(timezone.utc),
    )
    db.add(confirmation)
    sub.status = "rejected"
    await db.commit()
    await db.refresh(sub)
    log.info("Submission %s rejected by %s: %s", submission_id, confirmer_id, reason)
    return {"submission_id": submission_id, "status": "rejected", "reason": reason}


async def get_confirmations(db: AsyncSession, submission_id: str) -> list[Confirmation]:
    result = await db.execute(
        select(Confirmation)
        .where(Confirmation.submission_id == submission_id)
        .order_by(Confirmation.confirmed_at)
    )
    return list(result.scalars().all())
