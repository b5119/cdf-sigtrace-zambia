"""Tests for cases & notifications (INC-016).

Acceptance: cases open from a contract or ghost signal; notes/status/escalation
work; alerts (notifications) fire.
"""
import uuid

import pytest
import pytest_asyncio

from tests.conftest import bearer, make_role, make_user


@pytest_asyncio.fixture
async def officer(db):
    role = await make_role(db, "oversight_officer", "Oversight Officer",
                           ["read_public", "read_named", "case_mgmt", "action_anomaly"])
    return await make_user(db, role, email="officer_case@oag.gov.zm", password="Officer123!")


@pytest_asyncio.fixture
async def analyst(db):
    role = await make_role(db, "analyst", "Analyst", ["read_public", "read_named"])
    return await make_user(db, role, email="analyst_case@oag.gov.zm", password="Analyst123!")


def _case_body(subject_type="contract", ref="ocds-zm-zppa-001"):
    return {"subject_type": subject_type, "subject_ref": ref,
            "title": f"Review {ref}", "priority": "high"}


# ── Open cases ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_open_case_from_contract(client, officer):
    r = await client.post("/api/v1/cases", json=_case_body("contract"), headers=bearer(officer))
    assert r.status_code == 201
    body = r.json()
    assert body["subject_type"] == "contract"
    assert body["status"] == "open"
    assert body["priority"] == "high"


@pytest.mark.asyncio
async def test_open_case_from_ghost_project(client, officer):
    r = await client.post("/api/v1/cases", json=_case_body("ghost_project", "signal-123"), headers=bearer(officer))
    assert r.status_code == 201
    assert r.json()["subject_type"] == "ghost_project"


@pytest.mark.asyncio
async def test_open_case_invalid_subject_type(client, officer):
    r = await client.post("/api/v1/cases",
                          json={"subject_type": "invalid", "subject_ref": "x", "title": "t"},
                          headers=bearer(officer))
    assert r.status_code == 422  # pattern validation


@pytest.mark.asyncio
async def test_case_requires_case_mgmt_permission(client, analyst):
    r = await client.post("/api/v1/cases", json=_case_body(), headers=bearer(analyst))
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_list_cases_requires_auth(client):
    r = await client.get("/api/v1/cases")
    assert r.status_code == 401


# ── Notes, status, escalation ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_add_note_to_case(client, officer):
    case = await client.post("/api/v1/cases", json=_case_body(), headers=bearer(officer))
    cid = case.json()["id"]
    r = await client.post(f"/api/v1/cases/{cid}/notes",
                          json={"body": "Contacted procuring entity for clarification"},
                          headers=bearer(officer))
    assert r.status_code == 201
    assert r.json()["body"].startswith("Contacted")

    # Note appears in case detail
    detail = await client.get(f"/api/v1/cases/{cid}", headers=bearer(officer))
    assert len(detail.json()["notes"]) == 1


@pytest.mark.asyncio
async def test_update_case_status(client, officer):
    case = await client.post("/api/v1/cases", json=_case_body(), headers=bearer(officer))
    cid = case.json()["id"]
    r = await client.patch(f"/api/v1/cases/{cid}", json={"status": "in_review"}, headers=bearer(officer))
    assert r.status_code == 200
    assert r.json()["status"] == "in_review"


@pytest.mark.asyncio
async def test_close_case_sets_closed_at(client, officer):
    case = await client.post("/api/v1/cases", json=_case_body(), headers=bearer(officer))
    cid = case.json()["id"]
    r = await client.patch(f"/api/v1/cases/{cid}", json={"status": "closed"}, headers=bearer(officer))
    assert r.json()["status"] == "closed"
    assert r.json()["closed_at"] is not None


@pytest.mark.asyncio
async def test_escalate_case(client, officer):
    case = await client.post("/api/v1/cases", json=_case_body(), headers=bearer(officer))
    cid = case.json()["id"]
    r = await client.post(f"/api/v1/cases/{cid}/escalate", json={"target": "ACC"}, headers=bearer(officer))
    assert r.status_code == 200
    assert r.json()["status"] == "escalated"


@pytest.mark.asyncio
async def test_note_on_unknown_case_404(client, officer):
    r = await client.post(f"/api/v1/cases/{uuid.uuid4()}/notes", json={"body": "x"}, headers=bearer(officer))
    assert r.status_code == 404


# ── Notifications (alerts fire) ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_opening_case_fires_notification(client, officer):
    """Opening a case (self-assigned) creates a notification for the assignee."""
    await client.post("/api/v1/cases", json=_case_body(), headers=bearer(officer))
    r = await client.get("/api/v1/notifications", headers=bearer(officer))
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    assert any(n["type"] == "case_opened" for n in body["notifications"])


@pytest.mark.asyncio
async def test_escalation_fires_notification(client, officer):
    case = await client.post("/api/v1/cases", json=_case_body(), headers=bearer(officer))
    cid = case.json()["id"]
    await client.post(f"/api/v1/cases/{cid}/escalate", json={"target": "ACC"}, headers=bearer(officer))
    r = await client.get("/api/v1/notifications", headers=bearer(officer))
    assert any(n["type"] == "case_escalated" for n in r.json()["notifications"])


@pytest.mark.asyncio
async def test_mark_notification_read(client, officer):
    await client.post("/api/v1/cases", json=_case_body(), headers=bearer(officer))
    notes = await client.get("/api/v1/notifications", headers=bearer(officer))
    nid = notes.json()["notifications"][0]["id"]
    r = await client.post(f"/api/v1/notifications/{nid}/read", headers=bearer(officer))
    assert r.status_code == 200
    assert r.json()["read"] is True


@pytest.mark.asyncio
async def test_notifications_scoped_to_user(client, db, officer):
    """A user only sees their own notifications."""
    other_role = await make_role(db, "oversight_officer", "Officer", ["read_named", "case_mgmt"])
    other = await make_user(db, other_role, email="other_case@oag.gov.zm", password="Other123!")
    # officer opens a case → notification for officer only
    await client.post("/api/v1/cases", json=_case_body("contract", "ocds-unique-xyz"), headers=bearer(officer))
    r = await client.get("/api/v1/notifications", headers=bearer(other))
    # 'other' should not see officer's case_opened notification
    assert all(n["payload"].get("subject_ref") != "ocds-unique-xyz" for n in r.json()["notifications"])


@pytest.mark.asyncio
async def test_notifications_require_auth(client):
    r = await client.get("/api/v1/notifications")
    assert r.status_code == 401
