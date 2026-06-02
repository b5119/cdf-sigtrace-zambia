"""INC-001: Auth, RBAC and user/role model

Revision ID: 001_inc001_auth_rbac
Revises:
Create Date: 2026-06-02
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, UUID
from alembic import op

revision: str = "001_inc001_auth_rbac"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- institutions ---
    op.create_table(
        "institutions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False, unique=True),
        sa.Column("type", sa.String(100), nullable=False),
        sa.Column("data_sharing_agreement_ref", sa.String(500), nullable=True),
    )

    # --- roles ---
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("key", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("permissions", JSON, nullable=False, server_default="[]"),
    )

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column("mfa_secret", sa.String(64), nullable=True),
        sa.Column("mfa_enabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("institution_id", UUID(as_uuid=True), sa.ForeignKey("institutions.id"), nullable=True),
    )

    # --- refresh_tokens ---
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("jti", sa.String(36), nullable=False, unique=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean, nullable=False, server_default="false"),
    )
    op.create_index("ix_refresh_tokens_jti", "refresh_tokens", ["jti"])

    # --- seed the six roles ---
    op.bulk_insert(
        sa.table(
            "roles",
            sa.column("key", sa.String),
            sa.column("name", sa.String),
            sa.column("permissions", JSON),
        ),
        [
            {"key": "anonymous",          "name": "Anonymous",           "permissions": ["read_public", "verify_document"]},
            {"key": "community_monitor",  "name": "Community Monitor",   "permissions": ["read_public", "verify_document", "create_submission"]},
            {"key": "inst_confirmer",     "name": "Institutional Confirmer", "permissions": ["read_public", "verify_document", "read_named", "confirm_submission", "ghost_action"]},
            {"key": "oversight_officer",  "name": "Oversight Officer",   "permissions": ["read_public", "verify_document", "read_named", "read_audit", "action_anomaly", "confirm_submission", "ghost_action", "case_mgmt"]},
            {"key": "analyst",            "name": "Analyst",             "permissions": ["read_public", "verify_document", "read_named", "read_audit"]},
            {"key": "system_admin",       "name": "System Administrator","permissions": ["read_public", "verify_document", "read_named", "read_audit", "action_anomaly", "confirm_submission", "ghost_action", "case_mgmt", "manage_users", "configure_weights", "ledger_governance", "system_admin"]},
        ],
    )


def downgrade() -> None:
    op.drop_table("refresh_tokens")
    op.drop_table("users")
    op.drop_table("roles")
    op.drop_table("institutions")
