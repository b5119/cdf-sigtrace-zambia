"""Contract, Supplier, IngestionRun SQLAlchemy models (INC-002)."""
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    tpin: Mapped[str | None] = mapped_column(String(50), index=True)
    address: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(50))
    shareholders: Mapped[dict | None] = mapped_column(JSON)
    debarred_until: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    contracts: Mapped[list["Contract"]] = relationship("Contract", back_populates="supplier")


class Contract(Base):
    __tablename__ = "contracts"

    ocid: Mapped[str] = mapped_column(String(200), primary_key=True)
    procuring_entity: Mapped[str] = mapped_column(String(500), nullable=False)
    supplier_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True
    )
    value: Mapped[float | None] = mapped_column(Numeric(20, 2))
    currency: Mapped[str] = mapped_column(String(3), default="ZMW")
    award_date: Mapped[date | None] = mapped_column(Date)
    signing_date: Mapped[date | None] = mapped_column(Date)
    signing_doc_ref: Mapped[str | None] = mapped_column(String(500))
    framework_parent: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="active")  # active/complete/cancelled
    risk_score: Mapped[int | None] = mapped_column(Integer)
    content_hash: Mapped[str | None] = mapped_column(String(64), index=True)  # SHA-256 of raw_ocds for idempotency
    raw_ocds: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    supplier: Mapped["Supplier | None"] = relationship("Supplier", back_populates="contracts")


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source: Mapped[str] = mapped_column(String(500), nullable=False)  # URL or "sample"
    records_in: Mapped[int] = mapped_column(Integer, default=0)
    records_loaded: Mapped[int] = mapped_column(Integer, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, default=0)
    records_skipped: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(20), default="running")  # running/complete/failed
