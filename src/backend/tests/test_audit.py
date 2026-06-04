"""Tests for anchored audit logging (INC-018).

Acceptance: every privileged action is logged; the audit batch hash is anchored.
"""
import uuid

import pytest
import pytest_asyncio

from app.services.fabric_client import MockFabricClient, get_fabric_client
from tests.conftest import bearer, make_role, make_user


@pytest_asyncio.fixture(autouse=True)
def reset_fabric():
    c = get_fabric_client()
    if isinstance(c, MockFabricClient):
        c.clear()
    yield


@pytest_asyncio.fixture
async def admin(db):
    role = await make_role(db, "system_admin", "System Admin",
                           ["read_public", "read_named", "read_audit", "system_admin",
                            "manage_users", "configure_weights", "case_mgmt"])
    return await make_user(db, role, email="admin_audit@oag.gov.zm", password="AdminPass123!")


@pytest_asyncio.fixture
async def officer(db):
    role = await make_role(db, "oversight_officer", "Officer",
                           ["read_named", "read_audit", "case_mgmt"])
    return await make_user(db, role, email="officer_audit@oag.gov.zm", password="Officer123!")


# ── Service-level ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_log_action_appends(db):
    from app.services.audit_service import log_action, get_audit
    await log_action(db, "actor-1", "test_action", "thing", "ref-1", {"k": "v"})
    await db.commit()
    entries = await get_audit(db, action="test_action")
    assert len(entries) >= 1
    assert entries[0]["action"] == "test_action"
    assert entries[0]["anchored"] is False


@pytest.mark.asyncio
async def test_batch_hash_deterministic(db):
    from app.services.audit_service import log_action, compute_batch_hash
    from app.models.audit import AuditLog
    from sqlalchemy import select
    await log_action(db, "a", "act1", "t", "r")
    await db.commit()
    result = await db.execute(select(AuditLog).where(AuditLog.anchor_hash.is_(None)))
    entries = list(result.scalars().all())
    h1 = compute_batch_hash(entries)
    h2 = compute_batch_hash(entries)
    assert h1 == h2
    assert len(h1) == 64


@pytest.mark.asyncio
async def test_anchor_batch_stamps_entries(db):
    from app.services.audit_service import log_action, anchor_batch, get_audit
    await log_action(db, "a", "act_to_anchor", "t", "r")
    await db.commit()

    result = await anchor_batch(db)
    assert result["anchored"] >= 1
    assert result["batch_hash"] is not None
    assert len(result["batch_hash"]) == 64
    assert result["anchor_tx"] is not None

    # Entries now show anchored
    entries = await get_audit(db, action="act_to_anchor")
    assert entries[0]["anchored"] is True
    assert entries[0]["anchor_tx"] is not None


@pytest.mark.asyncio
async def test_anchor_batch_idempotent(db):
    """Already-anchored entries are not re-anchored."""
    from app.services.audit_service import log_action, anchor_batch
    await log_action(db, "a", "idem_action", "t", "r")
    await db.commit()

    r1 = await anchor_batch(db)
    assert r1["anchored"] >= 1
    # Second call — nothing new to anchor
    r2 = await anchor_batch(db)
    assert r2["anchored"] == 0


# ── Privileged actions are logged (end-to-end) ────────────────────────────────

@pytest.mark.asyncio
async def test_opening_case_is_audited(client, admin):
    """A privileged action (open case) creates an audit entry."""
    await client.post("/api/v1/cases",
                      json={"subject_type": "contract", "subject_ref": "ocds-audit-1", "title": "Audit case"},
                      headers=bearer(admin))
    r = await client.get("/api/v1/admin/audit?action=case_opened", headers=bearer(admin))
    assert r.status_code == 200
    assert r.json()["total"] >= 1


@pytest.mark.asyncio
async def test_weight_change_is_audited(client, admin, db):
    from app.models.anomaly import CheckDefinition
    from sqlalchemy import select
    existing = await db.execute(select(CheckDefinition).where(CheckDefinition.key == "signing"))
    if existing.scalar_one_or_none() is None:
        db.add(CheckDefinition(id=1, key="signing", name="Signing", basis="t",
                               severity="high", weight=15.0, enabled=True))
        await db.commit()
    await client.put("/api/v1/admin/config/weights",
                     json={"weights": {"signing": 25.0}}, headers=bearer(admin))
    r = await client.get("/api/v1/admin/audit?action=weights_updated", headers=bearer(admin))
    assert r.json()["total"] >= 1


# ── API ───────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_audit_requires_read_audit(client, db):
    role = await make_role(db, "community_monitor", "Monitor", ["read_public", "create_submission"])
    monitor = await make_user(db, role, email="mon_audit@cdf.zm", password="Monitor123!")
    r = await client.get("/api/v1/admin/audit", headers=bearer(monitor))
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_audit_anchor_endpoint(client, admin, db):
    from app.services.audit_service import log_action
    await log_action(db, "a", "endpoint_test", "t", "r")
    await db.commit()
    r = await client.post("/api/v1/admin/audit/anchor", headers=bearer(admin))
    assert r.status_code == 200
    assert r.json()["anchored"] >= 1


@pytest.mark.asyncio
async def test_officer_can_read_audit(client, officer, db):
    from app.services.audit_service import log_action
    await log_action(db, "a", "officer_read", "t", "r")
    await db.commit()
    r = await client.get("/api/v1/admin/audit", headers=bearer(officer))
    assert r.status_code == 200  # officer has read_audit
