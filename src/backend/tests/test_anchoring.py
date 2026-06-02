"""Tests for the Fabric anchoring service (INC-006).

Acceptance criteria:
- Anchoring writes a hash to Fabric and stores a record.
- Re-anchoring the same document is idempotent (one record, no second tx).
- A modified document produces a different hash and a new record.
- verify: original → MATCH; modified → MISMATCH; unknown OCID → NOT_REGISTERED.
- Document bytes never leave the anchor service (only hash stored).
- API: POST /anchors requires action_anomaly permission; GET /anchors/{ocid} requires read_named.
- Public anchor endpoint returns hash but no named data.
"""
import io
import uuid
from datetime import date

import pytest
import pytest_asyncio

from app.models.anchor import AnchorRecord
from app.models.contract import Contract, Supplier
from app.services.anchor_service import (
    VerifyVerdict,
    anchor_contract,
    compute_sha256,
    get_anchor_history,
    verify_document,
)
from app.services.fabric_client import MockFabricClient, get_fabric_client
from tests.conftest import bearer, make_role, make_user


# ── Fixtures ───────────────────────────────────────────────────────────────────

SAMPLE_PDF = b"%PDF-1.4 fake contract document content for testing"
MODIFIED_PDF = b"%PDF-1.4 fake contract document content for testing MODIFIED"


@pytest_asyncio.fixture(autouse=True)
def reset_mock_fabric():
    """Clear the in-memory mock store before each test."""
    client = get_fabric_client()
    if isinstance(client, MockFabricClient):
        client.clear()
    yield
    if isinstance(client, MockFabricClient):
        client.clear()


async def _make_contract(db, ocid: str) -> str:
    """Insert a contract with the given OCID (skip if already exists)."""
    from sqlalchemy import select
    existing = await db.execute(select(Contract).where(Contract.ocid == ocid))
    if existing.scalar_one_or_none():
        return ocid
    supplier = Supplier(id=uuid.uuid4(), name=f"Supplier-{ocid}",
                        tpin=f"80{abs(hash(ocid)) % 10**8:08d}", address="Anchor Road")
    db.add(supplier)
    await db.flush()
    contract = Contract(
        ocid=ocid,
        procuring_entity="Ministry of Anchoring",
        supplier_id=supplier.id,
        value=3_000_000.0, currency="ZMW",
        award_date=date(2024, 5, 1), signing_date=date(2024, 5, 20),
        status="active", raw_ocds={},
    )
    db.add(contract)
    await db.commit()
    return ocid


@pytest_asyncio.fixture
async def contract_ocid(db):
    """Shared contract for anchor write/idempotency tests."""
    return await _make_contract(db, "ocds-anchor-001")


@pytest_asyncio.fixture
async def verify_ocid(db):
    """Separate contract for verify tests — fresh per test, no bleed from anchor tests."""
    fresh = f"ocds-verify-{uuid.uuid4().hex[:8]}"
    return await _make_contract(db, fresh)


@pytest_asyncio.fixture
async def officer_role(db):
    return await make_role(db, "oversight_officer", "Oversight Officer",
                           ["read_named", "read_public", "action_anomaly"])


@pytest_asyncio.fixture
async def officer_user(db, officer_role):
    return await make_user(db, officer_role, email="officer_anc@oag.gov.zm", password="Officer123!")


# ── SHA-256 unit tests ─────────────────────────────────────────────────────────

def test_compute_sha256_deterministic():
    h1 = compute_sha256(SAMPLE_PDF)
    h2 = compute_sha256(SAMPLE_PDF)
    assert h1 == h2
    assert len(h1) == 64


def test_compute_sha256_different_for_different_content():
    h1 = compute_sha256(SAMPLE_PDF)
    h2 = compute_sha256(MODIFIED_PDF)
    assert h1 != h2


def test_compute_sha256_single_byte_change_changes_hash():
    original = b"contract content exactly"
    modified = b"contract content exactlY"  # last char changed
    assert compute_sha256(original) != compute_sha256(modified)


# ── Mock Fabric client unit tests ──────────────────────────────────────────────

def test_mock_fabric_set_and_get():
    client = MockFabricClient()
    result = client.submit_set_hash("ocds-001", "abc123")
    assert "tx_id" in result
    assert result["tx_id"].startswith("mock-tx-")
    assert client.query_get_hash("ocds-001") == "abc123"


def test_mock_fabric_unknown_ocid_returns_none():
    client = MockFabricClient()
    assert client.query_get_hash("unknown") is None


