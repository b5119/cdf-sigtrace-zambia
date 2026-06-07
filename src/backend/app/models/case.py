"""Case, CaseNote, and Notification models (INC-016)."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Case(Base):
    """An oversight case opened from a contract or a ghost-project signal."""
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    subject_type: Mapped[str] = mapped_column(String(20), nullable=False)  # contract / ghost_project
    subject_ref: Mapped[str] = mapped_column(String(200), nullable=False)  # ocid or signal id
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    assignee_id: Mapped[str | None] = mapped_column(String(36), index=True)
    status: Mapped[str] = mapped_column(String(20), default="open")        # open / in_review / escalated / closed
    priority: Mapped[str] = mapped_column(String(10), default="medium")    # low / medium / high
    owner_institution: Mapped[str | None] = mapped_column(String(20), index=True)   # OAG / ACC / ZPPA — institution that owns the case
    escalated_to: Mapped[str | None] = mapped_column(String(20), index=True)        # institution the case is escalated to
    created_by: Mapped[str] = mapped_column(String(36), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    notes: Mapped[list["CaseNote"]] = relationship(
        "CaseNote", back_populates="case", cascade="all, delete-orphan", lazy="selectin"
    )


class CaseNote(Base):
    __tablename__ = "case_notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[str] = mapped_column(String(36), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    case: Mapped["Case"] = relationship("Case", back_populates="notes")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # case_opened / case_escalated / high_risk / ghost_signal
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
