"""Pydantic schemas for ingestion run endpoints (INC-002)."""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TriggerRunRequest(BaseModel):
    source: str = "api"  # "api" | "sample" | a URL
    since: Optional[str] = None  # ISO date string


class IngestionRunOut(BaseModel):
    id: uuid.UUID
    started_at: datetime
    finished_at: Optional[datetime]
    source: str
    records_in: int
    records_loaded: int
    records_updated: int
    records_skipped: int
    errors: list[dict]
    status: str

    model_config = {"from_attributes": True}


class IngestionRunListResponse(BaseModel):
    runs: list[IngestionRunOut]
    total: int
