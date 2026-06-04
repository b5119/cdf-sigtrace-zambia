"""INC-013: confirmations table

Revision ID: 008_inc013_confirmation
Revises: 007_inc010_pulse
Create Date: 2026-06-04
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "008_inc013_confirmation"
down_revision: Union[str, None] = "007_inc010_pulse"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "confirmations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("submission_id", sa.String(36),
                  sa.ForeignKey("pulse_submissions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("confirmer_id", sa.String(36), nullable=False),
        sa.Column("decision", sa.String(10), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("signature", sa.String(200), nullable=True),
        sa.Column("onchain_tx", sa.String(200), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_confirmations_submission_id", "confirmations", ["submission_id"])
    op.create_index("ix_confirmations_confirmer_id", "confirmations", ["confirmer_id"])


def downgrade() -> None:
    op.drop_table("confirmations")
