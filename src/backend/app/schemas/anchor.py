"""Pydantic schemas for anchor and verify endpoints (INC-006)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AnchorRecordOut(BaseModel):
    id: str
    contract_ocid: str
    sha256: str
    ledger: str
    ledger_tx: Optional[str]
    block_ref: Optional[str]
    anchored_by: Optional[str]
    anchored_at: datetime
    is_mock: bool

    model_config = {"from_attributes": True}


class AnchorHistoryResponse(BaseModel):
    ocid: str
    anchors: list[AnchorRecordOut]


class VerifyResponse(BaseModel):
    verdict: str              # "match" | "mismatch" | "not_registered"
    provided_hash: str
    anchored_hash: Optional[str]
    anchor: Optional[AnchorRecordOut]
    message: str


class PublicAnchorOut(BaseModel):
    """De-identified anchor record for public /public/anchors/{ocid} endpoint."""
    contract_ocid: str
    sha256: str
    ledger: str
    ledger_tx: Optional[str]
    block_ref: Optional[str]
    anchored_at: datetime

    model_config = {"from_attributes": True}
