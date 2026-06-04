"""Disbursement and GhostProjectSignal models — the integrated monitor (INC-015)."""
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Disbursement(Base):
    """A CDF fund disbursement (from IFMIS). The integrated monitor matches each
    disbursement against a clean-integrity contract AND a verified completion."""
    __tablename__ = "disbursements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    constituency_id: Mapped[str | None] = mapped_column(String(50), index=True)
    project_id: Mapped[str | None] = mapped_column(String(36), index=True)
    contract_ocid: Mapped[str | None] = mapped_column(String(200))  # linked clean contract
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="IFMIS")
    matched_completion: Mapped[bool] = mapped_column(Boolean, default=False)
    matched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class GhostProjectSignal(Base):
    """Raised when a disbursement has no verified completion within the window.
    A ghost-project signal goes to the OAG oversight queue."""
    __tablename__ = "ghost_project_signals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    disbursement_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("disbursements.id", ondelete="CASCADE"), nullable=False, index=True
    )
    days_overdue: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    state: Mapped[str] = mapped_column(String(20), default="open")  # open / cleared / escalated
    justification: Mapped[str | None] = mapped_column(Text)
    raised_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    cleared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
