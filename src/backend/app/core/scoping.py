"""Two-tier data scoping: strip PII/named fields for non-restricted callers.

The scoping layer is applied at the schema/serialisation level. This module provides
helper functions that are called from response schemas (via model_validator or explicit
call in route handlers) to project the right tier based on the caller's role.
"""
from typing import Any

from app.core.rbac import Permission, ROLE_PERMISSIONS

# Fields that must never appear in a public-tier response
_PUBLIC_STRIP_FIELDS = frozenset(
    {
        "supplier_name",
        "supplier_tpin",
        "supplier_address",
        "supplier_phone",
        "supplier_shareholders",
        "procuring_entity",
        "monitor_id",
        "monitor_name",
        "confirmer_id",
        "confirmer_name",
        "assignee_id",
        "assignee_name",
        "actor_id",
        "actor_name",
        # user PII
        "name",
        "email",
        "password_hash",
        "mfa_secret",
    }
)


def is_restricted(role_key: str) -> bool:
    """True if the role can see named/PII data."""
    return Permission.READ_NAMED in ROLE_PERMISSIONS.get(role_key, set())


def apply_public_projection(data: dict[str, Any]) -> dict[str, Any]:
    """Remove any named/PII field from a dict before sending to a public caller."""
    return {k: v for k, v in data.items() if k not in _PUBLIC_STRIP_FIELDS}


def scope_response(data: dict[str, Any], role_key: str) -> dict[str, Any]:
    """Apply the correct tier projection based on the caller's role."""
    if is_restricted(role_key):
        return data
    return apply_public_projection(data)
