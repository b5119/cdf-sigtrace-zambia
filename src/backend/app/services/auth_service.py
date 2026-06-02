"""Business logic for authentication flows (INC-001)."""
import uuid as _uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.mfa import verify_totp
from app.core.security import (
    create_access_token,
    create_mfa_challenge_token,
    create_password_reset_token,
    create_refresh_token,
    hash_password,
    verify_password,
    decode_token,
)
from app.models.user import RefreshToken, User


class AuthError(Exception):
    pass


async def authenticate_password(db: AsyncSession, email: str, password: str) -> User:
    result = await db.execute(select(User).where(User.email == email, User.active == True))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise AuthError("Invalid credentials")
    return user


async def start_login(db: AsyncSession, email: str, password: str) -> dict:
    """
    Step 1 of login: validate password.
    Returns either full tokens (if MFA not required/enabled) or an MFA challenge token.
    """
    user = await authenticate_password(db, email, password)
    if settings.MFA_ENFORCE and user.mfa_enabled:
        challenge = create_mfa_challenge_token(str(user.id))
        return {"step": "mfa", "mfa_challenge_token": challenge}
    # MFA not enforced or not yet set up — issue tokens directly (dev mode)
    return await _issue_tokens(db, user)


async def complete_mfa(db: AsyncSession, challenge_token: str, totp_code: str) -> dict:
    """Step 2 of login: verify TOTP, issue tokens."""
    from jose import JWTError
    try:
        payload = decode_token(challenge_token)
    except JWTError:
        raise AuthError("Invalid or expired challenge token")
    if payload.get("type") != "mfa_challenge":
        raise AuthError("Invalid token type")
    user_id = _uuid.UUID(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id, User.active == True))
    user = result.scalar_one_or_none()
    if not user:
        raise AuthError("User not found")
    if not user.mfa_secret or not verify_totp(user.mfa_secret, totp_code):
        raise AuthError("Invalid TOTP code")
    return await _issue_tokens(db, user)


async def _issue_tokens(db: AsyncSession, user: User) -> dict:
    institution_id = str(user.institution_id) if user.institution_id else None
    access = create_access_token(str(user.id), user.role.key, institution_id)
    refresh, jti = create_refresh_token(str(user.id), user.role.key, institution_id)

    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    db.add(RefreshToken(jti=jti, user_id=user.id, expires_at=expires_at))

    # Update last_login
    await db.execute(
        update(User).where(User.id == user.id).values(last_login=datetime.now(timezone.utc))
    )
    await db.commit()
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


async def rotate_tokens(db: AsyncSession, refresh_token_str: str) -> dict:
    """Validate a refresh token, revoke it, issue a new pair."""
    from jose import JWTError
    try:
        payload = decode_token(refresh_token_str)
    except JWTError:
        raise AuthError("Invalid or expired refresh token")
    if payload.get("type") != "refresh":
        raise AuthError("Invalid token type")
    jti = payload["jti"]
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.jti == jti, RefreshToken.revoked == False)
    )
    token_record = result.scalar_one_or_none()
    if not token_record:
        raise AuthError("Token not found or already revoked")

    # Revoke old token
    token_record.revoked = True
    await db.flush()

    user_id = _uuid.UUID(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id, User.active == True))
    user = result.scalar_one_or_none()
    if not user:
        raise AuthError("User not found")
    return await _issue_tokens(db, user)


async def revoke_refresh_token(db: AsyncSession, refresh_token_str: str) -> None:
    """Logout: revoke the given refresh token by jti."""
    from jose import JWTError
    try:
        payload = decode_token(refresh_token_str)
    except JWTError:
        return  # graceful on invalid token
    jti = payload.get("jti")
    if jti:
        result = await db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
        record = result.scalar_one_or_none()
        if record:
            record.revoked = True
            await db.commit()


async def initiate_password_reset(db: AsyncSession, email: str) -> str | None:
    """Return a reset token if user exists; otherwise return None (no email enumeration)."""
    result = await db.execute(select(User).where(User.email == email, User.active == True))
    user = result.scalar_one_or_none()
    if not user:
        return None
    return create_password_reset_token(str(user.id))


async def apply_password_reset(db: AsyncSession, reset_token: str, new_password: str) -> None:
    from jose import JWTError
    try:
        payload = decode_token(reset_token)
    except JWTError:
        raise AuthError("Invalid or expired reset token")
    if payload.get("type") != "password_reset":
        raise AuthError("Invalid token type")
    user_id = _uuid.UUID(payload["sub"])
    new_hash = hash_password(new_password)
    await db.execute(update(User).where(User.id == user_id).values(password_hash=new_hash))
    await db.commit()
