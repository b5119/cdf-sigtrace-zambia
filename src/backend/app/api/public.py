"""Public transparency API — /api/v1/public/* (INC-007 + INC-008 stub).

INC-007 delivers:
  POST /public/verify-contract   — upload a PDF, get MATCH/MISMATCH/NOT_REGISTERED

INC-008 will extend this router with:
  GET  /public/overview
  GET  /public/constituencies
  GET  /public/constituencies/{id}
  GET  /public/projects
  GET  /public/projects/{id}
  GET  /public/map
  GET  /public/risk/aggregate
  GET  /public/opendata/{dataset}

All public endpoints:
  - No authentication required.
  - Return ONLY de-identified / aggregated data.
  - Rate limited (120 req/min per IP — from rate_limit.py).
  - Cacheable (Redis cache decorator on GET routes — INC-008).
"""
from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from app.core.rate_limit import PUBLIC_LIMIT, limiter
from app.db.session import get_db
from app.schemas.public import PublicVerifyResponse
from app.services.anchor_service import verify_document
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/public", tags=["public"])

_MAX_UPLOAD_MB = 20
_MAX_BYTES = _MAX_UPLOAD_MB * 1024 * 1024

_VERDICT_MESSAGES = {
    "match": (
        "The document matches the anchored hash. "
        "This contract's integrity has been independently verified on the Fabric ledger."
    ),
    "mismatch": (
        "The document does NOT match the anchored hash. "
        "The file may have been altered after anchoring. "
        "Report this to the Office of the Auditor General."
    ),
    "not_registered": (
        "No anchor record was found for this contract. "
        "Either the contract has not been anchored yet, or the OCID is incorrect."
    ),
}


@router.post("/verify-contract", response_model=PublicVerifyResponse)
@limiter.limit(PUBLIC_LIMIT)
async def public_verify_contract(
    request: Request,
    ocid: str,
    file: UploadFile = File(..., description="Signed contract PDF to verify"),
    db: AsyncSession = Depends(get_db),
):
    """
    Public document verification (screen P6).

    Upload a contract PDF and an OCID. The server computes SHA-256,
    compares it against the Fabric-anchored hash, and returns a verdict.

    No authentication required. No named data in the response.
    The uploaded file is discarded after hashing — never stored.
    """
    content_type = file.content_type or ""
    if "pdf" not in content_type and not (file.filename or "").endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Only PDF documents are accepted")

    data = await file.read()
    if len(data) > _MAX_BYTES:
        raise HTTPException(status_code=413, detail=f"File exceeds {_MAX_UPLOAD_MB} MB limit")
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    result = await verify_document(db, ocid, data)
    verdict: str = result["verdict"]
    anchor = result.get("anchor")

    return PublicVerifyResponse(
        verdict=verdict,
        message=_VERDICT_MESSAGES[verdict],
        provided_hash=result["provided_hash"],
        anchored_hash=result.get("anchored_hash"),
        ledger=anchor.ledger if anchor else None,
        ledger_tx=anchor.ledger_tx if anchor else None,
        block_ref=anchor.block_ref if anchor else None,
        anchored_at=anchor.anchored_at if anchor else None,
    )
