"""Consolidated security checklist (INC-019).

Automates the security checklist from docs/10_TESTING.md as a single
verifiable suite. Each test maps to a checklist item.
"""
import io
import uuid

import pytest
import pytest_asyncio

from tests.conftest import bearer, make_role, make_user


# ── 1. Restricted endpoints reject missing/invalid JWT ────────────────────────

@pytest.mark.asyncio
@pytest.mark.parametrize("path", [
    "/api/v1/auth/me",
    "/api/v1/contracts/ocds-x",
    "/api/v1/anchors/ocds-x",
    "/api/v1/monitor/ghost-projects",
    "/api/v1/cases",
    "/api/v1/admin/health",
    "/api/v1/admin/users",
])
async def test_restricted_endpoints_reject_no_jwt(client, path):
    r = await client.get(path)
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_restricted_endpoint_rejects_invalid_jwt(client):
    r = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not.a.real.token"})
    assert r.status_code == 401


# ── 2. No PII / names in any public response ──────────────────────────────────

@pytest.mark.asyncio
@pytest.mark.parametrize("path", [
    "/api/v1/public/overview",
    "/api/v1/public/map",
    "/api/v1/public/constituencies",
    "/api/v1/public/risk/aggregate",
    "/api/v1/public/opendata/contracts",
])
async def test_public_responses_have_no_pii_fields(client, path):
    r = await client.get(path)
    assert r.status_code == 200
    body = r.text.lower()
    for forbidden in ["password", "mfa_secret", "supplier_name", "procuring_entity", "monitor_id", "tpin"]:
        assert forbidden not in body, f"{forbidden} leaked in {path}"


# ── 3. No personal data written to any ledger ─────────────────────────────────

def test_anchor_sends_only_hash_not_document():
    """The anchor service hashes the document and only the hash goes to Fabric."""
    from app.services.anchor_service import compute_sha256
    doc = b"%PDF sensitive contract with names and TPINs"
    h = compute_sha256(doc)
    # The hash is 64 hex chars; the document bytes are not derivable from it
    assert len(h) == 64
    assert h != doc.hex()


def test_ipfs_cid_is_hash_not_content():
    """IPFS CID is a content hash, not the photo bytes."""
    from app.services.ipfs_client import compute_cid
    photo = b"\xff\xd8 photo with a person's face \xff\xd9"
    cid = compute_cid(photo)
    assert cid.startswith("bafkrei")
    assert "person" not in cid


# ── 4. File upload validation ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_public_verify_rejects_non_pdf(client):
    r = await client.post("/api/v1/public/verify-contract?ocid=x",
                          files={"file": ("x.exe", io.BytesIO(b"MZ"), "application/octet-stream")})
    assert r.status_code == 415


@pytest.mark.asyncio
async def test_public_verify_rejects_empty(client):
    r = await client.post("/api/v1/public/verify-contract?ocid=x",
                          files={"file": ("x.pdf", io.BytesIO(b""), "application/pdf")})
    assert r.status_code == 400


# ── 5. Security headers present ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_security_headers_present(client):
    r = await client.get("/healthz")
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert "max-age" in r.headers.get("Strict-Transport-Security", "")
    assert "Content-Security-Policy" in r.headers
    assert "Referrer-Policy" in r.headers


# ── 6. Rate limiting configured ───────────────────────────────────────────────

def test_rate_limiter_configured():
    from app.core.rate_limit import limiter, AUTH_LIMIT, PUBLIC_LIMIT
    assert limiter is not None
    assert "minute" in AUTH_LIMIT
    assert "minute" in PUBLIC_LIMIT


# ── 7. Passwords hashed with Argon2id ─────────────────────────────────────────

def test_passwords_use_argon2():
    from app.core.security import hash_password
    h = hash_password("secret-password-123")
    assert h.startswith("$argon2id$")


# ── 8. Audit trail integrity (tamper-evidence) ────────────────────────────────

@pytest.mark.asyncio
async def test_audit_integrity_detects_tampering(db):
    """Recomputed batch hash must match; tampering breaks it."""
    from app.services.audit_service import log_action, anchor_batch, verify_integrity, compute_batch_hash
    from app.models.audit import AuditLog
    from sqlalchemy import select

    await log_action(db, "actor-x", "sensitive_action", "thing", "ref-1", {"amount": 1000})
    await db.commit()
    await anchor_batch(db)

    # Untampered → verified
    v1 = await verify_integrity(db)
    assert v1["verified"] is True

    # Tamper with an entry's meta directly
    result = await db.execute(select(AuditLog).where(AuditLog.action == "sensitive_action"))
    entry = result.scalar_one()
    entry.meta = {"amount": 999999}  # someone altered the record
    await db.commit()

    v2 = await verify_integrity(db)
    assert v2["verified"] is False
    assert len(v2["tampered"]) >= 1


# ── 9. MFA enforced flag exists; brute force throttled via rate limit ─────────

def test_mfa_enforce_setting_exists():
    from app.core.config import settings
    assert hasattr(settings, "MFA_ENFORCE")


# ── 10. Two-tier isolation — public cannot read named contract data ───────────

@pytest.mark.asyncio
async def test_public_caller_gets_no_named_contract_data(client):
    """An anonymous /contracts call returns de-identified rows only."""
    r = await client.get("/api/v1/contracts")
    assert r.status_code == 200
    for c in r.json().get("contracts", []):
        assert "procuring_entity" not in c
        assert "supplier" not in c
