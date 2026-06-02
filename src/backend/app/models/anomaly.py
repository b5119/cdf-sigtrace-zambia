"""CheckDefinition and AnomalyFlag SQLAlchemy models (INC-003)."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CheckDefinition(Base):
    """Configurable metadata for each of the 8 anomaly checks."""
    __tablename__ = "check_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # 1-8 fixed
    key: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    basis: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    flags: Mapped[list["AnomalyFlag"]] = relationship("AnomalyFlag", back_populates="check")


class AnomalyFlag(Base):
    """One check result (flag/ok/skip) for one contract."""
    __tablename__ = "anomaly_flags"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    contract_ocid: Mapped[str] = mapped_column(
        String(200), ForeignKey("contracts.ocid", ondelete="CASCADE"), nullable=False, index=True
    )
    check_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("check_definitions.id"), nullable=False
    )
    result: Mapped[str] = mapped_column(String(10), nullable=False)  # flag/ok/skip
    weight_applied: Mapped[float] = mapped_column(Float, default=0.0)
    evidence_note: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    check: Mapped["CheckDefinition"] = relationship("CheckDefinition", back_populates="flags")