def test_mock_fabric_history():
    client = MockFabricClient()
    client.submit_set_hash("ocds-002", "deadbeef")
    history = client.query_get_history("ocds-002")
    assert len(history) == 1
    assert history[0]["sha256"] == "deadbeef"


def test_mock_fabric_clear():
    client = MockFabricClient()
    client.submit_set_hash("ocds-001", "hash1")
    client.clear()
    assert client.query_get_hash("ocds-001") is None


# ── Anchor service integration tests ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_anchor_creates_record(db, contract_ocid):
    record = await anchor_contract(db, contract_ocid, SAMPLE_PDF, anchored_by="user-1")
    assert record.contract_ocid == contract_ocid
    assert record.sha256 == compute_sha256(SAMPLE_PDF)
    assert record.ledger == "fabric"
    assert record.ledger_tx is not None
    assert record.block_ref is not None
    assert record.is_mock is True  # FABRIC_MOCK_MODE=True in test


@pytest.mark.asyncio
async def test_anchor_idempotent_same_document(db, contract_ocid):
    """Anchoring the same document twice → one record, no second Fabric tx."""
    r1 = await anchor_contract(db, contract_ocid, SAMPLE_PDF)
    r2 = await anchor_contract(db, contract_ocid, SAMPLE_PDF)
    assert r1.id == r2.id  # same record returned
    history = await get_anchor_history(db, contract_ocid)
    # Only one anchor record for this hash
    same_hash_records = [r for r in history if r.sha256 == r1.sha256]
    assert len(same_hash_records) == 1


@pytest.mark.asyncio
async def test_anchor_new_record_for_modified_document(db, contract_ocid):
    """Re-anchoring with a changed document → new record (re-signed contract)."""
    r1 = await anchor_contract(db, contract_ocid, SAMPLE_PDF)
    r2 = await anchor_contract(db, contract_ocid, MODIFIED_PDF)
    assert r1.id != r2.id
    assert r1.sha256 != r2.sha256
    history = await get_anchor_history(db, contract_ocid)
    assert len(history) >= 2


@pytest.mark.asyncio
async def test_anchor_unknown_ocid_raises(db):
    with pytest.raises(ValueError, match="not found"):
        await anchor_contract(db, "ocds-does-not-exist", SAMPLE_PDF)


# ── Verify tests ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_verify_original_match(db, verify_ocid):
    await anchor_contract(db, verify_ocid, SAMPLE_PDF)
    result = await verify_document(db, verify_ocid, SAMPLE_PDF)
    assert result["verdict"] == VerifyVerdict.MATCH
    assert result["provided_hash"] == result["anchored_hash"]


@pytest.mark.asyncio
async def test_verify_modified_mismatch(db, verify_ocid):
    await anchor_contract(db, verify_ocid, SAMPLE_PDF)
    result = await verify_document(db, verify_ocid, MODIFIED_PDF)
    assert result["verdict"] == VerifyVerdict.MISMATCH
    assert result["provided_hash"] != result["anchored_hash"]


@pytest.mark.asyncio
async def test_verify_not_registered(db, verify_ocid):
    # Fresh contract with no anchors
    result = await verify_document(db, verify_ocid, SAMPLE_PDF)
    assert result["verdict"] == VerifyVerdict.NOT_REGISTERED
    assert result["anchored_hash"] is None
    assert result["anchor"] is None


@pytest.mark.asyncio
async def test_verify_single_byte_change_mismatch(db, verify_ocid):
    data = b"exact contract content"
    tampered = b"eXact contract content"
    await anchor_contract(db, verify_ocid, data)
    result = await verify_document(db, verify_ocid, tampered)
    assert result["verdict"] == VerifyVerdict.MISMATCH


