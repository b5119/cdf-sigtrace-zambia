"""Admin service (INC-017): weights, thresholds, users, health, ledger."""
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.models.anomaly import CheckDefinition
from app.models.config import Config
from app.models.user import Institution, Role, User

log = logging.getLogger(__name__)

DEFAULT_THRESHOLDS = {
    "standstill_days": 14,
    "time_gap_min_days": 1,
    "amendment_cap_pct": 15.0,
    "ghost_window_days": settings.GHOST_WINDOW_DAYS,
    "high_risk_threshold": 60,
}


# ── Check weights ──────────────────────────────────────────────────────────────

async def get_weights(db: AsyncSession) -> list[dict]:
    result = await db.execute(select(CheckDefinition).order_by(CheckDefinition.id))
    return [
        {"id": c.id, "key": c.key, "name": c.name, "weight": c.weight,
         "severity": c.severity, "enabled": c.enabled}
        for c in result.scalars().all()
    ]


async def update_weights(db: AsyncSession, weights: dict[str, float], updated_by: str) -> list[dict]:
    """Update CheckDefinition weights by key. Scoring re-reads these on next analysis."""
    result = await db.execute(select(CheckDefinition))
    defs = {c.key: c for c in result.scalars().all()}
    for key, w in weights.items():
        if key in defs:
            defs[key].weight = float(w)
    await db.commit()
    log.info("Check weights updated by %s: %s", updated_by, weights)
    return await get_weights(db)


# ── Thresholds ─────────────────────────────────────────────────────────────────

async def get_thresholds(db: AsyncSession) -> dict:
    result = await db.execute(select(Config).where(Config.key == "thresholds"))
    cfg = result.scalar_one_or_none()
    if cfg and cfg.value:
        return {**DEFAULT_THRESHOLDS, **cfg.value}
    return dict(DEFAULT_THRESHOLDS)


async def update_thresholds(db: AsyncSession, thresholds: dict, updated_by: str) -> dict:
    result = await db.execute(select(Config).where(Config.key == "thresholds"))
    cfg = result.scalar_one_or_none()
    merged = {**DEFAULT_THRESHOLDS, **(cfg.value if cfg else {}), **thresholds}
    if cfg:
        cfg.value = merged
        cfg.updated_by = updated_by
        cfg.version += 1
    else:
        cfg = Config(key="thresholds", value=merged, updated_by=updated_by, version=1)
        db.add(cfg)
    await db.commit()
    log.info("Thresholds updated by %s: %s", updated_by, thresholds)
    return merged


# ── Users ──────────────────────────────────────────────────────────────────────

async def list_users(db: AsyncSession) -> list[dict]:
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [
        {"id": str(u.id), "name": u.name, "email": u.email,
         "role": u.role.key if u.role else None,
         "institution_id": str(u.institution_id) if u.institution_id else None,
         "active": u.active, "mfa_enabled": u.mfa_enabled,
         "last_login": u.last_login.isoformat() if u.last_login else None}
        for u in users
    ]


async def create_user(db: AsyncSession, name: str, email: str, password: str,
                      role_key: str, institution_id: str | None = None) -> dict:
    # Look up role
    role_result = await db.execute(select(Role).where(Role.key == role_key))
    role = role_result.scalar_one_or_none()
    if not role:
        raise ValueError(f"Unknown role '{role_key}'")
    # Check email uniqueness
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        raise ValueError("Email already registered")

    user = User(
        id=uuid.uuid4(), name=name, email=email, password_hash=hash_password(password),
        role_id=role.id, institution_id=uuid.UUID(institution_id) if institution_id else None,
        active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": str(user.id), "name": user.name, "email": user.email,
            "role": role_key, "active": user.active}


async def update_user(db: AsyncSession, user_id: str, **fields) -> dict:
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")
    if "name" in fields and fields["name"] is not None:
        user.name = fields["name"]
    if "active" in fields and fields["active"] is not None:
        user.active = fields["active"]
    if fields.get("role_key"):
        role_result = await db.execute(select(Role).where(Role.key == fields["role_key"]))
        role = role_result.scalar_one_or_none()
        if not role:
            raise ValueError(f"Unknown role '{fields['role_key']}'")
        user.role_id = role.id
    await db.commit()
    await db.refresh(user)
    return {"id": str(user.id), "name": user.name, "email": user.email,
            "role": user.role.key if user.role else None, "active": user.active}


async def list_roles(db: AsyncSession) -> list[dict]:
    result = await db.execute(select(Role).order_by(Role.id))
    return [{"id": r.id, "key": r.key, "name": r.name, "permissions": r.permissions}
            for r in result.scalars().all()]


async def list_institutions(db: AsyncSession) -> list[dict]:
    result = await db.execute(select(Institution).order_by(Institution.name))
    return [{"id": str(i.id), "name": i.name, "type": i.type,
             "data_sharing_agreement_ref": i.data_sharing_agreement_ref}
            for i in result.scalars().all()]


# ── Health & ledger status ─────────────────────────────────────────────────────

async def health_check(db: AsyncSession) -> dict:
    """Probe component status. DB is probed live; ledgers report mock/real mode."""
    components = {}
    # DB — live probe
    try:
        await db.execute(select(func.count()).select_from(User))
        components["database"] = "ok"
    except Exception:
        components["database"] = "error"
    # Redis — config presence (live probe at INC-020)
    components["redis"] = "configured" if settings.REDIS_URL else "not_configured"
    # Fabric
    components["fabric"] = "mock" if settings.FABRIC_MOCK_MODE else "live"
    # Polygon
    components["polygon"] = "mock" if settings.POLYGON_MOCK_MODE else "live"
    # IPFS
    components["ipfs"] = "mock" if settings.IPFS_MOCK_MODE else "live"
    # Anomaly engine — always available (in-process)
    components["anomaly_engine"] = "ok"

    overall = "ok" if components["database"] == "ok" else "degraded"
    return {"status": overall, "components": components,
            "checked_at": datetime.now(timezone.utc).isoformat()}


async def ledger_status(db: AsyncSession) -> dict:
    from app.models.anchor import AnchorRecord
    from app.models.pulse import PulseSubmission

    anchor_count = (await db.execute(select(func.count()).select_from(AnchorRecord))).scalar_one()
    onchain_count = (await db.execute(
        select(func.count()).select_from(PulseSubmission).where(PulseSubmission.onchain_tx.isnot(None))
    )).scalar_one()
    return {
        "fabric": {"mode": "mock" if settings.FABRIC_MOCK_MODE else "live",
                   "channel": settings.FABRIC_CHANNEL, "anchored_contracts": anchor_count},
        "polygon": {"mode": "mock" if settings.POLYGON_MOCK_MODE else "live",
                    "contract_address": settings.POLYGON_CONTRACT_ADDRESS or "(not deployed)",
                    "confirmed_submissions": onchain_count},
        "ipfs": {"mode": "mock" if settings.IPFS_MOCK_MODE else "live",
                 "gateway": settings.IPFS_GATEWAY_URL},
    }
