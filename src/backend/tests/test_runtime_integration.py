"""Regression tests for runtime-only bugs found by running the live server (not just unit tests).

These guard the three bugs that 390 unit tests missed because tests use pytest.ini's
pythonpath and call services directly:
  1. /analysis/run must score synchronously (no Celery worker in prototype).
  2. The anomaly engine must be importable from the backend runtime.
  3. /contracts/{ocid}/checks must not 500 from an async lazy-load.
"""
import uuid
from datetime import date

import pytest
import pytest_asyncio

from tests.conftest import bearer, make_role, make_user


@pytest_asyncio.fixture
async def admin(db):
    role = await make_role(db, "system_admin", "System Admin",
                           ["read_public", "read_named", "system_admin", "configure_weights"])
    return await make_user(db, role, email="rt_admin@oag.gov.zm", password="AdminPass123!")


async def _seed_contract_and_checks(db, ocid):
    from app.models.anomaly import CheckDefinition
    from app.models.contract import Contract, Supplier
    from sqlalchemy import select
    if not (await db.execute(select(CheckDefinition))).scalars().first():
        for cid, key in [(1,"signing"),(2,"standstill"),(3,"time_gap"),(4,"forensics"),
                         (5,"supplier_net"),(6,"score_var"),(7,"amendment"),(8,"debarment")]:
            db.add(CheckDefinition(id=cid, key=key, name=key, basis="t", severity="high", weight=10.0, enabled=True))
        await db.flush()
    if (await db.execute(select(Contract).where(Contract.ocid == ocid))).scalar_one_or_none():
        return
    sup = Supplier(id=uuid.uuid4(), name=f"RT {ocid}", tpin=f"40{abs(hash(ocid))%10**8:08d}", address="x")
    db.add(sup); await db.flush()
    db.add(Contract(ocid=ocid, procuring_entity="Min", supplier_id=sup.id,
                    value=3_000_000.0, currency="ZMW", award_date=date(2024,1,1),
                    signing_date=None, status="active", raw_ocds={}))
    await db.commit()


def test_engine_importable_from_runtime():
    """The standalone anomaly engine must import without pytest.ini's pythonpath."""
    import importlib
    mod = importlib.import_module("engine.runner")
    assert hasattr(mod, "run_checks")


@pytest.mark.asyncio
async def test_analysis_run_scores_synchronously(client, admin, db):
    """POST /analysis/run must create RiskScore rows immediately (no Celery needed)."""
    await _seed_contract_and_checks(db, "ocds-rt-sync")
    r = await client.post("/api/v1/analysis/run", json={"ocids": ["ocds-rt-sync"]}, headers=bearer(admin))
    assert r.status_code == 200
    # The risk score is now retrievable — proves scoring actually ran
    risk = await client.get("/api/v1/contracts/ocds-rt-sync/risk", headers=bearer(admin))
    assert risk.status_code == 200
    assert risk.json()["score"] >= 0
    assert risk.json()["flag_count"] >= 1  # missing signing date flags


@pytest.mark.asyncio
async def test_contract_checks_endpoint_no_500(client, admin, db):
    """GET /contracts/{ocid}/checks must return the 8 results, not 500."""
    await _seed_contract_and_checks(db, "ocds-rt-checks")
    await client.post("/api/v1/analysis/run", json={"ocids": ["ocds-rt-checks"]}, headers=bearer(admin))
    r = await client.get("/api/v1/contracts/ocds-rt-checks/checks", headers=bearer(admin))
    assert r.status_code == 200
    checks = r.json()
    assert isinstance(checks, list)
    assert len(checks) == 8
    # check_key resolved via the eager-loaded relationship (the bug was a lazy-load 500)
    assert all(c["check_key"] for c in checks)
    assert any(c["check_key"] == "signing" and c["result"] == "flag" for c in checks)