# ── API endpoint tests ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_post_anchor_requires_auth(client, contract_ocid):
    pdf_bytes = io.BytesIO(SAMPLE_PDF)
    r = await client.post(
        f"/api/v1/anchors?ocid={contract_ocid}",
        files={"file": ("contract.pdf", pdf_bytes, "application/pdf")},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_post_anchor_wrong_role_forbidden(client, db, contract_ocid):
    analyst_role = await make_role(db, "analyst_anc", "Analyst",
                                   ["read_named", "read_public"])
    analyst = await make_user(db, analyst_role, email="analyst_anc2@sigtrace.zm",
                               password="Analyst123!")
    pdf_bytes = io.BytesIO(SAMPLE_PDF)
    r = await client.post(
        f"/api/v1/anchors?ocid={contract_ocid}",
        files={"file": ("contract.pdf", pdf_bytes, "application/pdf")},
        headers=bearer(analyst),
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_post_anchor_success(client, officer_user, contract_ocid):
    pdf_bytes = io.BytesIO(SAMPLE_PDF)
    r = await client.post(
        f"/api/v1/anchors?ocid={contract_ocid}",
        files={"file": ("contract.pdf", pdf_bytes, "application/pdf")},
        headers=bearer(officer_user),
    )
    assert r.status_code == 201
    body = r.json()
    assert body["contract_ocid"] == contract_ocid
    assert body["sha256"] == compute_sha256(SAMPLE_PDF)
    assert body["ledger"] == "fabric"
    assert body["ledger_tx"] is not None


@pytest.mark.asyncio
async def test_post_anchor_idempotent_api(client, officer_user, contract_ocid):
    """Posting the same document twice returns the same anchor id."""
    pdf_bytes1 = io.BytesIO(SAMPLE_PDF)
    r1 = await client.post(
        f"/api/v1/anchors?ocid={contract_ocid}",
        files={"file": ("contract.pdf", pdf_bytes1, "application/pdf")},
        headers=bearer(officer_user),
    )
    pdf_bytes2 = io.BytesIO(SAMPLE_PDF)
    r2 = await client.post(
        f"/api/v1/anchors?ocid={contract_ocid}",
        files={"file": ("contract.pdf", pdf_bytes2, "application/pdf")},
        headers=bearer(officer_user),
    )
    assert r1.status_code == r2.status_code == 201
    assert r1.json()["id"] == r2.json()["id"]


@pytest.mark.asyncio
async def test_get_anchor_restricted(client, officer_user, contract_ocid, db):
    await anchor_contract(db, contract_ocid, SAMPLE_PDF)
    r = await client.get(f"/api/v1/anchors/{contract_ocid}", headers=bearer(officer_user))
    assert r.status_code == 200
    body = r.json()
    assert body["ocid"] == contract_ocid
    assert len(body["anchors"]) >= 1


@pytest.mark.asyncio
async def test_get_anchor_requires_auth(client, contract_ocid):
    r = await client.get(f"/api/v1/anchors/{contract_ocid}")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_public_anchor_endpoint(client, contract_ocid, db):
    await anchor_contract(db, contract_ocid, SAMPLE_PDF)
    r = await client.get(f"/api/v1/public/anchors/{contract_ocid}")
    assert r.status_code == 200
    body = r.json()
    assert "sha256" in body
    assert "ledger_tx" in body
    # Public endpoint must NOT expose named data (anchored_by not in response)
    assert "anchored_by" not in body


@pytest.mark.asyncio
async def test_public_anchor_not_found(client):
    r = await client.get("/api/v1/public/anchors/ocds-no-anchor")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_verify_endpoint_match(client, officer_user, db):
    v_ocid = await _make_contract(db, f"ocds-vapi-{uuid.uuid4().hex[:8]}")
    await anchor_contract(db, v_ocid, SAMPLE_PDF)
    r = await client.post(
        f"/api/v1/verify?ocid={v_ocid}",
        files={"file": ("contract.pdf", io.BytesIO(SAMPLE_PDF), "application/pdf")},
        headers=bearer(officer_user),
    )
    assert r.status_code == 200
    assert r.json()["verdict"] == "match"


@pytest.mark.asyncio
async def test_verify_endpoint_mismatch(client, officer_user, db):
    v_ocid = await _make_contract(db, f"ocds-vapi-{uuid.uuid4().hex[:8]}")
    await anchor_contract(db, v_ocid, SAMPLE_PDF)
    r = await client.post(
        f"/api/v1/verify?ocid={v_ocid}",
        files={"file": ("contract.pdf", io.BytesIO(MODIFIED_PDF), "application/pdf")},
        headers=bearer(officer_user),
    )
    assert r.status_code == 200
    assert r.json()["verdict"] == "mismatch"


@pytest.mark.asyncio
async def test_verify_endpoint_not_registered(client, officer_user, db):
    v_ocid = await _make_contract(db, f"ocds-vapi-{uuid.uuid4().hex[:8]}")
    r = await client.post(
        f"/api/v1/verify?ocid={v_ocid}",
        files={"file": ("contract.pdf", io.BytesIO(SAMPLE_PDF), "application/pdf")},
        headers=bearer(officer_user),
    )
    assert r.status_code == 200
    assert r.json()["verdict"] == "not_registered"
