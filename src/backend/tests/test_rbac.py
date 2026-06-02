"""Table-driven RBAC test — asserts every (role × permission) cell from 05_RBAC_SECURITY.md.

This is the key acceptance test for INC-001. It does NOT require a database; it tests
the in-memory ROLE_PERMISSIONS mapping directly.
"""
import pytest

from app.core.rbac import ROLE_PERMISSIONS, Permission, RoleKey, has_permission

# Mirror of the permission matrix in 05_RBAC_SECURITY.md
# Format: (role_key, permission, expected_bool)
MATRIX = [
    # READ_PUBLIC — all roles
    (RoleKey.ANONYMOUS,         Permission.READ_PUBLIC,        True),
    (RoleKey.COMMUNITY_MONITOR, Permission.READ_PUBLIC,        True),
    (RoleKey.INST_CONFIRMER,    Permission.READ_PUBLIC,        True),
    (RoleKey.OVERSIGHT_OFFICER, Permission.READ_PUBLIC,        True),
    (RoleKey.ANALYST,           Permission.READ_PUBLIC,        True),
    (RoleKey.SYSTEM_ADMIN,      Permission.READ_PUBLIC,        True),

    # VERIFY_DOCUMENT — all roles
    (RoleKey.ANONYMOUS,         Permission.VERIFY_DOCUMENT,    True),
    (RoleKey.COMMUNITY_MONITOR, Permission.VERIFY_DOCUMENT,    True),
    (RoleKey.INST_CONFIRMER,    Permission.VERIFY_DOCUMENT,    True),
    (RoleKey.OVERSIGHT_OFFICER, Permission.VERIFY_DOCUMENT,    True),
    (RoleKey.ANALYST,           Permission.VERIFY_DOCUMENT,    True),
    (RoleKey.SYSTEM_ADMIN,      Permission.VERIFY_DOCUMENT,    True),

    # READ_NAMED — restricted roles only
    (RoleKey.ANONYMOUS,         Permission.READ_NAMED,         False),
    (RoleKey.COMMUNITY_MONITOR, Permission.READ_NAMED,         False),
    (RoleKey.INST_CONFIRMER,    Permission.READ_NAMED,         True),
    (RoleKey.OVERSIGHT_OFFICER, Permission.READ_NAMED,         True),
    (RoleKey.ANALYST,           Permission.READ_NAMED,         True),
    (RoleKey.SYSTEM_ADMIN,      Permission.READ_NAMED,         True),

    # ACTION_ANOMALY — officer and admin only
    (RoleKey.ANONYMOUS,         Permission.ACTION_ANOMALY,     False),
    (RoleKey.COMMUNITY_MONITOR, Permission.ACTION_ANOMALY,     False),
    (RoleKey.INST_CONFIRMER,    Permission.ACTION_ANOMALY,     False),
    (RoleKey.OVERSIGHT_OFFICER, Permission.ACTION_ANOMALY,     True),
    (RoleKey.ANALYST,           Permission.ACTION_ANOMALY,     False),
    (RoleKey.SYSTEM_ADMIN,      Permission.ACTION_ANOMALY,     True),

    # CREATE_SUBMISSION — monitor only
    (RoleKey.ANONYMOUS,         Permission.CREATE_SUBMISSION,  False),
    (RoleKey.COMMUNITY_MONITOR, Permission.CREATE_SUBMISSION,  True),
    (RoleKey.INST_CONFIRMER,    Permission.CREATE_SUBMISSION,  False),
    (RoleKey.OVERSIGHT_OFFICER, Permission.CREATE_SUBMISSION,  False),
    (RoleKey.ANALYST,           Permission.CREATE_SUBMISSION,  False),
    (RoleKey.SYSTEM_ADMIN,      Permission.CREATE_SUBMISSION,  False),

    # CONFIRM_SUBMISSION — confirmer, officer, admin
    (RoleKey.ANONYMOUS,         Permission.CONFIRM_SUBMISSION, False),
    (RoleKey.COMMUNITY_MONITOR, Permission.CONFIRM_SUBMISSION, False),
    (RoleKey.INST_CONFIRMER,    Permission.CONFIRM_SUBMISSION, True),
    (RoleKey.OVERSIGHT_OFFICER, Permission.CONFIRM_SUBMISSION, True),
    (RoleKey.ANALYST,           Permission.CONFIRM_SUBMISSION, False),
    (RoleKey.SYSTEM_ADMIN,      Permission.CONFIRM_SUBMISSION, True),

    # GHOST_ACTION — confirmer, officer, admin
    (RoleKey.ANONYMOUS,         Permission.GHOST_ACTION,       False),
    (RoleKey.COMMUNITY_MONITOR, Permission.GHOST_ACTION,       False),
    (RoleKey.INST_CONFIRMER,    Permission.GHOST_ACTION,       True),
    (RoleKey.OVERSIGHT_OFFICER, Permission.GHOST_ACTION,       True),
    (RoleKey.ANALYST,           Permission.GHOST_ACTION,       False),
    (RoleKey.SYSTEM_ADMIN,      Permission.GHOST_ACTION,       True),

    # CASE_MGMT — officer, admin
    (RoleKey.ANONYMOUS,         Permission.CASE_MGMT,          False),
    (RoleKey.COMMUNITY_MONITOR, Permission.CASE_MGMT,          False),
    (RoleKey.INST_CONFIRMER,    Permission.CASE_MGMT,          False),
    (RoleKey.OVERSIGHT_OFFICER, Permission.CASE_MGMT,          True),
    (RoleKey.ANALYST,           Permission.CASE_MGMT,          False),
    (RoleKey.SYSTEM_ADMIN,      Permission.CASE_MGMT,          True),

    # MANAGE_USERS — admin only
    (RoleKey.ANONYMOUS,         Permission.MANAGE_USERS,       False),
    (RoleKey.COMMUNITY_MONITOR, Permission.MANAGE_USERS,       False),
    (RoleKey.INST_CONFIRMER,    Permission.MANAGE_USERS,       False),
    (RoleKey.OVERSIGHT_OFFICER, Permission.MANAGE_USERS,       False),
    (RoleKey.ANALYST,           Permission.MANAGE_USERS,       False),
    (RoleKey.SYSTEM_ADMIN,      Permission.MANAGE_USERS,       True),

    # CONFIGURE_WEIGHTS — admin only
    (RoleKey.ANONYMOUS,         Permission.CONFIGURE_WEIGHTS,  False),
    (RoleKey.COMMUNITY_MONITOR, Permission.CONFIGURE_WEIGHTS,  False),
    (RoleKey.INST_CONFIRMER,    Permission.CONFIGURE_WEIGHTS,  False),
    (RoleKey.OVERSIGHT_OFFICER, Permission.CONFIGURE_WEIGHTS,  False),
    (RoleKey.ANALYST,           Permission.CONFIGURE_WEIGHTS,  False),
    (RoleKey.SYSTEM_ADMIN,      Permission.CONFIGURE_WEIGHTS,  True),

    # LEDGER_GOVERNANCE — admin only
    (RoleKey.ANONYMOUS,         Permission.LEDGER_GOVERNANCE,  False),
    (RoleKey.COMMUNITY_MONITOR, Permission.LEDGER_GOVERNANCE,  False),
    (RoleKey.INST_CONFIRMER,    Permission.LEDGER_GOVERNANCE,  False),
    (RoleKey.OVERSIGHT_OFFICER, Permission.LEDGER_GOVERNANCE,  False),
    (RoleKey.ANALYST,           Permission.LEDGER_GOVERNANCE,  False),
    (RoleKey.SYSTEM_ADMIN,      Permission.LEDGER_GOVERNANCE,  True),

    # READ_AUDIT — officer, analyst, admin
    (RoleKey.ANONYMOUS,         Permission.READ_AUDIT,         False),
    (RoleKey.COMMUNITY_MONITOR, Permission.READ_AUDIT,         False),
    (RoleKey.INST_CONFIRMER,    Permission.READ_AUDIT,         False),
    (RoleKey.OVERSIGHT_OFFICER, Permission.READ_AUDIT,         True),
    (RoleKey.ANALYST,           Permission.READ_AUDIT,         True),
    (RoleKey.SYSTEM_ADMIN,      Permission.READ_AUDIT,         True),
]


@pytest.mark.parametrize("role_key, permission, expected", MATRIX)
def test_rbac_matrix(role_key: str, permission: Permission, expected: bool):
    assert has_permission(role_key, permission) == expected, (
        f"Role '{role_key}' × permission '{permission}': expected {expected}"
    )


def test_all_roles_have_entries():
    for role in RoleKey:
        assert role in ROLE_PERMISSIONS, f"Role '{role}' missing from ROLE_PERMISSIONS"


def test_anonymous_has_no_restricted_perms():
    restricted = {Permission.READ_NAMED, Permission.ACTION_ANOMALY, Permission.MANAGE_USERS}
    anon_perms = ROLE_PERMISSIONS[RoleKey.ANONYMOUS]
    assert anon_perms.isdisjoint(restricted), "Anonymous must not have restricted permissions"
