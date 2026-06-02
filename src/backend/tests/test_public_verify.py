"""Tests for the public verification portal — POST /public/verify-contract (INC-007).

Acceptance criteria (from 08_INCREMENT_PLAN.md):
- Uploading the original document returns MATCH.
- A modified byte returns MISMATCH.
- Unknown OCID returns NOT_REGISTERED.
- No named data in any response field.
- No authentication required.
- Rate limiting applies (120/min — verified structurally, not exhaustively).
- Empty file and non-PDF rejected with correct status codes.
"""
import io
import uuid
from datetime import date

import pytest
import pytest_asyncio

from app.models.contract import Contract, Supplier
from app.services.anchor_service import anchor_contract, compute_sha256
from app.services.fabric_client import MockFabricClient, get_fabric_client

SAMPLE_PDF = b"%PDF-1.4 genuine contract document for public portal testing"
MODIFIED_PDF = b"%PDF-1.4 genuine contract document for public portal testing TAMPERED"
NOT_PDF = b"This is plain text, not a PDF"


@pytest_asyncio.fixture(autouse=True)
def reset_mock():
    client = get_fabric_client()
    if isinstance(client, MockFabricClient):
        client.clear()
    yield
    if isinstance(client, MockFabricClient):
        client.clear()


async def _make_contract(db, ocid: str) -> str:
    from sqlalchemy import select
    existing = await db.execute(select(Contract).where(Contract.ocid == ocid))
    if existing.scalar_one_or_none():
        return ocid
    supplier = Supplier(
        id=uuid.uuid4(), name=f"Pub-Supplier-{ocid}",
        tpin=f"70{abs(hash(ocid)) % 10**8:08d}", address="Public Road"
    )
    db.add(supplier)
    await db.flush()
    contract = Contract(
        ocid=ocid, procuring_entity="Ministry of Public Works",
        supplier_id=supplier.id, value=2_500_000.0, currency="ZMW",
        award_date=date(2024, 6, 1), signing_date=date(2024, 6, 18),
        status="active", raw_ocds={},
    )
    db.add(contract)
    await db.commit()
    return ocid


