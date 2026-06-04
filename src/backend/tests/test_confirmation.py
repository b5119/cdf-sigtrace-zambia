"""Tests for the confirmation workflow (INC-013).

Wires PulseSubmission confirmation to the Polygon mock. Asserts the multi-party
guarantee end-to-end through the API:
  - N distinct confirmations required before 'confirmed'
  - a single party cannot complete alone (duplicate confirm → 409)
  - monitor cannot self-confirm
  - reject sets status to 'rejected'
"""
import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio

from app.services.polygon_client import get_polygon_client
from tests.conftest import bearer, make_role, make_user


@pytest_asyncio.fixture(autouse=True)
def reset_chain():
    c = get_polygon_client()
    if hasattr(c, "clear"):
        c.clear()
    yield
    if hasattr(c, "clear"):
        c.clear()


@pytest_asyncio.fixture
async def monitor(db):
    role = await make_role(db, "community_monitor", "Community Monitor",
                           ["read_public", "create_submission"])
    return await make_user(db, role, email="mon_conf@cdf.zm", password="Monitor123!")


@pytest_asyncio.fixture
async def confirmer_a(db):
    role = await make_role(db, "inst_confirmer", "Institutional Confirmer",
                           ["read_public", "read_named", "confirm_submission"])
    return await make_user(db, role, email="conf_a@council.zm", password="Conf12345!")


@pytest_asyncio.fixture
async def confirmer_b(db):
    role = await make_role(db, "inst_confirmer", "Institutional Confirmer",
                           ["read_public", "read_named", "confirm_submission"])
    return await make_user(db, role, email="conf_b@council.zm", password="Conf12345!")


async def _make_submission(client, monitor, cu: str) -> str:
    body = {
        "client_uuid": cu, "project_id": "proj-conf", "constituency_id": "LPV-002",
        "lat": -11.43, "lng": 29.45, "category": "Borehole",
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }
    r = await client.post("/api/v1/pulse/submissions", json=body, headers=bearer(monitor))
    return r.json()["id"]


# ── Multi-party confirmation ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_confirm_requires_permission(client, monitor):
    sub_id = await _make_submission(client, monitor, "conf-cu-0001")
    # Monitor lacks confirm_submission permission
    r = await client.post(f"/api/v1/pulse/submissions/{sub_id}/confirm", json={}, headers=bearer(monitor))
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_first_confirmation_does_not_complete(client, monitor, confirmer_a):
    sub_id = await _make_submission(client, monitor, "conf-cu-0002")
    r = await client.post(f"/api/v1/pulse/submissions/{sub_id}/confirm", json={}, headers=bearer(confirmer_a))
    assert r.status_code == 200
    body = r.json()
    assert body["confirmation_count"] == 1
    assert body["complete"] is False
    assert body["status"] == "pending"
    assert body["onchain_tx"] is not None


@pytest.mark.asyncio
async def test_second_distinct_confirmation_completes(client, monitor, confirmer_a, confirmer_b):
    sub_id = await _make_submission(client, monitor, "conf-cu-0003")
    await client.post(f"/api/v1/pulse/submissions/{sub_id}/confirm", json={}, headers=bearer(confirmer_a))
    r = await client.post(f"/api/v1/pulse/submissions/{sub_id}/confirm", json={}, headers=bearer(confirmer_b))
    body = r.json()
    assert body["confirmation_count"] == 2
    assert body["complete"] is True
    assert body["status"] == "confirmed"


@pytest.mark.asyncio
async def test_single_party_cannot_complete_alone(client, monitor, confirmer_a):
    """Same confirmer confirming twice → 409, submission stays pending."""
    sub_id = await _make_submission(client, monitor, "conf-cu-0004")
    await client.post(f"/api/v1/pulse/submissions/{sub_id}/confirm", json={}, headers=bearer(confirmer_a))
    r2 = await client.post(f"/api/v1/pulse/submissions/{sub_id}/confirm", json={}, headers=bearer(confirmer_a))
    assert r2.status_code == 409
    # Verify still pending
    detail = await client.get(f"/api/v1/pulse/submissions/{sub_id}", headers=bearer(confirmer_a))
    assert detail.json()["status"] == "pending"


@pytest.mark.asyncio
async def test_monitor_cannot_self_confirm(client, db, confirmer_a):
    """The recording monitor cannot confirm their own submission.

    Canonical roles separate capture (monitor) from confirm (confirmer), so we
    construct a submission whose monitor_id IS the confirmer, then have that same
    confirmer attempt to confirm — the on-chain self-confirm guard must reject it.
    """
    from app.models.pulse import PulseSubmission
    sub = PulseSubmission(
        id=str(uuid.uuid4()), client_uuid="self-confirm-001", project_id="proj-conf",
        constituency_id="LPV-002", monitor_id=str(confirmer_a.id),
        lat=-11.43, lng=29.45, captured_at=datetime.now(timezone.utc), status="pending",
    )
    db.add(sub)
    await db.commit()

    r = await client.post(f"/api/v1/pulse/submissions/{sub.id}/confirm", json={}, headers=bearer(confirmer_a))
    assert r.status_code == 400
    assert "self-confirm" in r.json()["detail"]


@pytest.mark.asyncio
async def test_confirm_unknown_submission(client, confirmer_a):
    r = await client.post(f"/api/v1/pulse/submissions/{uuid.uuid4()}/confirm", json={}, headers=bearer(confirmer_a))
    assert r.status_code == 404


# ── Rejection ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_reject_submission(client, monitor, confirmer_a):
    sub_id = await _make_submission(client, monitor, "conf-cu-0006")
    r = await client.post(f"/api/v1/pulse/submissions/{sub_id}/reject",
                          json={"reason": "Photo does not match project location"},
                          headers=bearer(confirmer_a))
    assert r.status_code == 200
    assert r.json()["status"] == "rejected"


@pytest.mark.asyncio
async def test_cannot_confirm_after_reject(client, monitor, confirmer_a, confirmer_b):
    sub_id = await _make_submission(client, monitor, "conf-cu-0007")
    await client.post(f"/api/v1/pulse/submissions/{sub_id}/reject",
                      json={"reason": "Invalid"}, headers=bearer(confirmer_a))
    r = await client.post(f"/api/v1/pulse/submissions/{sub_id}/confirm", json={}, headers=bearer(confirmer_b))
    assert r.status_code == 400
    assert "rejected" in r.json()["detail"]


@pytest.mark.asyncio
async def test_reject_requires_reason(client, monitor, confirmer_a):
    sub_id = await _make_submission(client, monitor, "conf-cu-0008")
    r = await client.post(f"/api/v1/pulse/submissions/{sub_id}/reject", json={}, headers=bearer(confirmer_a))
    assert r.status_code == 422  # missing required reason


# ── Confirmation list ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_confirmations(client, monitor, confirmer_a, confirmer_b):
    sub_id = await _make_submission(client, monitor, "conf-cu-0009")
    await client.post(f"/api/v1/pulse/submissions/{sub_id}/confirm", json={}, headers=bearer(confirmer_a))
    await client.post(f"/api/v1/pulse/submissions/{sub_id}/confirm", json={}, headers=bearer(confirmer_b))
    r = await client.get(f"/api/v1/pulse/submissions/{sub_id}/confirmations", headers=bearer(confirmer_a))
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    assert all(c["decision"] == "confirm" for c in body["confirmations"])
    assert all(c["onchain_tx"] is not None for c in body["confirmations"])
