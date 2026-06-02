"""INC-006: anchor_records table

Revision ID: 005_inc006_anchor
Revises: 004_inc005_risk_score
Create Date: 2026-06-02
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005_inc006_anchor"
down_revision: Union[str, None] = "004_inc005_risk_score"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "anchor_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("contract_ocid", sa.String(200),
                  sa.ForeignKey("contracts.ocid", ondelete="CASCADE"), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("ledger", sa.String(50), nullable=False, server_default="fabric"),
        sa.Column("ledger_tx", sa.String(200), nullable=True),
        sa.Column("block_ref", sa.String(100), nullable=True),
        sa.Column("anchored_by", sa.String(36), nullable=True),
        sa.Column("anchored_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("is_mock", sa.Boolean, nullable=False, server_default="false"),
    )
    op.create_index("ix_anchor_records_contract_ocid", "anchor_records", ["contract_ocid"])
    op.create_index("ix_anchor_records_sha256", "anchor_records", ["sha256"])


def downgrade() -> None:
    op.drop_table("anchor_records")
