"""Tests for public project evidence (INC-014, P5).

Acceptance criteria:
- Public project page shows evidence, verified location, confirmation status.
- De-identified: NO monitor_id / confirmer identity in any public response.
- Evidence photo retrievable by IPFS CID without auth.
"""
import io
import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio

from app.services.ipfs_client import MockIPFSClient, compute_cid, get_ipfs_client
from app.services.polygon_client import get_polygon_client
from tests.conftest import bearer, make_role, make_user

IMG = b"\xff\xd8\xff\xe0" + b"public evidence photo bytes" + b"\xff\xd9"


@pytest_asyncio.fixture(autouse=True)
def reset_state():
    ic = get_ipfs_client()
    if isinstance(ic, MockIPFSClient):
        ic.clear()
    pc = get_polygon_client()
    if hasattr(pc, "clear"):
        pc.clear()
    yield


@pytest_asyncio.fixture
async def monitor(db):
    role = await make_role(db, "community_monitor", "Community Monitor",
                           ["read_public", "create_submission"])
    return await make_user(db, role, email="mon_p5@cdf.zm", password="Monitor123!")


@pytest_asyncio.fixture
async def confirmer_a(db):
    role = await make_role(db, "inst_confirmer", "Institutional Confirmer",
                           ["read_public", "read_named", "confirm_submission"])
    return await make_user(db, role, email="ca_p5@council.zm", password="Conf12345!")


@pytest_asyncio.fixture
async def confirmer_b(db):
    role = await make_role(db, "inst_confirmer", "Institutional Confirmer",
                           ["read_public", "read_named", "confirm_submission"])
    return await make_user(db, role, email="cb_p5@council.zm", password="Conf12345!")


async def _capture_with_photo(client, monitor, cu, project="proj-p5"):
    body = {"client_uuid": cu, "project_id": project, "constituency_id": "LPV-002",
            "lat": -11.432, "lng": 29.456, "category": "Borehole",
            "captured_at": datetime.now(timezone.utc).isoformat()}
    r = await client.post("/api/v1/pulse/submissions", json=body, headers=bearer(monitor))
    sid = r.json()["id"]
    await client.post(f"/api/v1/pulse/submissions/{sid}/photo",
                      files={"file": ("e.jpg", io.BytesIO(IMG), "image/jpeg")}, headers=bearer(monitor))
    return sid


# ── Project detail ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_project_detail_no_auth(client, monitor):
    await _capture_with_photo(client, monitor, "p5-cu-0001")
    r = await client.get("/api/v1/public/projects/proj-p5")
    assert r.status_code == 200
    body = r.json()
    assert body["project_id"] == "proj-p5"
    assert body["evidence_count"] >= 1
    assert "title" in body
    assert "disbursement_amount" in body


@pytest.mark.asyncio
async def test_project_detail_verified_location(client, monitor):
    await _capture_with_photo(client, monitor, "p5-cu-0002")
    r = await client.get("/api/v1/public/projects/proj-p5")
    body = r.json()
    assert body["location"] is not None
    assert abs(body["location"]["lat"] - (-11.432)) < 0.01
    assert abs(body["location"]["lng"] - 29.456) < 0.01


@pytest.mark.asyncio
async def test_project_verified_after_confirmation(client, monitor, confirmer_a, confirmer_b):
    sid = await _capture_with_photo(client, monitor, "p5-cu-0003", project="proj-verified")
    # Two distinct confirmations → confirmed
    await client.post(f"/api/v1/pulse/submissions/{sid}/confirm", json={}, headers=bearer(confirmer_a))
    await client.post(f"/api/v1/pulse/submissions/{sid}/confirm", json={}, headers=bearer(confirmer_b))

    r = await client.get("/api/v1/public/projects/proj-verified")
    body = r.json()
    assert body["verified"] is True
    assert body["confirmed_count"] == 1
    assert body["status"] == "completed"


# ── Evidence list — DE-IDENTIFIED ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_evidence_list_no_auth(client, monitor):
    await _capture_with_photo(client, monitor, "p5-cu-0004", project="proj-evlist")
    r = await client.get("/api/v1/public/projects/proj-evlist/evidence")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    assert body["evidence"][0]["ipfs_cid"] == compute_cid(IMG)


@pytest.mark.asyncio
async def test_evidence_has_no_monitor_identity(client, monitor):
    """CRITICAL two-tier rule: public evidence must NOT expose monitor_id."""
    await _capture_with_photo(client, monitor, "p5-cu-0005", project="proj-deident")
    r = await client.get("/api/v1/public/projects/proj-deident/evidence")
    body_str = r.text
    assert "monitor_id" not in body_str
    assert str(monitor.id) not in body_str
    # The evidence items must carry status + confirmation_count + location, but no identity
    item = r.json()["evidence"][0]
    assert "monitor_id" not in item
    assert "status" in item
    assert "confirmation_count" in item
    assert "lat" in item and "lng" in item


@pytest.mark.asyncio
async def test_evidence_shows_confirmation_status(client, monitor, confirmer_a, confirmer_b):
    sid = await _capture_with_photo(client, monitor, "p5-cu-0006", project="proj-confstatus")
    await client.post(f"/api/v1/pulse/submissions/{sid}/confirm", json={}, headers=bearer(confirmer_a))
    await client.post(f"/api/v1/pulse/submissions/{sid}/confirm", json={}, headers=bearer(confirmer_b))

    r = await client.get("/api/v1/public/projects/proj-confstatus/evidence")
    item = r.json()["evidence"][0]
    assert item["status"] == "confirmed"
    assert item["confirmation_count"] == 2
    assert item["onchain_tx"] is not None


@pytest.mark.asyncio
async def test_evidence_empty_for_unknown_project(client):
    r = await client.get("/api/v1/public/projects/no-such-project/evidence")
    assert r.status_code == 200
    assert r.json()["total"] == 0


# ── Evidence photo by CID ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_evidence_photo_by_cid_no_auth(client, monitor):
    await _capture_with_photo(client, monitor, "p5-cu-0007", project="proj-photo")
    cid = compute_cid(IMG)
    r = await client.get(f"/api/v1/public/evidence/{cid}")
    assert r.status_code == 200
    assert r.content == IMG
    assert r.headers.get("X-IPFS-CID") == cid


@pytest.mark.asyncio
async def test_evidence_photo_unknown_cid_404(client):
    r = await client.get("/api/v1/public/evidence/bafkreiunknowncid")
    assert r.status_code == 404
