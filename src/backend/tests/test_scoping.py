"""Tests for two-tier data scoping (INC-001).

Verifies that public callers receive no named/PII fields while restricted callers
receive the full projection. This is the scoping correctness test required by the
architecture (05_RBAC_SECURITY.md §4 and 10_TESTING.md).
"""
import pytest

from app.core.scoping import apply_public_projection, is_restricted, scope_response
from app.core.rbac import RoleKey


FULL_RECORD = {
    "ocid": "ocds-abc-001",
    "risk_score": 72,
    "procuring_entity": "Ministry of Health",       # named — must be stripped for public
    "supplier_name": "Acme Construction Ltd",        # named
    "supplier_tpin": "1234567890",                   # PII
    "supplier_address": "Plot 123, Lusaka",          # PII
    "value": 5_000_000,
    "award_date": "2025-01-15",
}


def test_restricted_roles_see_all_fields():
    for role in [RoleKey.OVERSIGHT_OFFICER, RoleKey.ANALYST, RoleKey.SYSTEM_ADMIN, RoleKey.INST_CONFIRMER]:
        result = scope_response(FULL_RECORD, role)
        assert result["procuring_entity"] == "Ministry of Health"
        assert result["supplier_name"] == "Acme Construction Ltd"
        assert result["supplier_tpin"] == "1234567890"


def test_public_projection_strips_named_fields():
    result = apply_public_projection(FULL_RECORD)
    assert "procuring_entity" not in result
    assert "supplier_name" not in result
    assert "supplier_tpin" not in result
    assert "supplier_address" not in result
    # Non-PII fields must survive
    assert result["ocid"] == "ocds-abc-001"
    assert result["risk_score"] == 72
    assert result["value"] == 5_000_000


def test_anonymous_scope_strips_pii():
    result = scope_response(FULL_RECORD, RoleKey.ANONYMOUS)
    assert "supplier_name" not in result
    assert "procuring_entity" not in result
    assert result["risk_score"] == 72


def test_monitor_scope_strips_pii():
    # community_monitor does not have READ_NAMED
    result = scope_response(FULL_RECORD, RoleKey.COMMUNITY_MONITOR)
    assert "supplier_name" not in result


def test_is_restricted():
    assert is_restricted(RoleKey.OVERSIGHT_OFFICER)
    assert is_restricted(RoleKey.ANALYST)
    assert is_restricted(RoleKey.SYSTEM_ADMIN)
    assert is_restricted(RoleKey.INST_CONFIRMER)
    assert not is_restricted(RoleKey.ANONYMOUS)
    assert not is_restricted(RoleKey.COMMUNITY_MONITOR)
