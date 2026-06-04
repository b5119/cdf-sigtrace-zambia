from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    APP_NAME: str = "CDF SigTrace API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cdf_sigtrace"
    DATABASE_SYNC_URL: str = "postgresql://postgres:postgres@localhost:5432/cdf_sigtrace"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "changeme-dev-secret-at-least-32-chars-long"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # MFA
    MFA_ISSUER: str = "CDF SigTrace"
    MFA_ENFORCE: bool = True  # set False in test

    # Password reset
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"]

    # Object store
    OBJECT_STORE_ENDPOINT: str = "http://localhost:9000"
    OBJECT_STORE_ACCESS_KEY: str = "minioadmin"
    OBJECT_STORE_SECRET_KEY: str = "minioadmin"
    OBJECT_STORE_BUCKET_CONTRACTS: str = "contracts"

    # Fabric (INC-006)
    FABRIC_GATEWAY_ENDPOINT: str = ""
    FABRIC_MSP_ID: str = ""
    FABRIC_CHANNEL: str = "sigtrace-channel"
    FABRIC_CHAINCODE: str = "anchor"
    FABRIC_TLS_CERT_PATH: str = ""
    FABRIC_CLIENT_CERT_PATH: str = ""
    FABRIC_CLIENT_KEY_PATH: str = ""
    # Set True in dev/test to use in-memory mock instead of real Fabric network
    FABRIC_MOCK_MODE: bool = True

    # Polygon (placeholder for INC-012)
    POLYGON_RPC: str = ""
    POLYGON_SIGNER_KEY: str = ""

    # IPFS (INC-011)
    IPFS_API: str = "/ip4/127.0.0.1/tcp/5001"
    IPFS_API_URL: str = "http://localhost:5001"  # Kubo HTTP API base
    IPFS_GATEWAY_URL: str = "http://localhost:8080/ipfs"
    # Set True in dev/test to use the in-memory content-addressed mock
    IPFS_MOCK_MODE: bool = True
    # Max evidence photo size (MB)
    IPFS_MAX_PHOTO_MB: int = 15

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_secret(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters")
        return v


settings = Settings()
