"""Pydantic schemas for public-tier endpoints (INC-007, INC-008)."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


# ── Verification portal (INC-007) ──────────────────────────────────────────────

class PublicVerifyResponse(BaseModel):
    """
    Response from POST /public/verify-contract.
    Contains no named data — only hash, ledger proof, and verdict.
    """
    verdict: str                    # "match" | "mismatch" | "not_registered"
    message: str
    provided_hash: str              # SHA-256 of the uploaded file
    anchored_hash: Optional[str]    # SHA-256 stored on Fabric (if registered)
    ledger: Optional[str]           # "fabric"
    ledger_tx: Optional[str]        # Fabric transaction ID
    block_ref: Optional[str]        # Fabric block reference
    anchored_at: Optional[datetime] # when the anchor was written
    # No: ocid, procuring_entity, supplier, anchored_by — all stripped


# ── Public overview / KPIs (INC-008) ──────────────────────────────────────────

class NationalKPIs(BaseModel):
    total_contracts: int
    total_value_zmw: Optional[float]
    verified_contracts: int         # anchored
    high_risk_contracts: int
    ghost_project_signals: int      # disbursements with no verified completion
    constituencies_covered: int


class ConstituencySummary(BaseModel):
    id: str
    name: str
    province: str
    project_count: int
    verified_count: int
    risk_aggregate: Optional[str]   # "high" | "medium" | "low" | None


class PublicContractSummary(BaseModel):
    """De-identified contract row for public risk overview (no names)."""
    ocid: str
    status: str
    risk_score: Optional[int]
    risk_tier: Optional[str]
    award_date: Optional[date]
    anchor_status: str              # "anchored" | "not_anchored"
    flag_count: Optional[int]


class PublicRiskAggregateRow(BaseModel):
    """Aggregated risk by procuring entity sector — de-identified."""
    sector: str
    contract_count: int
    avg_risk_score: Optional[float]
    high_risk_count: int
    total_value_zmw: Optional[float]
