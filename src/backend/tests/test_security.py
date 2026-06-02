"""Unit tests for JWT, password hashing, and MFA utilities (INC-001)."""
import time

import pytest
from jose import JWTError

from app.core.mfa import generate_totp_secret, verify_totp, get_totp_uri
from app.core.security import (
    create_access_token,
    create_mfa_challenge_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


# --- Password hashing ---

def test_hash_verify_round_trip():
    pw = "supersecret123"
    h = hash_password(pw)
    assert verify_password(pw, h)


def test_wrong_password_rejected():
    h = hash_password("correct")
    assert not verify_password("wrong", h)


def test_hashes_are_unique():
    pw = "same_password"
    assert hash_password(pw) != hash_password(pw)  # argon2 uses a unique salt


# --- JWT ---

def test_access_token_decode():
    token = create_access_token("user-123", "oversight_officer", "inst-abc")
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["role"] == "oversight_officer"
    assert payload["institution_id"] == "inst-abc"
    assert payload["type"] == "access"


def test_refresh_token_decode():
    token, jti = create_refresh_token("user-456", "analyst", None)
    payload = decode_token(token)
    assert payload["sub"] == "user-456"
    assert payload["jti"] == jti
    assert payload["type"] == "refresh"
    assert payload["institution_id"] is None


def test_mfa_challenge_token():
    token = create_mfa_challenge_token("user-789")
    payload = decode_token(token)
    assert payload["type"] == "mfa_challenge"
    assert payload["sub"] == "user-789"


def test_password_reset_token():
    token = create_password_reset_token("user-000")
    payload = decode_token(token)
    assert payload["type"] == "password_reset"


def test_tampered_token_rejected():
    token = create_access_token("u1", "analyst", None)
    tampered = token[:-4] + "XXXX"
    with pytest.raises(JWTError):
        decode_token(tampered)


# --- TOTP MFA ---

def test_totp_valid_code():
    import pyotp
    secret = generate_totp_secret()
    code = pyotp.TOTP(secret).now()
    assert verify_totp(secret, code)


def test_totp_wrong_code():
    secret = generate_totp_secret()
    assert not verify_totp(secret, "000000")


def test_totp_uri_contains_issuer():
    secret = generate_totp_secret()
    uri = get_totp_uri(secret, "officer@oag.gov.zm")
    assert "CDF" in uri
    assert "officer%40oag.gov.zm" in uri or "officer@oag.gov.zm" in uri
