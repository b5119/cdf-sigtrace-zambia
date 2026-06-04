"""Tests for IPFS evidence storage (INC-011).

Core acceptance criterion: a photo pins to IPFS and altering the file changes
the CID — tamper-evidence demonstrated.
"""
import io
import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio

from app.services.ipfs_client import MockIPFSClient, compute_cid, get_ipfs_client
from app.services.ipfs_service import verify_cid
from tests.conftest import bearer, make_role, make_user


IMG_A = b"\xff\xd8\xff\xe0" + b"genuine field photo bytes - borehole completed" + b"\xff\xd9"
IMG_B = b"\xff\xd8\xff\xe0" + b"genuine field photo bytes - borehole completeD" + b"\xff\xd9"  # 1 byte diff


@pytest_asyncio.fixture(autouse=True)
def reset_ipfs():
    c = get_ipfs_client()
    if isinstance(c, MockIPFSClient):
        c.clear()
    yield
    if isinstance(c, MockIPFSClient):
        c.clear()


@pytest_asyncio.fixture
async def monitor(db):
    role = await make_role(db, "community_monitor", "Community Monitor",
                           ["read_public", "create_submission"])
    return await make_user(db, role, email="monitor_ipfs@cdf.zm", password="Monitor123!")


def _submission_json(cu: str, project="proj-ipfs"):
    return {
        "client_uuid": cu, "project_id": project, "constituency_id": "LPV-002",
        "lat": -11.43, "lng": 29.45, "category": "Borehole",
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }


# ── CID computation (the tamper-evidence primitive) ───────────────────────────

def test_cid_is_deterministic():
    assert compute_cid(IMG_A) == compute_cid(IMG_A)


def test_cid_format_is_cidv1_raw():
    """Raw-codec CIDv1 + sha2-256 + base32 starts with 'bafkrei'."""
    cid = compute_cid(IMG_A)
    assert cid.startswith("bafkrei")
    assert len(cid) == 59  # standard length for raw CIDv1 base32


def test_altering_one_byte_changes_cid():
    """THE key tamper-evidence property."""
    cid_a = compute_cid(IMG_A)
    cid_b = compute_cid(IMG_B)
    assert cid_a != cid_b


def test_verify_cid_matches_original():
    cid = compute_cid(IMG_A)
    assert verify_cid(cid, IMG_A) is True


def test_verify_cid_rejects_altered():
    cid = compute_cid(IMG_A)
    assert verify_cid(cid, IMG_B) is False


# ── Mock client round-trip ────────────────────────────────────────────────────

def test_mock_add_and_cat():
    c = MockIPFSClient()
    cid = c.add(IMG_A)
    assert c.cat(cid) == IMG_A


def test_mock_add_same_bytes_same_cid():
    c = MockIPFSClient()
    assert c.add(IMG_A) == c.add(IMG_A)


def test_mock_cat_unknown_cid_returns_none():
    c = MockIPFSClient()
    assert c.cat("bafkreiunknown") is None


# ── API: pin photo → store CID ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_upload_photo_pins_and_stores_cid(client, monitor):
    created = await client.post("/api/v1/pulse/submissions",
                                json=_submission_json("ipfs-cu-0001"), headers=bearer(monitor))
    sub_id = created.json()["id"]

    r = await client.post(
        f"/api/v1/pulse/submissions/{sub_id}/photo",
        files={"file": ("evidence.jpg", io.BytesIO(IMG_A), "image/jpeg")},
        headers=bearer(monitor),
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ipfs_cid"] is not None
    assert body["ipfs_cid"] == compute_cid(IMG_A)


@pytest.mark.asyncio
async def test_upload_photo_rejects_non_image(client, monitor):
    created = await client.post("/api/v1/pulse/submissions",
                                json=_submission_json("ipfs-cu-0002"), headers=bearer(monitor))
    sub_id = created.json()["id"]
    r = await client.post(
        f"/api/v1/pulse/submissions/{sub_id}/photo",
        files={"file": ("notes.txt", io.BytesIO(b"not an image"), "text/plain")},
        headers=bearer(monitor),
    )
    assert r.status_code == 415


@pytest.mark.asyncio
async def test_upload_photo_rejects_empty(client, monitor):
    created = await client.post("/api/v1/pulse/submissions",
                                json=_submission_json("ipfs-cu-0003"), headers=bearer(monitor))
    sub_id = created.json()["id"]
    r = await client.post(
        f"/api/v1/pulse/submissions/{sub_id}/photo",
        files={"file": ("empty.jpg", io.BytesIO(b""), "image/jpeg")},
        headers=bearer(monitor),
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_upload_photo_forbidden_for_other_monitor(client, db):
    role = await make_role(db, "community_monitor", "Community Monitor",
                           ["read_public", "create_submission"])
    owner = await make_user(db, role, email="owner_ipfs@cdf.zm", password="Pass12345!")
    other = await make_user(db, role, email="other_ipfs@cdf.zm", password="Pass12345!")
    created = await client.post("/api/v1/pulse/submissions",
                                json=_submission_json("ipfs-cu-0004"), headers=bearer(owner))
    sub_id = created.json()["id"]
    r = await client.post(
        f"/api/v1/pulse/submissions/{sub_id}/photo",
        files={"file": ("e.jpg", io.BytesIO(IMG_A), "image/jpeg")},
        headers=bearer(other),
    )
    assert r.status_code == 403


# ── API: retrieve photo ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_retrieve_photo_round_trip(client, monitor):
    created = await client.post("/api/v1/pulse/submissions",
                                json=_submission_json("ipfs-cu-0005"), headers=bearer(monitor))
    sub_id = created.json()["id"]
    await client.post(
        f"/api/v1/pulse/submissions/{sub_id}/photo",
        files={"file": ("e.jpg", io.BytesIO(IMG_A), "image/jpeg")},
        headers=bearer(monitor),
    )
    r = await client.get(f"/api/v1/pulse/submissions/{sub_id}/photo", headers=bearer(monitor))
    assert r.status_code == 200
    assert r.content == IMG_A
    assert r.headers.get("X-IPFS-CID") == compute_cid(IMG_A)


@pytest.mark.asyncio
async def test_retrieve_photo_404_when_none_pinned(client, monitor):
    created = await client.post("/api/v1/pulse/submissions",
                                json=_submission_json("ipfs-cu-0006"), headers=bearer(monitor))
    sub_id = created.json()["id"]
    r = await client.get(f"/api/v1/pulse/submissions/{sub_id}/photo", headers=bearer(monitor))
    assert r.status_code == 404


# ── API: project evidence list ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_project_evidence_lists_pinned_only(client, monitor):
    # One submission with a photo, one without
    s1 = await client.post("/api/v1/pulse/submissions",
                           json=_submission_json("ipfs-ev-0001", project="proj-evidence"), headers=bearer(monitor))
    await client.post("/api/v1/pulse/submissions",
                      json=_submission_json("ipfs-ev-0002", project="proj-evidence"), headers=bearer(monitor))
    s1_id = s1.json()["id"]
    await client.post(
        f"/api/v1/pulse/submissions/{s1_id}/photo",
        files={"file": ("e.jpg", io.BytesIO(IMG_A), "image/jpeg")},
        headers=bearer(monitor),
    )
    r = await client.get("/api/v1/pulse/projects/proj-evidence/evidence", headers=bearer(monitor))
    assert r.status_code == 200
    body = r.json()
    # Only the submission with a pinned photo appears as evidence
    assert body["total"] == 1
    assert body["submissions"][0]["ipfs_cid"] == compute_cid(IMG_A)
