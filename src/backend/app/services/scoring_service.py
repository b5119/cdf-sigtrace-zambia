"""Risk scoring service (INC-005).

Computes the 0-100 risk score from an EngineOutput and persists a RiskScore record.

Scoring formula
───────────────
absolute_score   = Σ weight_applied  for all FLAG checks           (0-100, weights sum to 100)
applicable_max   = Σ weight          for all non-SKIP checks
normalised_score = round(absolute_score / applicable_max * 100)    if applicable_max > 0
                   else 0

The absolute score is stored on Contract.risk_score for fast sorting/filtering.
The normalised score accounts for cases where many checks are skipped (e.g. a
framework call-off has several checks skipped, so its applicable max is lower).

Both scores are stored in RiskScore.breakdown for full auditability.
"""
import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contract import Contract
from app.models.risk import RiskScore

log = logging.getLogger(__name__)

# Tier labels match the high_risk_threshold config key
TIER_HIGH   = "high"
TIER_MEDIUM = "medium"
TIER_LOW    = "low"


def _weights_version(weights: dict) -> str:
    """Short hash of the weights dict — used to track config changes."""
    raw = json.dumps(weights, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:8]


def compute_score(engine_output, weights: dict) -> dict:
    """
    Pure function: compute score from EngineOutput and current weights.
    Returns a dict suitable for constructing a RiskScore record.
    """
    from engine.models import CheckResult

    absolute = 0.0
    applicable_max = 0.0
    breakdown = {}

    for out in engine_output.outputs:
        check_weight = weights.get(out.check_key, out.weight_applied or 0.0)
        if out.result == CheckResult.FLAG:
            absolute += out.weight_applied
            applicable_max += check_weight
        elif out.result == CheckResult.OK:
            applicable_max += check_weight
        # SKIP contributes nothing to either numerator or denominator

        breakdown[out.check_key] = {
            "result": str(out.result),
            "weight_applied": out.weight_applied,
            "evidence_note": out.evidence_note,
        }

    normalised = round(absolute / applicable_max * 100) if applicable_max > 0 else 0
    normalised = min(100, normalised)
    absolute_int = min(100, int(round(absolute)))

    return {
        "score": absolute_int,
        "normalised_score": normalised,
        "breakdown": breakdown,
        "flag_count": engine_output.flag_count,
        "applicable_max": applicable_max,
        "weights_version": _weights_version(weights),
    }


def risk_tier(score: int, high_threshold: int = 60) -> str:
    """Return 'high' | 'medium' | 'low' label for a given score."""
    if score >= high_threshold:
        return TIER_HIGH
    if score >= 30:
        return TIER_MEDIUM
    return TIER_LOW


async def score_contract(db: AsyncSession, ocid: str) -> dict:
    """
    Run the full engine + scoring pipeline for one contract, persist results.
    Returns a scoring summary dict.
    """
    from app.services.anomaly_service import analyse_contract

    # Run checks (this also updates Contract.risk_score with the raw absolute score)
    engine_summary = await analyse_contract(db, ocid)

    # Load the engine output to compute the detailed score
    from engine.runner import run_checks, build_config
    from app.services.anomaly_service import _contract_to_dict, _load_config

    result = await db.execute(select(Contract).where(Contract.ocid == ocid))
    contract = result.scalar_one_or_none()
    if not contract:
        raise ValueError(f"Contract {ocid!r} not found")

    config = await _load_config(db)
    contract_dict = _contract_to_dict(contract)
    engine_out = run_checks(contract_dict, config)

    score_data = compute_score(engine_out, config.get("weights", {}))

    # Upsert RiskScore
    existing = await db.execute(select(RiskScore).where(RiskScore.contract_ocid == ocid))
    rs = existing.scalar_one_or_none()
    if rs:
        rs.score = score_data["score"]
        rs.normalised_score = score_data["normalised_score"]
        rs.breakdown = score_data["breakdown"]
        rs.flag_count = score_data["flag_count"]
        rs.applicable_max = score_data["applicable_max"]
        rs.weights_version = score_data["weights_version"]
        rs.computed_at = datetime.now(timezone.utc)
    else:
        rs = RiskScore(contract_ocid=ocid, **score_data)
        db.add(rs)

    # Keep Contract.risk_score in sync with the absolute score
    contract.risk_score = score_data["score"]
    await db.commit()

    tier = risk_tier(score_data["normalised_score"])
    log.info(
        "Scored contract %s — score=%d normalised=%d tier=%s flags=%d",
        ocid, score_data["score"], score_data["normalised_score"], tier, score_data["flag_count"],
    )
    return {
        "ocid": ocid,
        "score": score_data["score"],
        "normalised_score": score_data["normalised_score"],
        "tier": tier,
        "flag_count": score_data["flag_count"],
        "applicable_max": score_data["applicable_max"],
        "weights_version": score_data["weights_version"],
        "breakdown": score_data["breakdown"],
    }


async def score_all_contracts(db: AsyncSession) -> dict:
    """Score every contract in the DB. Returns aggregate summary."""
    result = await db.execute(select(Contract.ocid))
    ocids = [row[0] for row in result.all()]

    high = medium = low = errors = 0
    for ocid in ocids:
        try:
            s = await score_contract(db, ocid)
            tier = s["tier"]
            if tier == TIER_HIGH:
                high += 1
            elif tier == TIER_MEDIUM:
                medium += 1
            else:
                low += 1
        except Exception as e:
            log.error("Failed to score %s: %s", ocid, e)
            errors += 1

    return {
        "total": len(ocids),
        "high_risk": high,
        "medium_risk": medium,
        "low_risk": low,
        "errors": errors,
    }
