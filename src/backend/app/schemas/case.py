"""Schemas for cases & notifications (INC-016)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CaseCreate(BaseModel):
    subject_type: str = Field(..., pattern="^(contract|ghost_project)$")
    subject_ref: str
    title: str = Field(..., min_length=1, max_length=300)
    assignee_id: Optional[str] = None
    priority: str = Field("medium", pattern="^(low|medium|high)$")


class CaseUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(open|in_review|escalated|closed)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    assignee_id: Optional[str] = None


class NoteCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=5000)


class EscalateRequest(BaseModel):
    target: str = Field("ACC", max_length=50)


class CaseNoteOut(BaseModel):
    id: str
    case_id: str
    author_id: str
    body: str
    created_at: datetime
    model_config = {"from_attributes": True}


class CaseOut(BaseModel):
    id: str
    subject_type: str
    subject_ref: str
    title: str
    assignee_id: Optional[str]
    status: str
    priority: str
    created_by: str
    created_at: datetime
    closed_at: Optional[datetime]
    notes: list[CaseNoteOut] = []
    model_config = {"from_attributes": True}


class CaseListResponse(BaseModel):
    total: int
    cases: list[CaseOut]


class NotificationOut(BaseModel):
    id: str
    type: str
    payload: dict
    read: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    total: int
    unread: int
    notifications: list[NotificationOut]
