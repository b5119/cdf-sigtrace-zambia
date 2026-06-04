"""Tests for the integrated monitor + ghost queue (INC-015).

Core acceptance criterion:
- A disbursement with no verified completion within the window appears in the
  ghost queue; matching one (a verified completion) clears it.
"""
import uuid
from datetime import date, datetime, timezone, timedelta

import pytest
import pytest_asyncio

from app.models.monitor import Disbursement
from app.models.pulse import PulseSubmission
from tests.conftest import bearer, make_role, make_user


@pytest_asyncio.fixture
async def officer(db):
    role = await make_role(db, "oversight_officer", "Oversight Officer",
                           ["read_public", "read_named", "ghost_action"])
    return await make_user(db, role, email="officer_mon@oag.gov.zm", password="Officer123!")


@pytest_asyncio.fixture
async def admin(db):
    role = await make_role(db, "system_admin", "System Admin",
                           ["read_public", "read_named", "system_admin", "ghost_action"])
    return await make_user(db, role, email="admin_mon@oag.gov.zm", password="Admin123!")


async def _add_disbursement(db, project_id, disb_date, did=None):
    d = Disbursement(
        id=did or str(uuid.uuid4()), constituency_id="LPV-002", project_id=project_id,
        contract_ocid="ocds-zm-zppa-001", amount=285_000, date=disb_date, source="IFMIS",
    )
    db.add(d)
    await db.commit()
    return d


async def _add_confirmed_submission(db, project_id):
    sub = PulseSubmission(
        id=str(uuid.uuid4()), client_uuid=f"mon-{uuid.uuid4().hex}", project_id=project_id,
        constituency_id="LPV-002", monitor_id="some-monitor", lat=-11.4, lng=29.4,
        captured_at=datetime.now(timezone.utc), status="confirmed",
    )
    db.add(sub)
    await db.commit()
    return sub


# ── Sweep service ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_old_disbursement_no_completion_raises_ghost(db):
    """A disbursement past the window with no verified completion → ghost signal."""
    from app.services.monitor_service import run_sweep, get_ghost_queue
    old = date(2024, 1, 1)  # well past 180-day window relative to as_of
    await _add_disbursement(db, "proj-ghost-1", old)

    result = await run_sweep(db, as_of=date(2025, 1, 1))
    assert result["ghost_signals_raised"] == 1

    queue = await get_ghost_queue(db)
    assert len(queue) == 1
    assert queue[0]["project_id"] == "proj-ghost-1"
    assert queue[0]["days_overdue"] > 0


@pytest.mark.asyncio
async def test_recent_disbursement_within_window_no_ghost(db):
    """A disbursement still within the window → no ghost signal yet."""
    from app.services.monitor_service import run_sweep, get_ghost_queue
    recent = date(2024, 12, 1)
    await _add_disbursement(db, "proj-recent-1", recent)

    result = await run_sweep(db, as_of=date(2025, 1, 1))  # ~31 days < 180
    assert result["ghost_signals_raised"] == 0
    queue = await get_ghost_queue(db)
    assert all(q["project_id"] != "proj-recent-1" for q in queue)


@pytest.mark.asyncio
async def test_disbursement_with_completion_no_ghost(db):
    """A disbursement WITH a verified completion → matched, no ghost."""
    from app.services.monitor_service import run_sweep
    old = date(2024, 1, 1)
    await _add_disbursement(db, "proj-matched-1", old)
    await _add_confirmed_submission(db, "proj-matched-1")

    result = await run_sweep(db, as_of=date(2025, 1, 1))
    assert result["matched"] == 1
    assert result["ghost_signals_raised"] == 0


@pytest.mark.asyncio
async def test_matching_clears_existing_ghost(db):
    """THE key criterion: a ghost signal clears once a verified completion appears.

    Assertions are scoped to this test's own project (the session-shared DB
    accumulates disbursements from other tests, so the global count is not used).
    """
    from app.services.monitor_service import run_sweep, get_ghost_queue
    old = date(2024, 1, 1)
    await _add_disbursement(db, "proj-clears-1", old)

    # First sweep — raises a ghost for proj-clears-1
    await run_sweep(db, as_of=date(2025, 1, 1))
    queue = await get_ghost_queue(db)
    assert any(q["project_id"] == "proj-clears-1" for q in queue), "ghost should be raised"

    # Verified completion arrives
    await _add_confirmed_submission(db, "proj-clears-1")

    # Second sweep — clears the ghost for proj-clears-1
    await run_sweep(db, as_of=date(2025, 1, 1))
    queue_after = await get_ghost_queue(db)
    assert all(q["project_id"] != "proj-clears-1" for q in queue_after), "ghost should be cleared"


# ── API ───────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ghost_queue_requires_auth(client):
    r = await client.get("/api/v1/monitor/ghost-projects")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_run_requires_admin(client, officer):
    r = await client.post("/api/v1/monitor/run", json={}, headers=bearer(officer))
    assert r.status_code == 403  # officer lacks system_admin


@pytest.mark.asyncio
async def test_run_and_view_ghost_queue(client, db, admin):
    await _add_disbursement(db, "proj-api-ghost", date(2024, 1, 1), did="disb-api-1")
    r = await client.post("/api/v1/monitor/run", json={"as_of": "2025-01-01"}, headers=bearer(admin))
    assert r.status_code == 200
    assert r.json()["ghost_signals_raised"] >= 1

    q = await client.get("/api/v1/monitor/ghost-projects", headers=bearer(admin))
    assert q.status_code == 200
    assert q.json()["total"] >= 1


@pytest.mark.asyncio
async def test_clear_ghost_signal_via_api(client, db, admin, officer):
    await _add_disbursement(db, "proj-api-clear", date(2024, 1, 1), did="disb-api-2")
    await client.post("/api/v1/monitor/run", json={"as_of": "2025-01-01"}, headers=bearer(admin))

    q = await client.get("/api/v1/monitor/ghost-projects", headers=bearer(admin))
    signal = next(s for s in q.json()["signals"] if s["disbursement_id"] == "disb-api-2")

    r = await client.post(f"/api/v1/monitor/ghost-projects/{signal['id']}/clear",
                          json={"justification": "Completion verified offline by field officer"},
                          headers=bearer(officer))
    assert r.status_code == 200
    assert r.json()["state"] == "cleared"


@pytest.mark.asyncio
async def test_clear_requires_justification(client, db, admin, officer):
    await _add_disbursement(db, "proj-api-nj", date(2024, 1, 1), did="disb-api-3")
    await client.post("/api/v1/monitor/run", json={"as_of": "2025-01-01"}, headers=bearer(admin))
    q = await client.get("/api/v1/monitor/ghost-projects", headers=bearer(admin))
    signal = next(s for s in q.json()["signals"] if s["disbursement_id"] == "disb-api-3")
    r = await client.post(f"/api/v1/monitor/ghost-projects/{signal['id']}/clear",
                          json={}, headers=bearer(officer))
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_disbursements_and_mismatches(client, db, admin):
    await _add_disbursement(db, "proj-mismatch", date(2024, 1, 1), did="disb-mm-1")
    r = await client.get("/api/v1/monitor/disbursements", headers=bearer(admin))
    assert r.status_code == 200
    assert r.json()["total"] >= 1

    mm = await client.get("/api/v1/monitor/mismatches", headers=bearer(admin))
    assert mm.status_code == 200
    # The unmatched disbursement appears in mismatches
    assert any(d["id"] == "disb-mm-1" for d in mm.json()["disbursements"])
