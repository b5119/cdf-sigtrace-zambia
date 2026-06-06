"""Pydantic schemas for public-tier endpoints (INC-007, INC-008)."""
from datetime import date, datetime
from typing import Any, Optional

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


# ── Constituency schemas (INC-008) ────────────────────────────────────────────

class ConstituencySummary(BaseModel):
    id: str
    name: str
    province: str
    project_count: int
    verified_count: int
    risk_aggregate: Optional[str]   # "high" | "medium" | "low" | None


class ConstituencyDetail(BaseModel):
    id: str
    name: str
    province: str
    cdf_allocation: Optional[float]
    geo: Optional[Any]
    project_count: int
    verified_count: int
    risk_aggregate: Optional[str]


class ConstituencyMapFeature(BaseModel):
    """One item in the /public/map response — GeoJSON-style aggregate."""
    id: str
    name: str
    province: str
    lat: float
    lng: float
    project_count: int
    verified_count: int
    risk_score: Optional[float]
    risk_tier: Optional[str]        # "high" | "medium" | "low"
    cdf_allocation: Optional[float]


class MapResponse(BaseModel):
    type: str = "FeatureCollection"
    count: int
    features: list[ConstituencyMapFeature]


class ConstituencyListResponse(BaseModel):
    total: int
    constituencies: list[ConstituencySummary]


# ── Risk aggregate (INC-008) ──────────────────────────────────────────────────

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
    """Aggregated risk by procuring entity sector — de-identified (Entity A … E)."""
    entity_label: str               # "Entity A" … "Entity E"
    sector: str
    contract_count: int
    avg_risk_score: Optional[float]
    high_risk_count: int
    total_value_zmw: Optional[float]


class RiskAggregateResponse(BaseModel):
    entities: list[PublicRiskAggregateRow]
    generated_at: datetime


# ── Open data download (INC-008) ──────────────────────────────────────────────

class OpenDataMeta(BaseModel):
    dataset: str
    record_count: int
    generated_at: datetime
    note: str
    data: list[Any]


# ── Public project evidence (INC-014) ──────────────────────────────────────────

class PublicEvidenceItem(BaseModel):
    """De-identified field evidence — NO monitor identity, NO confirmer names."""
    submission_id: str
    ipfs_cid: Optional[str]
    lat: float
    lng: float
    category: Optional[str]
    captured_at: datetime
    status: str                      # pending / confirmed / rejected
    confirmation_count: int          # how many distinct confirmations
    onchain_tx: Optional[str]        # Polygon completion tx (if confirmed)


class PublicProjectDetail(BaseModel):
    """Public project page (P5) — disbursement, evidence, verified location, status."""
    project_id: str
    constituency_id: Optional[str]
    title: str
    category: str
    status: str
    verified: bool                   # has >=1 confirmed evidence submission
    disbursement_amount: Optional[float]
    disbursement_date: Optional[str]
    evidence_count: int
    confirmed_count: int
    location: Optional[dict]         # {lat, lng} verified location centroid


class PublicEvidenceListResponse(BaseModel):
    project_id: str
    total: int
    evidence: list[PublicEvidenceItem]


class PublicProjectSummary(BaseModel):
    """Public project list row (Projects index page)."""
    project_id: str
    title: str
    category: str
    constituency_id: Optional[str]
    disbursement_amount: Optional[float]
    status: str                      # completed | ongoing | no evidence
    verified: bool
    evidence_count: int


class PublicProjectListResponse(BaseModel):
    total: int
    projects: list[PublicProjectSummary]
