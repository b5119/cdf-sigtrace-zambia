"""RiskScore model — stores the computed score and per-check breakdown (INC-005)."""
import hashlib
import json
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class RiskScore(Base):
    __tablename__ = "risk_scores"

    contract_ocid: Mapped[str] = mapped_column(
        String(200), ForeignKey("contracts.ocid", ondelete="CASCADE"), primary_key=True
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)          # 0-100 absolute
    normalised_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-100 vs applicable max
    breakdown: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    flag_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    applicable_max: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    weights_version: Mapped[str] = mapped_column(String(16), nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
