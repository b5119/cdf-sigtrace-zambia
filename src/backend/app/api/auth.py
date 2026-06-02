"""Auth router — /api/v1/auth/* (INC-001)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.mfa import generate_totp_secret, get_totp_uri, verify_totp
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    MFAChallengeResponse,
    MFASetupResponse,
    MFAVerifyRequest,
    MeResponse,
    MessageResponse,
    RefreshRequest,
    ResetPasswordRequest,
    TokenPairResponse,
)
from app.services.auth_service import (
    AuthError,
    apply_password_reset,
    complete_mfa,
    initiate_password_reset,
    revoke_refresh_token,
    rotate_tokens,
    start_login,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=MFAChallengeResponse | TokenPairResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Step 1: validate credentials. Returns MFA challenge or full tokens (if MFA not set up)."""
    try:
        result = await start_login(db, body.email, body.password)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    if result.get("step") == "mfa":
        return MFAChallengeResponse(mfa_challenge_token=result["mfa_challenge_token"])
    return TokenPairResponse(**result)


@router.post("/mfa/verify", response_model=TokenPairResponse)
async def mfa_verify(body: MFAVerifyRequest, db: AsyncSession = Depends(get_db)):
    """Step 2: submit TOTP code → receive access + refresh tokens."""
    try:
        result = await complete_mfa(db, body.mfa_challenge_token, body.totp_code)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return TokenPairResponse(**result)


@router.post("/refresh", response_model=TokenPairResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Rotate a valid refresh token into a new token pair."""
    try:
        result = await rotate_tokens(db, body.refresh_token)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return TokenPairResponse(**result)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    body: LogoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Revoke the given refresh token (jti) so it cannot be rotated."""
    await revoke_refresh_token(db, body.refresh_token)
    return MessageResponse(message="Logged out successfully")


@router.post("/password/forgot", response_model=MessageResponse)
async def forgot_password(body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Initiate a password reset. Always returns 200 to avoid email enumeration."""
    token = await initiate_password_reset(db, body.email)
    # In production, email the token. For the prototype, the token is returned in the
    # response body (only if found, but the message is identical either way).
    if token:
        # TODO(INC-016): send reset email with the token
        pass
    return MessageResponse(message="If that email is registered, a reset link has been sent")


@router.post("/password/reset", response_model=MessageResponse)
async def reset_password(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Apply a password reset using the token from the forgot-password flow."""
    try:
        await apply_password_reset(db, body.reset_token, body.new_password)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return MessageResponse(message="Password updated successfully")


@router.get("/me", response_model=MeResponse)
async def me(current_user: User = Depends(get_current_user)):
    """Return the current authenticated principal with role and permissions."""
    return current_user


# --- MFA device management (for onboarding / reset) ---

@router.post("/mfa/setup", response_model=MFASetupResponse)
async def mfa_setup(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a new TOTP secret for the authenticated user (not yet enabled)."""
    secret = generate_totp_secret()
    current_user.mfa_secret = secret
    await db.commit()
    return MFASetupResponse(
        secret=secret,
        totp_uri=get_totp_uri(secret, current_user.email),
    )


@router.post("/mfa/enable", response_model=MessageResponse)
async def mfa_enable(
    body: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Confirm the TOTP setup by verifying the first code, then mark MFA enabled."""
    if not current_user.mfa_secret:
        raise HTTPException(status_code=400, detail="Call /auth/mfa/setup first")
    if not verify_totp(current_user.mfa_secret, body.totp_code):
        raise HTTPException(status_code=400, detail="Invalid TOTP code")
    current_user.mfa_enabled = True
    await db.commit()
    return MessageResponse(message="MFA enabled successfully")
