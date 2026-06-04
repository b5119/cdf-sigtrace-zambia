"""Constituency and Project SQLAlchemy models (INC-008)."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Constituency(Base):
    """CDF electoral constituency — one row per constituency."""
    __tablename__ = "constituencies"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    province: Mapped[str] = mapped_column(String(100), nullable=False)
    geo: Mapped[dict | None] = mapped_column(JSON)          # GeoJSON polygon / centroid
    cdf_allocation: Mapped[float | None] = mapped_column(Float)  # ZMW amount
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    projects: Mapped[list["Project"]] = relationship("Project", back_populates="constituency")


class Project(Base):
    """CDF-funded project within a constituency."""
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    constituency_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("constituencies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "infrastructure"
    status: Mapped[str] = mapped_column(String(30), default="ongoing")   # ongoing/completed/stalled
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    constituency: Mapped["Constituency"] = relationship("Constituency", back_populates="projects")
