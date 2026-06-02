"""INC-005: risk_scores table

Revision ID: 004_inc005_risk_score
Revises: 003_inc003_anomaly_checks
Create Date: 2026-06-02
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON
from alembic import op

revision: str = "004_inc005_risk_score"
down_revision: Union[str, None] = "003_inc003_anomaly_checks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "risk_scores",
        sa.Column("contract_ocid", sa.String(200),
                  sa.ForeignKey("contracts.ocid", ondelete="CASCADE"), primary_key=True),
        sa.Column("score", sa.Integer, nullable=False),
        sa.Column("normalised_score", sa.Integer, nullable=False),
        sa.Column("breakdown", JSON, nullable=False, server_default="{}"),
        sa.Column("flag_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("applicable_max", sa.Float, nullable=False, server_default="0"),
        sa.Column("weights_version", sa.String(16), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("risk_scores")
