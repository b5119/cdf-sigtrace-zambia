"""Admin console API — /api/v1/admin/* (INC-017). All system_admin only."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import Permission, require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin import (
    HealthResponse, ThresholdsResponse, ThresholdsUpdate, UserCreate, UserListResponse,
    UserOut, UserUpdate, WeightsResponse, WeightsUpdate,
)
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["admin"])


# ── Health (S1) ────────────────────────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
async def health(db: AsyncSession = Depends(get_db),
                 _: User = require_permission(Permission.SYSTEM_ADMIN)):
    return await admin_service.health_check(db)


@router.get("/ledger/nodes")
async def ledger_nodes(db: AsyncSession = Depends(get_db),
                       _: User = require_permission(Permission.SYSTEM_ADMIN)):
    """S6 — Fabric / Polygon / IPFS status."""
    return await admin_service.ledger_status(db)


# ── Users & Roles (S2) ─────────────────────────────────────────────────────────

@router.get("/users", response_model=UserListResponse)
async def list_users(db: AsyncSession = Depends(get_db),
                     _: User = require_permission(Permission.MANAGE_USERS)):
    users = await admin_service.list_users(db)
    return UserListResponse(total=len(users), users=users)


@router.post("/users", response_model=UserOut, status_code=201)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db),
                      _: User = require_permission(Permission.MANAGE_USERS)):
    try:
        user = await admin_service.create_user(
            db, body.name, body.email, body.password, body.role_key, body.institution_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return user


@router.patch("/users/{user_id}", response_model=UserOut)
async def update_user(user_id: str, body: UserUpdate, db: AsyncSession = Depends(get_db),
                      _: User = require_permission(Permission.MANAGE_USERS)):
    try:
        user = await admin_service.update_user(db, user_id, **body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e) else 400, detail=str(e))
    return user


@router.get("/roles")
async def list_roles(db: AsyncSession = Depends(get_db),
                     _: User = require_permission(Permission.MANAGE_USERS)):
    return {"roles": await admin_service.list_roles(db)}


@router.get("/institutions")
async def list_institutions(db: AsyncSession = Depends(get_db),
                            _: User = require_permission(Permission.SYSTEM_ADMIN)):
    return {"institutions": await admin_service.list_institutions(db)}


# ── Check weights (S3) ─────────────────────────────────────────────────────────

@router.get("/config/weights", response_model=WeightsResponse)
async def get_weights(db: AsyncSession = Depends(get_db),
                      _: User = require_permission(Permission.CONFIGURE_WEIGHTS)):
    return WeightsResponse(weights=await admin_service.get_weights(db))


@router.put("/config/weights", response_model=WeightsResponse)
async def update_weights(body: WeightsUpdate, db: AsyncSession = Depends(get_db),
                         current_user: User = require_permission(Permission.CONFIGURE_WEIGHTS)):
    weights = await admin_service.update_weights(db, body.weights, str(current_user.id))
    return WeightsResponse(weights=weights)


# ── Thresholds (S4) ────────────────────────────────────────────────────────────

@router.get("/config/thresholds", response_model=ThresholdsResponse)
async def get_thresholds(db: AsyncSession = Depends(get_db),
                         _: User = require_permission(Permission.CONFIGURE_WEIGHTS)):
    return ThresholdsResponse(thresholds=await admin_service.get_thresholds(db))


@router.put("/config/thresholds", response_model=ThresholdsResponse)
async def update_thresholds(body: ThresholdsUpdate, db: AsyncSession = Depends(get_db),
                            current_user: User = require_permission(Permission.CONFIGURE_WEIGHTS)):
    thresholds = await admin_service.update_thresholds(db, body.thresholds, str(current_user.id))
    return ThresholdsResponse(thresholds=thresholds)
