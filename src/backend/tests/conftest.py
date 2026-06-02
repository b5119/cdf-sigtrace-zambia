"""Shared pytest fixtures for backend tests."""
import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import event

from app.core.config import settings
from app.core.security import hash_password, create_access_token
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import Institution, Role, User, RefreshToken

# --- In-memory SQLite for fast unit tests (no Postgres required) ---
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = lambda: db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# --- Seed helpers ---

async def make_role(db: AsyncSession, key: str, name: str, permissions: list[str]) -> Role:
    from sqlalchemy import select as sa_select
    result = await db.execute(sa_select(Role).where(Role.key == key))
    role = result.scalar_one_or_none()
    if role is None:
        role = Role(key=key, name=name, permissions=permissions)
        db.add(role)
        await db.flush()
    return role


async def make_user(
    db: AsyncSession,
    role: Role,
    email: str = "test@example.com",
    password: str = "password123",
    mfa_enabled: bool = False,
    institution: Institution | None = None,
) -> User:
    from sqlalchemy import select as sa_select
    result = await db.execute(sa_select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            id=uuid.uuid4(),
            name="Test User",
            email=email,
            password_hash=hash_password(password),
            role_id=role.id,
            mfa_enabled=mfa_enabled,
            institution_id=institution.id if institution else None,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


def bearer(user: User) -> dict:
    token = create_access_token(str(user.id), user.role.key, None)
    return {"Authorization": f"Bearer {token}"}
