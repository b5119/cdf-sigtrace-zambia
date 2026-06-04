"""INC-017: config table

Revision ID: 011_inc017_config
Revises: 010_inc016_cases
Create Date: 2026-06-04
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON
from alembic import op

revision: str = "011_inc017_config"
down_revision: Union[str, None] = "010_inc016_cases"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "config",
        sa.Column("key", sa.String(50), primary_key=True),
        sa.Column("value", JSON, nullable=False, server_default="{}"),
        sa.Column("updated_by", sa.String(36), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
    )


def downgrade() -> None:
    op.drop_table("config")
