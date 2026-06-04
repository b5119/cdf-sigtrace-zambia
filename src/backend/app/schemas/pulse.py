"""Pydantic schemas for CDF Pulse field evidence (INC-010)."""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AssignmentProject(BaseModel):
    id: str
    title: str
    category: str
    status: str
    constituency_id: str
    constituency_name: str


class AssignmentsResponse(BaseModel):
    constituency_id: str
    constituency_name: str
    projects: list[AssignmentProject]


class SubmissionCreate(BaseModel):
    """One offline-captured submission. client_uuid gives exactly-once semantics."""
    client_uuid: str = Field(..., min_length=8, max_length=64)
    project_id: str
    constituency_id: Optional[str] = None
    lat: float
    lng: float
    category: Optional[str] = None
    note: Optional[str] = None
    captured_at: datetime


class SyncBatch(BaseModel):
    """A batch of queued offline submissions to sync in one request."""
    submissions: list[SubmissionCreate]


class SubmissionOut(BaseModel):
    id: str
    client_uuid: str
    project_id: str
    constituency_id: Optional[str]
    lat: float
    lng: float
    category: Optional[str]
    note: Optional[str]
    ipfs_cid: Optional[str]
    captured_at: datetime
    synced_at: Optional[datetime]
    status: str
    onchain_tx: Optional[str]

    model_config = {"from_attributes": True}


class SubmissionListResponse(BaseModel):
    submissions: list[SubmissionOut]
    total: int


class SyncResult(BaseModel):
    synced: int
    duplicates: int  # client_uuids already present (idempotent skip)
    submissions: list[SubmissionOut]
