"""Confirmation model — multi-party confirmation of field evidence (INC-013)."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Confirmation(Base):
    """One confirmer's confirm/reject decision on a PulseSubmission.

    Mirrors the on-chain CDFConfirmation record. Each (submission, confirmer)
    pair is unique — a confirmer cannot confirm the same submission twice
    (enforced here and on-chain).
    """
    __tablename__ = "confirmations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("pulse_submissions.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    confirmer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    decision: Mapped[str] = mapped_column(String(10), nullable=False)  # confirm / reject
    reason: Mapped[str | None] = mapped_column(Text)                   # for rejections
    signature: Mapped[str | None] = mapped_column(String(200))         # confirmer signature/attestation
    onchain_tx: Mapped[str | None] = mapped_column(String(200))        # Polygon tx of this confirmation
    confirmed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
