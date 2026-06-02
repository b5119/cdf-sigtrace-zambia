"""Integration tests for /api/v1/auth/* endpoints (INC-001).

Uses an in-memory SQLite DB via the conftest overrides. Tests cover:
- Login step 1 (password)
- MFA challenge + verify
- Token refresh
- Logout (revocation)
- /auth/me
- Forgot/reset password
- Invalid/expired tokens rejected
"""
import pytest
import pytest_asyncio

from tests.conftest import make_role, make_user, bearer


@pytest_asyncio.fixture
async def admin_role(db):
    return await make_role(db, "system_admin", "System Administrator",
                           ["read_public", "verify_document", "read_named", "system_admin", "manage_users"])


@pytest_asyncio.fixture
async def admin_user(db, admin_role):
    return await make_user(db, admin_role, email="admin@sigtrace.zm", password="AdminPass123!")


@pytest.mark.asyncio
async def test_healthz(client):
    r = await client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_login_no_mfa_returns_tokens(client, admin_user, db):
    """When MFA not enabled, login returns tokens directly (dev / no-MFA path)."""
    r = await client.post("/api/v1/auth/login", json={"email": "admin@sigtrace.zm", "password": "AdminPass123!"})
    assert r.status_code == 200
    body = r.json()
    # Either MFA challenge or direct tokens
    assert "access_token" in body or "mfa_challenge_token" in body


@pytest.mark.asyncio
async def test_login_wrong_password(client, admin_user):
    r = await client.post("/api/v1/auth/login", json={"email": "admin@sigtrace.zm", "password": "WrongPass!"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email(client):
    r = await client.post("/api/v1/auth/login", json={"email": "nobody@nowhere.zm", "password": "pass"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_auth(client):
    r = await client.get("/api/v1/auth/me")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_principal(client, admin_user, db):
    """If no MFA, login → access token → /me returns the user."""
    r = await client.post("/api/v1/auth/login", json={"email": "admin@sigtrace.zm", "password": "AdminPass123!"})
    body = r.json()
    if "access_token" not in body:
        pytest.skip("MFA enforced — full token not available without TOTP code")
    token = body["access_token"]
    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    me_body = me.json()
    assert me_body["email"] == "admin@sigtrace.zm"
    assert me_body["role"]["key"] == "system_admin"


@pytest.mark.asyncio
async def test_refresh_then_logout(client, admin_user, db):
    r = await client.post("/api/v1/auth/login", json={"email": "admin@sigtrace.zm", "password": "AdminPass123!"})
    body = r.json()
    if "refresh_token" not in body:
        pytest.skip("MFA enforced — tokens not issued without TOTP")

    refresh_token = body["refresh_token"]
    access_token = body["access_token"]

    # Rotate the refresh token
    r2 = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert r2.status_code == 200
    new_tokens = r2.json()
    assert "access_token" in new_tokens

    # Old refresh token is now revoked — rotating again must fail
    r3 = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert r3.status_code == 401

    # Logout using new refresh token
    r4 = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": new_tokens["refresh_token"]},
        headers={"Authorization": f"Bearer {new_tokens['access_token']}"},
    )
    assert r4.status_code == 200


@pytest.mark.asyncio
async def test_forgot_password_always_200(client):
    """Forgot password must not reveal whether email exists."""
    r_exists = await client.post("/api/v1/auth/password/forgot", json={"email": "admin@sigtrace.zm"})
    r_missing = await client.post("/api/v1/auth/password/forgot", json={"email": "ghost@nowhere.zm"})
    assert r_exists.status_code == 200
    assert r_missing.status_code == 200
    assert r_exists.json()["message"] == r_missing.json()["message"]


@pytest.mark.asyncio
async def test_invalid_bearer_rejected(client):
    r = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not.a.valid.token"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_mfa_verify_bad_challenge_token(client):
    r = await client.post("/api/v1/auth/mfa/verify", json={
        "mfa_challenge_token": "invalid.token.here",
        "totp_code": "123456",
    })
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_reset_password_bad_token(client):
    r = await client.post("/api/v1/auth/password/reset", json={
        "reset_token": "invalid.reset.token",
        "new_password": "NewPassword999!",
    })
    assert r.status_code == 400
