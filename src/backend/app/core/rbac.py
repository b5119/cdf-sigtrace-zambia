"""RBAC: role keys, permission constants, and the require_permission decorator."""
from enum import StrEnum
from functools import wraps
from typing import Callable, List

from fastapi import Depends, HTTPException, status

from app.core.deps import get_current_user
from app.models.user import User


class RoleKey(StrEnum):
    ANONYMOUS = "anonymous"
    COMMUNITY_MONITOR = "community_monitor"
    INST_CONFIRMER = "inst_confirmer"
    OVERSIGHT_OFFICER = "oversight_officer"
    ANALYST = "analyst"
    SYSTEM_ADMIN = "system_admin"


class Permission(StrEnum):
    # Public
    READ_PUBLIC = "read_public"
    VERIFY_DOCUMENT = "verify_document"
    # Restricted reads
    READ_NAMED = "read_named"
    READ_AUDIT = "read_audit"
    # Procurement actions
    ACTION_ANOMALY = "action_anomaly"
    # Field
    CREATE_SUBMISSION = "create_submission"
    CONFIRM_SUBMISSION = "confirm_submission"
    # Ghost-project / integrated monitor
    GHOST_ACTION = "ghost_action"
    # Cases
    CASE_MGMT = "case_mgmt"
    # Admin
    MANAGE_USERS = "manage_users"
    CONFIGURE_WEIGHTS = "configure_weights"
    LEDGER_GOVERNANCE = "ledger_governance"
    SYSTEM_ADMIN = "system_admin"


# The full permission set for each role (data mirror of 05_RBAC_SECURITY.md)
ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    RoleKey.ANONYMOUS: {
        Permission.READ_PUBLIC,
        Permission.VERIFY_DOCUMENT,
    },
    RoleKey.COMMUNITY_MONITOR: {
        Permission.READ_PUBLIC,
        Permission.VERIFY_DOCUMENT,
        Permission.CREATE_SUBMISSION,
    },
    RoleKey.INST_CONFIRMER: {
        Permission.READ_PUBLIC,
        Permission.VERIFY_DOCUMENT,
        Permission.READ_NAMED,
        Permission.CONFIRM_SUBMISSION,
        Permission.GHOST_ACTION,
    },
    RoleKey.OVERSIGHT_OFFICER: {
        Permission.READ_PUBLIC,
        Permission.VERIFY_DOCUMENT,
        Permission.READ_NAMED,
        Permission.READ_AUDIT,
        Permission.ACTION_ANOMALY,
        Permission.CONFIRM_SUBMISSION,
        Permission.GHOST_ACTION,
        Permission.CASE_MGMT,
    },
    RoleKey.ANALYST: {
        Permission.READ_PUBLIC,
        Permission.VERIFY_DOCUMENT,
        Permission.READ_NAMED,
        Permission.READ_AUDIT,
    },
    RoleKey.SYSTEM_ADMIN: {
        Permission.READ_PUBLIC,
        Permission.VERIFY_DOCUMENT,
        Permission.READ_NAMED,
        Permission.READ_AUDIT,
        Permission.ACTION_ANOMALY,
        Permission.CONFIRM_SUBMISSION,
        Permission.GHOST_ACTION,
        Permission.CASE_MGMT,
        Permission.MANAGE_USERS,
        Permission.CONFIGURE_WEIGHTS,
        Permission.LEDGER_GOVERNANCE,
        Permission.SYSTEM_ADMIN,
    },
}


def has_permission(role_key: str, permission: Permission) -> bool:
    perms = ROLE_PERMISSIONS.get(role_key, set())
    return permission in perms


def require_permission(*permissions: Permission):
    """FastAPI dependency that asserts the current user holds ALL listed permissions."""
    async def dependency(current_user: User = Depends(get_current_user)):
        for perm in permissions:
            if not has_permission(current_user.role.key, perm):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {perm}",
                )
        return current_user

    return Depends(dependency)
