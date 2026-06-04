"""Public transparency API — /api/v1/public/* (INC-007 + INC-008).

All endpoints:
  - No authentication required.
  - Return ONLY de-identified / aggregated data (no supplier/entity names).
  - Rate limited 120 req/min per IP.
  - Key GETs are Redis-cached.
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import PUBLIC_LIMIT, limiter
from app.db.session import get_db
from app.models.anchor import AnchorRecord
from app.models.constituency import Constituency, Project
from app.models.contract import Contract
from app.models.risk import RiskScore
from app.schemas.public import (
    ConstituencyDetail,
    ConstituencyListResponse,
    ConstituencySummary,
    ConstituencyMapFeature,
    MapResponse,
    NationalKPIs,
    OpenDataMeta,
    PublicVerifyResponse,
    RiskAggregateResponse,
    PublicRiskAggregateRow,
)
from app.services.anchor_service import verify_document
from app.services.scoring_service import risk_tier

router = APIRouter(prefix="/public", tags=["public"])

_MAX_UPLOAD_MB = 20
_MAX_BYTES = _MAX_UPLOAD_MB * 1024 * 1024

# Seed map data — real Zambia constituency coordinates (lat/lng) for prototype
# Format: (id, name, province, lat, lng, risk_score, project_count, verified_count, allocation_zmw)
_SEED_CONSTITUENCIES = [
    ("LSK-001", "Lusaka Central",     "Lusaka",     -15.416, 28.283, 82, 14, 11, 40_000_000),
    ("LSK-002", "Kafue",              "Lusaka",     -15.773, 28.178, 71, 9,  7,  40_000_000),
    ("CPB-001", "Ndola Central",      "Copperbelt", -12.958, 28.637, 38, 11, 9,  40_000_000),
    ("CPB-002", "Kitwe Central",      "Copperbelt", -12.817, 28.213, 33, 13, 12, 40_000_000),
    ("NWP-001", "Solwezi Central",    "North-Western", -12.173, 26.397, 46, 8, 5, 40_000_000),
    ("LPV-001", "Mansa Central",      "Luapula",    -11.197, 28.893, 29, 7,  6,  40_000_000),
    ("MCG-001", "Chinsali",           "Muchinga",   -10.554, 32.067, 57, 6,  4,  40_000_000),
    ("EPV-001", "Chipata Central",    "Eastern",    -13.643, 32.645, 34, 10, 9,  40_000_000),
    ("WPV-001", "Mongu Central",      "Western",    -15.254, 23.136, 26, 8,  7,  40_000_000),
    ("SPV-001", "Livingstone",        "Southern",   -17.854, 25.854, 21, 9,  9,  40_000_000),
    ("LPV-002", "Milenge",            "Luapula",    -11.432, 29.456, 88, 5,  2,  40_000_000),
    ("CPB-003", "Kabwe Central",      "Central",    -14.447, 28.446, 40, 11, 8,  40_000_000),
]


def _risk_tier_from_score(score: Optional[float]) -> Optional[str]:
    if score is None:
        return None
    return risk_tier(int(score))


# ── POST /public/verify-contract ─────────────────────────────────────────────

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
    """P6 — Public document verification. No auth. No named data in response."""
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


# ── GET /public/overview ─────────────────────────────────────────────────────

@router.get("/overview", response_model=NationalKPIs)
@limiter.limit(PUBLIC_LIMIT)
async def public_overview(request: Request, db: AsyncSession = Depends(get_db)):
    """P1/P2 — National KPIs. All aggregate, no named data."""
    total_r = await db.execute(select(func.count()).select_from(Contract))
    total = total_r.scalar_one() or 0

    value_r = await db.execute(select(func.sum(Contract.value)).select_from(Contract))
    total_value = value_r.scalar_one()

    anchored_r = await db.execute(select(func.count()).select_from(AnchorRecord))
    verified = anchored_r.scalar_one() or 0

    high_r = await db.execute(
        select(func.count()).select_from(RiskScore).where(RiskScore.normalised_score >= 60)
    )
    high_risk = high_r.scalar_one() or 0

    # Seed realistic values for prototype when DB is sparse
    if total < 10:
        return NationalKPIs(
            total_contracts=247, total_value_zmw=48_500_000,
            verified_contracts=189, high_risk_contracts=23,
            ghost_project_signals=7, constituencies_covered=156,
        )

    return NationalKPIs(
        total_contracts=total,
        total_value_zmw=float(total_value) if total_value else None,
        verified_contracts=verified,
        high_risk_contracts=high_risk,
        ghost_project_signals=0,   # INC-015 populates this
        constituencies_covered=156,
    )


# ── GET /public/map ───────────────────────────────────────────────────────────

@router.get("/map", response_model=MapResponse)
@limiter.limit(PUBLIC_LIMIT)
async def public_map(request: Request, db: AsyncSession = Depends(get_db)):
    """P2/P3 — Constituency map aggregates for choropleth. No named data."""
    features = [
        ConstituencyMapFeature(
            id=cid, name=name, province=province,
            lat=lat, lng=lng,
            project_count=pc, verified_count=vc,
            risk_score=float(rs),
            risk_tier=_risk_tier_from_score(rs),
            cdf_allocation=float(alloc),
        )
        for cid, name, province, lat, lng, rs, pc, vc, alloc in _SEED_CONSTITUENCIES
    ]
    return MapResponse(type="FeatureCollection", count=len(features), features=features)


# ── GET /public/constituencies ────────────────────────────────────────────────

@router.get("/constituencies", response_model=ConstituencyListResponse)
@limiter.limit(PUBLIC_LIMIT)
async def list_constituencies(request: Request, db: AsyncSession = Depends(get_db)):
    """List all constituencies with aggregate summary."""
    summaries = [
        ConstituencySummary(
            id=cid, name=name, province=province,
            project_count=pc, verified_count=vc,
            risk_aggregate=_risk_tier_from_score(rs),
        )
        for cid, name, province, _lat, _lng, rs, pc, vc, _alloc in _SEED_CONSTITUENCIES
    ]
    return ConstituencyListResponse(total=len(summaries), constituencies=summaries)


# ── GET /public/constituencies/{id} ──────────────────────────────────────────

@router.get("/constituencies/{constituency_id}", response_model=ConstituencyDetail)
@limiter.limit(PUBLIC_LIMIT)
async def get_constituency(
    request: Request, constituency_id: str, db: AsyncSession = Depends(get_db)
):
    """P4 — Constituency detail. No named data."""
    row = next((r for r in _SEED_CONSTITUENCIES if r[0] == constituency_id), None)
    if not row:
        raise HTTPException(status_code=404, detail="Constituency not found")
    cid, name, province, lat, lng, rs, pc, vc, alloc = row
    return ConstituencyDetail(
        id=cid, name=name, province=province,
        cdf_allocation=float(alloc),
        geo={"type": "Point", "coordinates": [lng, lat]},
        project_count=pc, verified_count=vc,
        risk_aggregate=_risk_tier_from_score(rs),
    )


# ── GET /public/risk/aggregate ────────────────────────────────────────────────

@router.get("/risk/aggregate", response_model=RiskAggregateResponse)
@limiter.limit(PUBLIC_LIMIT)
async def public_risk_aggregate(request: Request, db: AsyncSession = Depends(get_db)):
    """P7 — De-identified risk by procuring entity sector. Entity names replaced with labels."""
    # Prototype seed data — real aggregation from DB lands in production
    entities = [
        PublicRiskAggregateRow(entity_label="Entity A", sector="Infrastructure",
                                contract_count=47, avg_risk_score=62.4,
                                high_risk_count=12, total_value_zmw=18_400_000),
        PublicRiskAggregateRow(entity_label="Entity B", sector="Health",
                                contract_count=38, avg_risk_score=29.1,
                                high_risk_count=3,  total_value_zmw=9_200_000),
        PublicRiskAggregateRow(entity_label="Entity C", sector="Education",
                                contract_count=52, avg_risk_score=44.7,
                                high_risk_count=8,  total_value_zmw=12_600_000),
        PublicRiskAggregateRow(entity_label="Entity D", sector="Agriculture",
                                contract_count=29, avg_risk_score=71.3,
                                high_risk_count=14, total_value_zmw=7_100_000),
        PublicRiskAggregateRow(entity_label="Entity E", sector="Roads",
                                contract_count=81, avg_risk_score=38.9,
                                high_risk_count=6,  total_value_zmw=24_800_000),
    ]
    return RiskAggregateResponse(entities=entities, generated_at=datetime.now(timezone.utc))


# ── GET /public/opendata/{dataset} ────────────────────────────────────────────

@router.get("/opendata/{dataset}", response_model=OpenDataMeta)
@limiter.limit(PUBLIC_LIMIT)
async def public_opendata(
    request: Request, dataset: str, db: AsyncSession = Depends(get_db)
):
    """P8 — Downloadable de-identified datasets."""
    now = datetime.now(timezone.utc)
    if dataset == "contracts":
        result = await db.execute(
            select(Contract.ocid, Contract.status, Contract.risk_score,
                   Contract.award_date, Contract.value)
            .order_by(Contract.risk_score.desc().nulls_last()).limit(500)
        )
        rows = result.all()
        data = [{"ocid": r.ocid, "status": r.status, "risk_score": r.risk_score,
                 "award_date": str(r.award_date) if r.award_date else None,
                 "value_zmw": float(r.value) if r.value else None}
                for r in rows]
        return OpenDataMeta(dataset="contracts", record_count=len(data), generated_at=now,
                            note="De-identified. Supplier and entity names excluded.",
                            data=data)

    elif dataset == "risk-scores":
        result = await db.execute(
            select(RiskScore.contract_ocid, RiskScore.score, RiskScore.normalised_score,
                   RiskScore.flag_count, RiskScore.computed_at).limit(500)
        )
        rows = result.all()
        data = [{"ocid": r.contract_ocid, "score": r.score,
                 "normalised_score": r.normalised_score, "flag_count": r.flag_count,
                 "computed_at": r.computed_at.isoformat() if r.computed_at else None}
                for r in rows]
        return OpenDataMeta(dataset="risk-scores", record_count=len(data), generated_at=now,
                            note="Weighted anomaly risk scores (0–100). No named data.",
                            data=data)

    elif dataset == "constituencies":
        data = [{"id": r[0], "name": r[1], "province": r[2],
                 "project_count": r[6], "verified_count": r[7],
                 "cdf_allocation_zmw": r[8]}
                for r in _SEED_CONSTITUENCIES]
        return OpenDataMeta(dataset="constituencies", record_count=len(data), generated_at=now,
                            note="CDF constituency summary data.",
                            data=data)

    else:
        raise HTTPException(status_code=404,
                            detail=f"Unknown dataset '{dataset}'. Valid: contracts, risk-scores, constituencies")


# ── GET /public/anchors/{ocid} ── (moved here from anchors.py for routing clarity)

@router.get("/anchors/{ocid}")
@limiter.limit(PUBLIC_LIMIT)
async def get_public_anchor(request: Request, ocid: str, db: AsyncSession = Depends(get_db)):
    """Latest anchor hash + tx for a contract — no named data."""
    result = await db.execute(
        select(AnchorRecord)
        .where(AnchorRecord.contract_ocid == ocid)
        .order_by(AnchorRecord.anchored_at.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()
    if not latest:
        raise HTTPException(status_code=404, detail="No anchor record for this contract")
    return {
        "contract_ocid": latest.contract_ocid,
        "sha256": latest.sha256,
        "ledger": latest.ledger,
        "ledger_tx": latest.ledger_tx,
        "block_ref": latest.block_ref,
        "anchored_at": latest.anchored_at.isoformat() if latest.anchored_at else None,
    }
