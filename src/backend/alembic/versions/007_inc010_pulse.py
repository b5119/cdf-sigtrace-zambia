"""INC-010: pulse_submissions table

Revision ID: 007_inc010_pulse
Revises: 006_inc008_constituency
Create Date: 2026-06-04
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007_inc010_pulse"
down_revision: Union[str, None] = "006_inc008_constituency"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pulse_submissions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("client_uuid", sa.String(64), nullable=False),
        sa.Column("project_id", sa.String(36), nullable=False),
        sa.Column("constituency_id", sa.String(50), nullable=True),
        sa.Column("monitor_id", sa.String(36), nullable=False),
        sa.Column("ipfs_cid", sa.String(100), nullable=True),
        sa.Column("lat", sa.Float, nullable=False),
        sa.Column("lng", sa.Float, nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("note", sa.Text, nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("onchain_tx", sa.String(200), nullable=True),
    )
    op.create_index("ix_pulse_client_uuid", "pulse_submissions", ["client_uuid"], unique=True)
    op.create_index("ix_pulse_project_id", "pulse_submissions", ["project_id"])
    op.create_index("ix_pulse_monitor_id", "pulse_submissions", ["monitor_id"])


def downgrade() -> None:
    op.drop_table("pulse_submissions")
