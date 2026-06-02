"""Pydantic request/response schemas for auth endpoints (INC-001)."""
import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


# --- Requests ---

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class MFAVerifyRequest(BaseModel):
    mfa_challenge_token: str
    totp_code: str

    @field_validator("totp_code")
    @classmethod
    def code_is_6_digits(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 6:
            raise ValueError("TOTP code must be 6 digits")
        return v


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError("Password must be at least 10 characters")
        return v


# --- Responses ---

class MFAChallengeResponse(BaseModel):
    mfa_challenge_token: str
    message: str = "Enter your TOTP code to complete login"


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class InstitutionOut(BaseModel):
    id: uuid.UUID
    name: str
    type: str

    model_config = {"from_attributes": True}


class RoleOut(BaseModel):
    id: int
    key: str
    name: str
    permissions: list[str]

    model_config = {"from_attributes": True}


class MeResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role: RoleOut
    institution: Optional[InstitutionOut]
    mfa_enabled: bool

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    message: str


class MFASetupResponse(BaseModel):
    secret: str
    totp_uri: str
    message: str = "Scan the QR code with your authenticator app, then call /auth/mfa/enable to confirm"
