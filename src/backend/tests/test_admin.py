"""Tests for the admin console (INC-017).

Key acceptance: admin can change a weight and see the score recompute;
thresholds editable; users manageable; health reflects component status.
"""
import uuid
from datetime import date

import pytest
import pytest_asyncio

from tests.conftest import bearer, make_role, make_user


@pytest_asyncio.fixture
async def admin(db):
    role = await make_role(db, "system_admin", "System Admin",
                           ["read_public", "read_named", "system_admin", "manage_users",
                            "configure_weights", "ledger_governance"])
    return await make_user(db, role, email="admin_console@oag.gov.zm", password="AdminPass123!")


@pytest_asyncio.fixture
async def officer(db):
    role = await make_role(db, "oversight_officer", "Officer", ["read_named", "case_mgmt"])
    return await make_user(db, role, email="officer_admin@oag.gov.zm", password="Officer123!")


async def _seed_check_definitions(db):
    """Seed the 8 check definitions if not present (admin reads/updates them)."""
    from app.models.anomaly import CheckDefinition
    from sqlalchemy import select
    existing = await db.execute(select(CheckDefinition))
    if existing.scalars().first():
        return
    seeds = [
        (1, "signing", "Signing", 15.0), (2, "standstill", "Standstill", 20.0),
        (3, "time_gap", "Time gap", 15.0), (4, "forensics", "Forensics", 15.0),
        (5, "supplier_net", "Supplier net", 10.0), (6, "score_var", "Score var", 5.0),
        (7, "amendment", "Amendment", 10.0), (8, "debarment", "Debarment", 10.0),
    ]
    for cid, key, name, w in seeds:
        db.add(CheckDefinition(id=cid, key=key, name=name, basis="test",
                               severity="high", weight=w, enabled=True))
    await db.commit()


# ── Health ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_requires_admin(client, officer):
    r = await client.get("/api/v1/admin/health", headers=bearer(officer))
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_health_reports_components(client, admin):
    r = await client.get("/api/v1/admin/health", headers=bearer(admin))
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in ("ok", "degraded")
    assert body["components"]["database"] == "ok"
    assert "fabric" in body["components"]
    assert "polygon" in body["components"]
    assert "ipfs" in body["components"]


@pytest.mark.asyncio
async def test_ledger_status(client, admin):
    r = await client.get("/api/v1/admin/ledger/nodes", headers=bearer(admin))
    assert r.status_code == 200
    body = r.json()
    assert body["fabric"]["mode"] == "mock"
    assert body["polygon"]["mode"] == "mock"


# ── Weights — change a weight and see the score recompute ─────────────────────

@pytest.mark.asyncio
async def test_get_weights(client, admin, db):
    await _seed_check_definitions(db)
    r = await client.get("/api/v1/admin/config/weights", headers=bearer(admin))
    assert r.status_code == 200
    weights = r.json()["weights"]
    assert len(weights) == 8
    assert any(w["key"] == "signing" for w in weights)


@pytest.mark.asyncio
async def test_update_weight_persists(client, admin, db):
    await _seed_check_definitions(db)
    r = await client.put("/api/v1/admin/config/weights",
                         json={"weights": {"signing": 30.0}}, headers=bearer(admin))
    assert r.status_code == 200
    weights = {w["key"]: w["weight"] for w in r.json()["weights"]}
    assert weights["signing"] == 30.0


@pytest.mark.asyncio
async def test_changing_weight_recomputes_score(client, admin, db):
    """THE key acceptance: change a weight → contract score recomputes."""
    await _seed_check_definitions(db)
    from app.models.contract import Contract, Supplier
    from app.services.scoring_service import score_contract

    # Seed a contract that flags the signing check (no signing date)
    supplier = Supplier(id=uuid.uuid4(), name="WSupplier", tpin="5000000001", address="x")
    db.add(supplier)
    await db.flush()
    contract = Contract(ocid="ocds-weight-test", procuring_entity="Min", supplier_id=supplier.id,
                        value=4_876_543.0, currency="ZMW", award_date=date(2024, 1, 1),
                        signing_date=None, status="active", raw_ocds={})
    db.add(contract)
    await db.commit()

    # Score with signing weight = 15
    s1 = await score_contract(db, "ocds-weight-test")
    score_before = s1["score"]

    # Admin raises signing weight to 40
    await client.put("/api/v1/admin/config/weights",
                     json={"weights": {"signing": 40.0}}, headers=bearer(admin))

    # Re-score — the signing flag now contributes more → higher score
    s2 = await score_contract(db, "ocds-weight-test")
    score_after = s2["score"]

    assert score_after != score_before, "Score must change when the weight changes"
    assert score_after > score_before


@pytest.mark.asyncio
async def test_weights_require_configure_permission(client, officer, db):
    await _seed_check_definitions(db)
    r = await client.put("/api/v1/admin/config/weights",
                         json={"weights": {"signing": 30.0}}, headers=bearer(officer))
    assert r.status_code == 403


# ── Thresholds ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_thresholds_defaults(client, admin):
    r = await client.get("/api/v1/admin/config/thresholds", headers=bearer(admin))
    assert r.status_code == 200
    t = r.json()["thresholds"]
    assert t["standstill_days"] == 14


@pytest.mark.asyncio
async def test_update_thresholds(client, admin):
    r = await client.put("/api/v1/admin/config/thresholds",
                         json={"thresholds": {"standstill_days": 21}}, headers=bearer(admin))
    assert r.status_code == 200
    assert r.json()["thresholds"]["standstill_days"] == 21


# ── Users ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_users(client, admin):
    r = await client.get("/api/v1/admin/users", headers=bearer(admin))
    assert r.status_code == 200
    assert r.json()["total"] >= 1


@pytest.mark.asyncio
async def test_create_user(client, admin, db):
    # Ensure the target role exists
    await make_role(db, "analyst", "Analyst", ["read_named"])
    r = await client.post("/api/v1/admin/users",
                          json={"name": "New Analyst", "email": "new_analyst@oag.gov.zm",
                                "password": "NewPassword123", "role_key": "analyst"},
                          headers=bearer(admin))
    assert r.status_code == 201
    assert r.json()["email"] == "new_analyst@oag.gov.zm"
    assert r.json()["role"] == "analyst"


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client, admin):
    r = await client.post("/api/v1/admin/users",
                          json={"name": "Dup", "email": "admin_console@oag.gov.zm",
                                "password": "Password123", "role_key": "system_admin"},
                          headers=bearer(admin))
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_deactivate_user(client, admin, db):
    await make_role(db, "analyst", "Analyst", ["read_named"])
    created = await client.post("/api/v1/admin/users",
                                json={"name": "ToDisable", "email": "todisable@oag.gov.zm",
                                      "password": "Password123", "role_key": "analyst"},
                                headers=bearer(admin))
    uid = created.json()["id"]
    r = await client.patch(f"/api/v1/admin/users/{uid}", json={"active": False}, headers=bearer(admin))
    assert r.status_code == 200
    assert r.json()["active"] is False


@pytest.mark.asyncio
async def test_users_require_manage_permission(client, officer):
    r = await client.get("/api/v1/admin/users", headers=bearer(officer))
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_list_roles(client, admin):
    r = await client.get("/api/v1/admin/roles", headers=bearer(admin))
    assert r.status_code == 200
    assert len(r.json()["roles"]) >= 1
