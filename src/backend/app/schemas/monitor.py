"""Schemas for the integrated monitor (INC-015)."""
from typing import Optional

from pydantic import BaseModel, Field


class MonitorRunRequest(BaseModel):
    as_of: Optional[str] = None  # ISO date; defaults to today


class MonitorRunResponse(BaseModel):
    disbursements: int
    matched: int
    ghost_signals_raised: int
    ghost_signals_cleared: int


class GhostSignalOut(BaseModel):
    id: str
    disbursement_id: str
    constituency_id: Optional[str]
    project_id: Optional[str]
    amount: float
    disbursement_date: str
    days_overdue: int
    state: str
    raised_at: Optional[str]


class GhostQueueResponse(BaseModel):
    total: int
    signals: list[GhostSignalOut]


class DisbursementOut(BaseModel):
    id: str
    constituency_id: Optional[str]
    project_id: Optional[str]
    contract_ocid: Optional[str]
    amount: float
    date: str
    source: str
    matched_completion: bool
    matched_at: Optional[str]


class DisbursementListResponse(BaseModel):
    total: int
    disbursements: list[DisbursementOut]


class ClearSignalRequest(BaseModel):
    justification: str = Field(..., min_length=1, max_length=1000)


class ClearSignalResponse(BaseModel):
    id: str
    state: str
    justification: str
