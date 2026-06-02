"""Anchor endpoints — /api/v1/anchors/* and /api/v1/verify (INC-006).

POST /anchors           — oversight_officer — anchor a contract document hash to Fabric
GET  /anchors/{ocid}    — read_named        — full anchor record (named context)
POST /verify            — read_named        — verify a document vs its anchor (restricted)

Public verification (POST /public/verify-contract) lives in the public router (INC-007).
"""
from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.rbac import Permission, require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.anchor import AnchorHistoryResponse, AnchorRecordOut, PublicAnchorOut, VerifyResponse
from app.services.anchor_service import anchor_contract, get_anchor_history, verify_document

router = APIRouter(tags=["anchors"])

_MAX_UPLOAD_MB = 20
_MAX_BYTES = _MAX_UPLOAD_MB * 1024 * 1024


# ── POST /anchors — anchor a contract document ─────────────────────────────────

@router.post("/anchors", response_model=AnchorRecordOut, status_code=status.HTTP_201_CREATED)
async def create_anchor(
    ocid: str,
    file: UploadFile = File(..., description="Signed contract PDF"),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permission(Permission.ACTION_ANOMALY),
):
    """
    Hash the uploaded document (SHA-256) and anchor the hash to Hyperledger Fabric.
    The document bytes are discarded after hashing — only the hash is stored.
    Idempotent: anchoring the same document twice returns the existing record.
    """
    content_type = file.content_type or ""
    if "pdf" not in content_type and not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Only PDF documents are accepted")

    data = await file.read()
    if len(data) > _MAX_BYTES:
        raise HTTPException(status_code=413, detail=f"File exceeds {_MAX_UPLOAD_MB} MB limit")

    try:
        record = await anchor_contract(
            db=db,
            ocid=ocid,
            document_bytes=data,
            anchored_by=str(current_user.id),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Fabric submission failed: {e}")

    return record


# ── GET /anchors/{ocid} — anchor history (restricted) ─────────────────────────

@router.get("/anchors/{ocid}", response_model=AnchorHistoryResponse)
async def get_anchor(
    ocid: str,
    db: AsyncSession = Depends(get_db),
    _: User = require_permission(Permission.READ_NAMED),
):
    """Return all anchor records for a contract (full named context)."""
    records = await get_anchor_history(db, ocid)
    return AnchorHistoryResponse(ocid=ocid, anchors=records)


# ── GET /public/anchors/{ocid} — public anchor record (de-identified) ─────────

@router.get("/public/anchors/{ocid}", response_model=PublicAnchorOut | None)
async def get_public_anchor(ocid: str, db: AsyncSession = Depends(get_db)):
    """
    Public endpoint: return the latest anchor hash + tx for a contract.
    No named data. Used by the public verification portal.
    """
    records = await get_anchor_history(db, ocid)
    if not records:
        raise HTTPException(status_code=404, detail="No anchor record for this contract")
    latest = records[0]
    return PublicAnchorOut(
        contract_ocid=latest.contract_ocid,
        sha256=latest.sha256,
        ledger=latest.ledger,
        ledger_tx=latest.ledger_tx,
        block_ref=latest.block_ref,
        anchored_at=latest.anchored_at,
    )


# ── POST /verify — restricted document verification ───────────────────────────

@router.post("/verify", response_model=VerifyResponse)
async def verify_restricted(
    ocid: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = require_permission(Permission.READ_NAMED),
):
    """Verify an uploaded document against its anchor (named/restricted context)."""
    data = await file.read()
    if len(data) > _MAX_BYTES:
        raise HTTPException(status_code=413, detail=f"File exceeds {_MAX_UPLOAD_MB} MB limit")

    result = await verify_document(db, ocid, data)
    verdict = result["verdict"]

    messages = {
        "match": "Document matches the anchored hash — integrity confirmed.",
        "mismatch": "Document does NOT match the anchored hash — possible tampering.",
        "not_registered": "No anchor record found for this contract OCID.",
    }

    return VerifyResponse(
        verdict=verdict,
        provided_hash=result["provided_hash"],
        anchored_hash=result.get("anchored_hash"),
        anchor=result.get("anchor"),
        message=messages[verdict],
    )
