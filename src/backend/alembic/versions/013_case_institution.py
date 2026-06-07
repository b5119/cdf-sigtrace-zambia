"""Case institution ownership + escalation routing

Adds owner_institution and escalated_to to cases so the oversight console is
institution-segregated (OAG / ACC / ZPPA) and escalations route to a receiving institution.

Revision ID: 013_case_institution
Revises: 012_inc018_audit
Create Date: 2026-06-07
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "013_case_institution"
down_revision: Union[str, None] = "012_inc018_audit"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("cases", sa.Column("owner_institution", sa.String(20), nullable=True))
    op.add_column("cases", sa.Column("escalated_to", sa.String(20), nullable=True))
    op.create_index("ix_cases_owner_institution", "cases", ["owner_institution"])
    op.create_index("ix_cases_escalated_to", "cases", ["escalated_to"])


def downgrade() -> None:
    op.drop_index("ix_cases_escalated_to", table_name="cases")
    op.drop_index("ix_cases_owner_institution", table_name="cases")
    op.drop_column("cases", "escalated_to")
    op.drop_column("cases", "owner_institution")
