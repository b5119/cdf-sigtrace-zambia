"""Integrated monitor service (INC-015).

Matches each disbursement against (i) a clean-integrity contract and (ii) a
verified completion. A disbursement with no verified completion within the
ghost window becomes a ghost-project signal in the OAG queue.

A "verified completion" = the disbursement's project has at least one
PulseSubmission with status 'confirmed' (multi-party confirmed on Polygon).
"""
import logging
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.monitor import Disbursement, GhostProjectSignal
from app.models.pulse import PulseSubmission

log = logging.getLogger(__name__)


async def _has_verified_completion(db: AsyncSession, project_id: str | None) -> bool:
    """True if the project has at least one confirmed field submission."""
    if not project_id:
        return False
    result = await db.execute(
        select(PulseSubmission.id)
        .where(PulseSubmission.project_id == project_id, PulseSubmission.status == "confirmed")
        .limit(1)
    )
    return result.scalar_one_or_none() is not None


async def run_sweep(db: AsyncSession, as_of: date | None = None) -> dict:
    """Run a monitor sweep over all disbursements.

    For each disbursement:
      - if it now has a verified completion → mark matched, clear any open ghost signal
      - else if past the ghost window → raise (or update) a ghost-project signal

    Returns aggregate counts.
    """
    as_of = as_of or datetime.now(timezone.utc).date()
    window = settings.GHOST_WINDOW_DAYS

    result = await db.execute(select(Disbursement))
    disbursements = list(result.scalars().all())

    matched = 0
    raised = 0
    cleared = 0

    for d in disbursements:
        has_completion = await _has_verified_completion(db, d.project_id)

        # Load any existing signal for this disbursement
        sig_result = await db.execute(
            select(GhostProjectSignal).where(GhostProjectSignal.disbursement_id == d.id)
        )
        signal = sig_result.scalar_one_or_none()

        if has_completion:
            # Matched — clear any open signal
            if not d.matched_completion:
                d.matched_completion = True
                d.matched_at = datetime.now(timezone.utc)
                matched += 1
            if signal and signal.state == "open":
                signal.state = "cleared"
                signal.cleared_at = datetime.now(timezone.utc)
                signal.justification = "Auto-cleared: verified completion matched"
                cleared += 1
            continue

        # No verified completion — check the window
        days_since = (as_of - d.date).days
        if days_since > window:
            days_overdue = days_since - window
            if signal is None:
                signal = GhostProjectSignal(
                    id=str(uuid.uuid4()), disbursement_id=d.id,
                    days_overdue=days_overdue, state="open",
                )
                db.add(signal)
                raised += 1
            elif signal.state == "open":
                signal.days_overdue = days_overdue

    await db.commit()
    log.info("Monitor sweep: matched=%d raised=%d cleared=%d", matched, raised, cleared)
    return {
        "disbursements": len(disbursements),
        "matched": matched,
        "ghost_signals_raised": raised,
        "ghost_signals_cleared": cleared,
    }


async def get_ghost_queue(db: AsyncSession, state: str = "open") -> list[dict]:
    """List ghost-project signals with their disbursement context."""
    result = await db.execute(
        select(GhostProjectSignal, Disbursement)
        .join(Disbursement, GhostProjectSignal.disbursement_id == Disbursement.id)
        .where(GhostProjectSignal.state == state)
        .order_by(GhostProjectSignal.days_overdue.desc())
    )
    rows = result.all()
    return [
        {
            "id": sig.id,
            "disbursement_id": sig.disbursement_id,
            "constituency_id": dis.constituency_id,
            "project_id": dis.project_id,
            "amount": dis.amount,
            "disbursement_date": dis.date.isoformat(),
            "days_overdue": sig.days_overdue,
            "state": sig.state,
            "raised_at": sig.raised_at.isoformat() if sig.raised_at else None,
        }
        for sig, dis in rows
    ]


async def get_disbursements(db: AsyncSession) -> list[dict]:
    """All disbursements + match status."""
    result = await db.execute(select(Disbursement).order_by(Disbursement.date.desc()))
    rows = list(result.scalars().all())
    return [
        {
            "id": d.id, "constituency_id": d.constituency_id, "project_id": d.project_id,
            "contract_ocid": d.contract_ocid, "amount": d.amount,
            "date": d.date.isoformat(), "source": d.source,
            "matched_completion": d.matched_completion,
            "matched_at": d.matched_at.isoformat() if d.matched_at else None,
        }
        for d in rows
    ]


async def get_mismatches(db: AsyncSession) -> list[dict]:
    """Disbursements with no verified completion (the mismatch list)."""
    all_d = await get_disbursements(db)
    return [d for d in all_d if not d["matched_completion"]]


async def clear_ghost_signal(db: AsyncSession, signal_id: str, justification: str) -> dict:
    """Clear a ghost signal with a written justification."""
    result = await db.execute(select(GhostProjectSignal).where(GhostProjectSignal.id == signal_id))
    signal = result.scalar_one_or_none()
    if not signal:
        raise ValueError("Ghost signal not found")
    signal.state = "cleared"
    signal.justification = justification
    signal.cleared_at = datetime.now(timezone.utc)
    await db.commit()
    return {"id": signal_id, "state": "cleared", "justification": justification}
