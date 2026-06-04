"""AuditLog model — append-only, periodically anchored (INC-018)."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AuditLog(Base):
    """Append-only record of every privileged action.

    Entries are never updated or deleted. A periodic batch of entries is
    hashed (SHA-256) and the batch hash is anchored to Hyperledger Fabric,
    making the audit trail tamper-evident: altering any past entry would
    change the batch hash and break the on-chain anchor.
    """
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_id: Mapped[str | None] = mapped_column(String(36), index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str | None] = mapped_column(String(50))
    target_ref: Mapped[str | None] = mapped_column(String(200))
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
    # Set once the entry is included in an anchored batch (tamper-evidence)
    anchor_hash: Mapped[str | None] = mapped_column(String(64))
    anchor_tx: Mapped[str | None] = mapped_column(String(200))
