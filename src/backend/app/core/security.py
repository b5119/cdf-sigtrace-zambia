"""JWT token handling, password hashing, and token revocation."""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _make_token(data: dict, expire_delta: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + expire_delta
    payload["iat"] = datetime.now(timezone.utc)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_access_token(sub: str, role: str, institution_id: Optional[str]) -> str:
    jti = str(uuid.uuid4())
    return _make_token(
        {
            "sub": sub,
            "role": role,
            "institution_id": institution_id,
            "jti": jti,
            "type": "access",
        },
        timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(sub: str, role: str, institution_id: Optional[str]) -> tuple[str, str]:
    """Returns (encoded_token, jti) — caller should store jti for revocation."""
    jti = str(uuid.uuid4())
    token = _make_token(
        {
            "sub": sub,
            "role": role,
            "institution_id": institution_id,
            "jti": jti,
            "type": "refresh",
        },
        timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return token, jti


def create_mfa_challenge_token(sub: str) -> str:
    """Short-lived token issued after password check, before MFA verify."""
    jti = str(uuid.uuid4())
    return _make_token(
        {"sub": sub, "jti": jti, "type": "mfa_challenge"},
        timedelta(minutes=5),
    )


def create_password_reset_token(sub: str) -> str:
    jti = str(uuid.uuid4())
    return _make_token(
        {"sub": sub, "jti": jti, "type": "password_reset"},
        timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
    )


def decode_token(token: str) -> dict:
    """Decode and return payload; raises JWTError on failure."""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