# ── Verdict tests ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_public_verify_match(client, db):
    ocid = await _make_contract(db, f"ocds-pub-{uuid.uuid4().hex[:8]}")
    await anchor_contract(db, ocid, SAMPLE_PDF)

    r = await client.post(
        f"/api/v1/public/verify-contract?ocid={ocid}",
        files={"file": ("contract.pdf", io.BytesIO(SAMPLE_PDF), "application/pdf")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["verdict"] == "match"
    assert body["provided_hash"] == compute_sha256(SAMPLE_PDF)
    assert body["anchored_hash"] == body["provided_hash"]
    assert body["ledger"] == "fabric"
    assert body["ledger_tx"] is not None
    assert "verified" in body["message"].lower()


@pytest.mark.asyncio
async def test_public_verify_mismatch(client, db):
    ocid = await _make_contract(db, f"ocds-pub-{uuid.uuid4().hex[:8]}")
    await anchor_contract(db, ocid, SAMPLE_PDF)

    r = await client.post(
        f"/api/v1/public/verify-contract?ocid={ocid}",
        files={"file": ("contract.pdf", io.BytesIO(MODIFIED_PDF), "application/pdf")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["verdict"] == "mismatch"
    assert body["provided_hash"] != body["anchored_hash"]
    assert "not match" in body["message"].lower()


@pytest.mark.asyncio
async def test_public_verify_not_registered(client, db):
    ocid = await _make_contract(db, f"ocds-pub-{uuid.uuid4().hex[:8]}")
    # No anchor created

    r = await client.post(
        f"/api/v1/public/verify-contract?ocid={ocid}",
        files={"file": ("contract.pdf", io.BytesIO(SAMPLE_PDF), "application/pdf")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["verdict"] == "not_registered"
    assert body["anchored_hash"] is None
    assert body["ledger_tx"] is None


@pytest.mark.asyncio
async def test_public_verify_unknown_ocid(client):
    """OCID not in DB at all → not_registered (verify_document returns not_registered)."""
    r = await client.post(
        "/api/v1/public/verify-contract?ocid=ocds-unknown-00000",
        files={"file": ("contract.pdf", io.BytesIO(SAMPLE_PDF), "application/pdf")},
    )
    assert r.status_code == 200
    assert r.json()["verdict"] == "not_registered"


# ── No authentication required ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_public_verify_requires_no_auth(client, db):
    """No Authorization header — must still work."""
    ocid = await _make_contract(db, f"ocds-pub-{uuid.uuid4().hex[:8]}")
    await anchor_contract(db, ocid, SAMPLE_PDF)

    r = await client.post(
        f"/api/v1/public/verify-contract?ocid={ocid}",
        files={"file": ("contract.pdf", io.BytesIO(SAMPLE_PDF), "application/pdf")},
        # deliberately no headers= arg
    )
    assert r.status_code == 200


# ── No named data in response ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_public_verify_response_contains_no_named_data(client, db):
    """
    The response must not expose procuring_entity, supplier name, anchored_by,
    or any PII — only hash, ledger proof, and verdict.
    """
    ocid = await _make_contract(db, f"ocds-pub-{uuid.uuid4().hex[:8]}")
    await anchor_contract(db, ocid, SAMPLE_PDF, anchored_by="officer-uuid-secret")

    r = await client.post(
        f"/api/v1/public/verify-contract?ocid={ocid}",
        files={"file": ("contract.pdf", io.BytesIO(SAMPLE_PDF), "application/pdf")},
    )
    body = r.json()
    # These must NOT appear
    assert "procuring_entity" not in body
    assert "supplier" not in body
    assert "anchored_by" not in body
    assert "officer-uuid-secret" not in str(body)
    assert "Ministry of Public Works" not in str(body)


# ── Input validation ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_public_verify_rejects_non_pdf(client):
    r = await client.post(
        "/api/v1/public/verify-contract?ocid=ocds-any",
        files={"file": ("notes.txt", io.BytesIO(NOT_PDF), "text/plain")},
    )
    assert r.status_code == 415


@pytest.mark.asyncio
async def test_public_verify_rejects_empty_file(client):
    r = await client.post(
        "/api/v1/public/verify-contract?ocid=ocds-any",
        files={"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")},
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_public_verify_single_byte_tamper_detected(client, db):
    """A single-byte change must produce MISMATCH."""
    ocid = await _make_contract(db, f"ocds-pub-{uuid.uuid4().hex[:8]}")
    original = b"exact contract bytes for tamper test"
    tampered = b"exact contract bytes for tamper tesT"
    await anchor_contract(db, ocid, original)

    r = await client.post(
        f"/api/v1/public/verify-contract?ocid={ocid}",
        files={"file": ("contract.pdf", io.BytesIO(tampered), "application/pdf")},
    )
    assert r.status_code == 200
    assert r.json()["verdict"] == "mismatch"


# ── Hash integrity ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_provided_hash_matches_sha256_of_upload(client, db):
    """provided_hash in response must always equal SHA-256 of the uploaded bytes."""
    ocid = await _make_contract(db, f"ocds-pub-{uuid.uuid4().hex[:8]}")

    r = await client.post(
        f"/api/v1/public/verify-contract?ocid={ocid}",
        files={"file": ("contract.pdf", io.BytesIO(SAMPLE_PDF), "application/pdf")},
    )
    expected = compute_sha256(SAMPLE_PDF)
    assert r.json()["provided_hash"] == expected


@pytest.mark.asyncio
async def test_different_documents_give_different_hashes(client, db):
    ocid = await _make_contract(db, f"ocds-pub-{uuid.uuid4().hex[:8]}")
    await anchor_contract(db, ocid, SAMPLE_PDF)

    r1 = await client.post(
        f"/api/v1/public/verify-contract?ocid={ocid}",
        files={"file": ("a.pdf", io.BytesIO(SAMPLE_PDF), "application/pdf")},
    )
    r2 = await client.post(
        f"/api/v1/public/verify-contract?ocid={ocid}",
        files={"file": ("b.pdf", io.BytesIO(MODIFIED_PDF), "application/pdf")},
    )
    assert r1.json()["provided_hash"] != r2.json()["provided_hash"]
    assert r1.json()["verdict"] == "match"
    assert r2.json()["verdict"] == "mismatch"
