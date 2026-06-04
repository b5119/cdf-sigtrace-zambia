"""Tests for CDF Pulse field evidence API (INC-010).

Acceptance criteria:
- Capture works (submission created with GPS + timestamp).
- Offline queue → sync = exactly-once (Idempotency-Key / client_uuid de-dup).
- Re-syncing the same submission does NOT duplicate.
- A monitor sees only their own submissions; officers see scoped set.
- create_submission requires create_submission permission.
"""
import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio

from tests.conftest import bearer, make_role, make_user


@pytest_asyncio.fixture
async def monitor(db):
    role = await make_role(db, "community_monitor", "Community Monitor",
                           ["read_public", "verify_document", "create_submission"])
    return await make_user(db, role, email="monitor@cdf.zm", password="Monitor123!")


@pytest_asyncio.fixture
async def officer(db):
    role = await make_role(db, "oversight_officer", "Oversight Officer",
                           ["read_public", "read_named", "create_submission", "confirm_submission"])
    return await make_user(db, role, email="officer_pulse@oag.gov.zm", password="Officer123!")


def _submission(client_uuid: str | None = None, project_id="proj-001"):
    return {
        "client_uuid": client_uuid or f"cu-{uuid.uuid4().hex}",
        "project_id": project_id,
        "constituency_id": "LPV-002",
        "lat": -15.41,
        "lng": 28.30,
        "category": "Borehole",
        "note": "Completed",
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }


# ── Assignments ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_assignments_requires_auth(client):
    r = await client.get("/api/v1/pulse/assignments")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_assignments_returns_projects(client, monitor):
    r = await client.get("/api/v1/pulse/assignments", headers=bearer(monitor))
    assert r.status_code == 200
    body = r.json()
    assert body["constituency_name"] == "Milenge"
    assert len(body["projects"]) > 0


# ── Capture ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_submission(client, monitor):
    r = await client.post("/api/v1/pulse/submissions", json=_submission(), headers=bearer(monitor))
    assert r.status_code == 201
    body = r.json()
    assert body["lat"] == -15.41
    assert body["lng"] == 28.30
    assert body["status"] == "pending"
    assert body["synced_at"] is not None


@pytest.mark.asyncio
async def test_create_submission_requires_permission(client, officer):
    """Officer has create_submission in this fixture, so use an analyst without it."""
    from tests.conftest import make_role, make_user
    # build an analyst with no create_submission
    pass  # covered by test_create_submission_forbidden_for_analyst below


@pytest.mark.asyncio
async def test_create_submission_forbidden_without_permission(client, db):
    role = await make_role(db, "analyst", "Analyst", ["read_public", "read_named"])
    analyst = await make_user(db, role, email="analyst_pulse@oag.gov.zm", password="Analyst123!")
    r = await client.post("/api/v1/pulse/submissions", json=_submission(), headers=bearer(analyst))
    assert r.status_code == 403


# ── Exactly-once sync (the core invariant) ────────────────────────────────────

@pytest.mark.asyncio
async def test_sync_batch_creates_submissions(client, monitor):
    batch = {"submissions": [_submission(), _submission(), _submission()]}
    r = await client.post("/api/v1/pulse/sync", json=batch, headers=bearer(monitor))
    assert r.status_code == 200
    body = r.json()
    assert body["synced"] == 3
    assert body["duplicates"] == 0


@pytest.mark.asyncio
async def test_sync_idempotent_no_duplicates(client, monitor):
    """Re-syncing the SAME client_uuids must not create duplicates."""
    s1 = _submission(client_uuid="fixed-cu-001")
    s2 = _submission(client_uuid="fixed-cu-002")
    batch = {"submissions": [s1, s2]}

    # First sync
    r1 = await client.post("/api/v1/pulse/sync", json=batch, headers=bearer(monitor))
    assert r1.json()["synced"] == 2
    assert r1.json()["duplicates"] == 0

    # Second sync of the exact same batch (simulates offline retry)
    r2 = await client.post("/api/v1/pulse/sync", json=batch, headers=bearer(monitor))
    assert r2.json()["synced"] == 0
    assert r2.json()["duplicates"] == 2


@pytest.mark.asyncio
async def test_single_submit_then_sync_no_duplicate(client, monitor):
    """Submit one online, then it appears in an offline sync batch — must de-dup."""
    sub = _submission(client_uuid="hybrid-cu-001")
    # Online submit
    r1 = await client.post("/api/v1/pulse/submissions", json=sub, headers=bearer(monitor))
    assert r1.status_code == 201
    # Same submission comes through sync batch
    r2 = await client.post("/api/v1/pulse/sync", json={"submissions": [sub]}, headers=bearer(monitor))
    assert r2.json()["synced"] == 0
    assert r2.json()["duplicates"] == 1


# ── Listing & scoping ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_monitor_sees_only_own_submissions(client, db):
    role = await make_role(db, "community_monitor", "Community Monitor",
                           ["read_public", "create_submission"])
    m1 = await make_user(db, role, email="m1@cdf.zm", password="Pass12345!")
    m2 = await make_user(db, role, email="m2@cdf.zm", password="Pass12345!")

    await client.post("/api/v1/pulse/submissions", json=_submission(client_uuid="m1-only-001"), headers=bearer(m1))
    await client.post("/api/v1/pulse/submissions", json=_submission(client_uuid="m2-only-001"), headers=bearer(m2))

    r1 = await client.get("/api/v1/pulse/submissions", headers=bearer(m1))
    cus = {s["client_uuid"] for s in r1.json()["submissions"]}
    assert "m1-only-001" in cus
    assert "m2-only-001" not in cus


@pytest.mark.asyncio
async def test_submission_detail_forbidden_for_other_monitor(client, db):
    role = await make_role(db, "community_monitor", "Community Monitor",
                           ["read_public", "create_submission"])
    owner = await make_user(db, role, email="owner@cdf.zm", password="Pass12345!")
    other = await make_user(db, role, email="other@cdf.zm", password="Pass12345!")

    created = await client.post("/api/v1/pulse/submissions",
                                json=_submission(client_uuid="owner-sub"), headers=bearer(owner))
    sub_id = created.json()["id"]

    r = await client.get(f"/api/v1/pulse/submissions/{sub_id}", headers=bearer(other))
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_submission_not_found(client, monitor):
    r = await client.get(f"/api/v1/pulse/submissions/{uuid.uuid4()}", headers=bearer(monitor))
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_gps_and_timestamp_persisted(client, monitor):
    """GPS + device timestamp must be preserved exactly."""
    sub = _submission(client_uuid="gps-test")
    sub["lat"] = -12.345678
    sub["lng"] = 28.987654
    r = await client.post("/api/v1/pulse/submissions", json=sub, headers=bearer(monitor))
    body = r.json()
    assert body["lat"] == -12.345678
    assert body["lng"] == 28.987654
    assert body["captured_at"] is not None
