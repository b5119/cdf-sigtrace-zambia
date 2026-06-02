"""INC-002: OCDS ingestion — Contract, Supplier, IngestionRun tables

Revision ID: 002_inc002_ocds_ingestion
Revises: 001_inc001_auth_rbac
Create Date: 2026-06-02
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, UUID
from alembic import op

revision: str = "002_inc002_ocds_ingestion"
down_revision: Union[str, None] = "001_inc001_auth_rbac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "suppliers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("tpin", sa.String(50), nullable=True),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("shareholders", JSON, nullable=True),
        sa.Column("debarred_until", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_suppliers_tpin", "suppliers", ["tpin"])

    op.create_table(
        "contracts",
        sa.Column("ocid", sa.String(200), primary_key=True),
        sa.Column("procuring_entity", sa.String(500), nullable=False),
        sa.Column("supplier_id", UUID(as_uuid=True), sa.ForeignKey("suppliers.id"), nullable=True),
        sa.Column("value", sa.Numeric(20, 2), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="ZMW"),
        sa.Column("award_date", sa.Date, nullable=True),
        sa.Column("signing_date", sa.Date, nullable=True),
        sa.Column("signing_doc_ref", sa.String(500), nullable=True),
        sa.Column("framework_parent", sa.String(200), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("risk_score", sa.Integer, nullable=True),
        sa.Column("content_hash", sa.String(64), nullable=True),
        sa.Column("raw_ocds", JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_contracts_content_hash", "contracts", ["content_hash"])
    op.create_index("ix_contracts_status", "contracts", ["status"])
    op.create_index("ix_contracts_procuring_entity", "contracts", ["procuring_entity"])

    op.create_table(
        "ingestion_runs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source", sa.String(500), nullable=False),
        sa.Column("records_in", sa.Integer, nullable=False, server_default="0"),
        sa.Column("records_loaded", sa.Integer, nullable=False, server_default="0"),
        sa.Column("records_updated", sa.Integer, nullable=False, server_default="0"),
        sa.Column("records_skipped", sa.Integer, nullable=False, server_default="0"),
        sa.Column("errors", JSON, nullable=False, server_default="[]"),
        sa.Column("status", sa.String(20), nullable=False, server_default="running"),
    )


def downgrade() -> None:
    op.drop_table("ingestion_runs")
    op.drop_table("contracts")
    op.drop_table("suppliers")
