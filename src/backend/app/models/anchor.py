"""AnchorRecord model (INC-006)."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AnchorRecord(Base):
    """Immutable ledger anchor: stores the SHA-256 hash written to Hyperledger Fabric."""
    __tablename__ = "anchor_records"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    contract_ocid: Mapped[str] = mapped_column(
        String(200), ForeignKey("contracts.ocid", ondelete="CASCADE"),
        nullable=False, index=True
    )
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    ledger: Mapped[str] = mapped_column(String(50), nullable=False, default="fabric")
    ledger_tx: Mapped[str | None] = mapped_column(String(200))   # Fabric transaction ID
    block_ref: Mapped[str | None] = mapped_column(String(100))   # block number / channel@block
    anchored_by: Mapped[str | None] = mapped_column(String(36))  # user ID who triggered anchor
    anchored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    # mock flag — set True when Fabric was unavailable; cleared when real anchor is later confirmed
    is_mock: Mapped[bool] = mapped_column(default=False)
