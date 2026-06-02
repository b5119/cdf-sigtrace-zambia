"""TOTP-based MFA utilities using pyotp."""
import pyotp

from app.core.config import settings


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def get_totp_uri(secret: str, user_email: str) -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=user_email,
        issuer_name=settings.MFA_ISSUER,
    )


def verify_totp(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    # valid_window=1 allows ±30 s clock drift
    return totp.verify(code, valid_window=1)
