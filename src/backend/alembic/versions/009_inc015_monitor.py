"""INC-015: disbursements and ghost_project_signals tables

Revision ID: 009_inc015_monitor
Revises: 008_inc013_confirmation
Create Date: 2026-06-04
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "009_inc015_monitor"
down_revision: Union[str, None] = "008_inc013_confirmation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "disbursements",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("constituency_id", sa.String(50), nullable=True),
        sa.Column("project_id", sa.String(36), nullable=True),
        sa.Column("contract_ocid", sa.String(200), nullable=True),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("source", sa.String(50), nullable=False, server_default="IFMIS"),
        sa.Column("matched_completion", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("matched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_disbursements_constituency_id", "disbursements", ["constituency_id"])
    op.create_index("ix_disbursements_project_id", "disbursements", ["project_id"])

    op.create_table(
        "ghost_project_signals",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("disbursement_id", sa.String(36),
                  sa.ForeignKey("disbursements.id", ondelete="CASCADE"), nullable=False),
        sa.Column("days_overdue", sa.Integer, nullable=False, server_default="0"),
        sa.Column("state", sa.String(20), nullable=False, server_default="open"),
        sa.Column("justification", sa.Text, nullable=True),
        sa.Column("raised_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("cleared_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_ghost_disbursement_id", "ghost_project_signals", ["disbursement_id"])


def downgrade() -> None:
    op.drop_table("ghost_project_signals")
    op.drop_table("disbursements")
