"""Contract schemas — two-tier projections (INC-005).

Public tier:  no procuring_entity name, no supplier name, no contract value detail.
              Only aggregate/de-identified fields.
Restricted:   full named data.

The two projections are explicit separate schemas (not a runtime strip) so that
FastAPI's response_model enforces the field set at serialisation time — defence-in-depth
on top of the scoping middleware.
"""
import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


# ── Shared sub-schemas ─────────────────────────────────────────────────────────

class CheckResultOut(BaseModel):
    check_id: int
    check_key: str
    result: str          # "flag" | "ok" | "skip"
    evidence_note: str
    weight_applied: float


class RiskScoreOut(BaseModel):
    contract_ocid: str
    score: int
    normalised_score: int
    tier: str            # "high" | "medium" | "low"
    flag_count: int
    applicable_max: float
    weights_version: str
    breakdown: dict[str, dict]
    computed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Public (de-identified) projection ─────────────────────────────────────────

class ContractPublic(BaseModel):
    """
    De-identified contract record for anonymous/public callers.
    No procuring entity name, no supplier name, no TPIN.
    Only aggregate risk signal.
    """
    ocid: str
    status: str
    risk_score: Optional[int]
    risk_tier: Optional[str] = None   # populated by the router
    award_date: Optional[date]
    signing_date: Optional[date]
    framework_parent: Optional[str]   # presence only (not named)

    model_config = {"from_attributes": True}


class ContractPublicList(BaseModel):
    contracts: list[ContractPublic]
    total: int
    page: int
    size: int


# ── Restricted (named) projection ─────────────────────────────────────────────

class SupplierSummary(BaseModel):
    id: uuid.UUID
    name: str
    tpin: Optional[str]
    debarred_until: Optional[date]

    model_config = {"from_attributes": True}


class ContractRestricted(BaseModel):
    """Full named contract record for oversight officers / analysts / admins."""
    ocid: str
    procuring_entity: str
    supplier: Optional[SupplierSummary]
    value: Optional[float]
    currency: str
    award_date: Optional[date]
    signing_date: Optional[date]
    framework_parent: Optional[str]
    status: str
    risk_score: Optional[int]
    content_hash: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ContractRestrictedList(BaseModel):
    contracts: list[ContractRestricted]
    total: int
    page: int
    size: int


# ── Analysis trigger ───────────────────────────────────────────────────────────

class AnalysisRunRequest(BaseModel):
    ocids: Optional[list[str]] = None   # None = run over all contracts
    recalculate: bool = True


class AnalysisRunResponse(BaseModel):
    total: int
    flagged: int
    high_risk: int
    medium_risk: int
    low_risk: int
    errors: int
