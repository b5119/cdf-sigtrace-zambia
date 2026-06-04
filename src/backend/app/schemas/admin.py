"""Schemas for the admin console (INC-017)."""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class WeightItem(BaseModel):
    id: int
    key: str
    name: str
    weight: float
    severity: str
    enabled: bool


class WeightsResponse(BaseModel):
    weights: list[WeightItem]


class WeightsUpdate(BaseModel):
    # map of check key -> new weight
    weights: dict[str, float]


class ThresholdsResponse(BaseModel):
    thresholds: dict


class ThresholdsUpdate(BaseModel):
    thresholds: dict


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: Optional[str]
    institution_id: Optional[str] = None
    active: bool
    mfa_enabled: Optional[bool] = None
    last_login: Optional[str] = None


class UserListResponse(BaseModel):
    total: int
    users: list[UserOut]


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=10)
    role_key: str
    institution_id: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    active: Optional[bool] = None
    role_key: Optional[str] = None


class RoleOut(BaseModel):
    id: int
    key: str
    name: str
    permissions: list[str]


class HealthResponse(BaseModel):
    status: str
    components: dict
    checked_at: str
