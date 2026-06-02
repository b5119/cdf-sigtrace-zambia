"""INC-003: check_definitions and anomaly_flags tables + seed check metadata

Revision ID: 003_inc003_anomaly_checks
Revises: 002_inc002_ocds_ingestion
Create Date: 2026-06-02
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_inc003_anomaly_checks"
down_revision: Union[str, None] = "002_inc002_ocds_ingestion"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "check_definitions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("key", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("basis", sa.Text, nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("weight", sa.Float, nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default="true"),
    )

    op.create_table(
        "anomaly_flags",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("contract_ocid", sa.String(200),
                  sa.ForeignKey("contracts.ocid", ondelete="CASCADE"), nullable=False),
        sa.Column("check_id", sa.Integer,
                  sa.ForeignKey("check_definitions.id"), nullable=False),
        sa.Column("result", sa.String(10), nullable=False),
        sa.Column("weight_applied", sa.Float, nullable=False, server_default="0"),
        sa.Column("evidence_note", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ix_anomaly_flags_contract_ocid", "anomaly_flags", ["contract_ocid"])

    # Seed the 8 check definitions (INC-003 delivers checks 1-3; 4-8 are stubs)
    op.bulk_insert(
        sa.table(
            "check_definitions",
            sa.column("id", sa.Integer),
            sa.column("key", sa.String),
            sa.column("name", sa.String),
            sa.column("basis", sa.Text),
            sa.column("severity", sa.String),
            sa.column("weight", sa.Float),
            sa.column("enabled", sa.Boolean),
        ),
        [
            {
                "id": 1, "key": "signing", "weight": 15.0, "enabled": True,
                "severity": "high",
                "name": "Missing contract signing date",
                "basis": "Public Procurement Act; e-GP CPMS signing requirement",
            },
            {
                "id": 2, "key": "standstill", "weight": 20.0, "enabled": True,
                "severity": "high",
                "name": "Standstill period violation",
                "basis": "Public Procurement Act §45 — 14-day challenge window post-award",
            },
            {
                "id": 3, "key": "time_gap", "weight": 15.0, "enabled": True,
                "severity": "medium",
                "name": "Suspicious compression of tender timeline",
                "basis": "ZPPA procurement guidelines — mandatory evaluation period",
            },
            {
                "id": 4, "key": "forensics", "weight": 15.0, "enabled": False,
                "severity": "medium",
                "name": "Digital forensics anomaly (metadata/Benford)",
                "basis": "Fraud detection — document metadata inconsistencies",
            },
            {
                "id": 5, "key": "supplier_net", "weight": 10.0, "enabled": False,
                "severity": "medium",
                "name": "Supplier network / related-party link",
                "basis": "Anti-corruption — undisclosed conflicts of interest",
            },
            {
                "id": 6, "key": "score_var", "weight": 5.0, "enabled": False,
                "severity": "low",
                "name": "Evaluation score variance anomaly",
                "basis": "ZPPA evaluation guidelines — bid scoring consistency",
            },
            {
                "id": 7, "key": "amendment", "weight": 10.0, "enabled": False,
                "severity": "medium",
                "name": "Contract amendment exceeds threshold",
                "basis": "Public Procurement Act — amendment cap without re-tender",
            },
            {
                "id": 8, "key": "debarment", "weight": 10.0, "enabled": False,
                "severity": "high",
                "name": "Debarred supplier awarded contract",
                "basis": "ZPPA debarment register — ineligible suppliers",
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("anomaly_flags")
    op.drop_table("check_definitions")
