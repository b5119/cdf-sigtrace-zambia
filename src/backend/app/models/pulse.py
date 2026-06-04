"""PulseSubmission model — field evidence capture (INC-010)."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PulseSubmission(Base):
    """A GPS-tagged field evidence submission from a community monitor.

    IPFS CID is populated at INC-011; on-chain tx at INC-012. For INC-010 the
    submission is captured offline, queued, and synced exactly-once via the
    Idempotency-Key (stored as client_uuid).
    """
    __tablename__ = "pulse_submissions"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # Client-generated UUID for offline de-dup (exactly-once sync)
    client_uuid: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    constituency_id: Mapped[str | None] = mapped_column(String(50))
    # monitor_id is PII — restricted, off-chain
    monitor_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    ipfs_cid: Mapped[str | None] = mapped_column(String(100))  # INC-011
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100))
    note: Mapped[str | None] = mapped_column(Text)

    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/confirmed/rejected
    onchain_tx: Mapped[str | None] = mapped_column(String(200))  # INC-012
