"""Tests for the OCDS ingestion pipeline (INC-002).

Acceptance criteria:
- Sample loads into Contract/Supplier tables correctly.
- Re-running the same sample does NOT duplicate records.
- Run history is visible via the API.
- Error records don't crash the pipeline.
- Framework call-off detection maps framework_parent.
- Missing signing_date is preserved as None.
"""
import json
import os
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.models.contract import Contract, IngestionRun, Supplier
from tests.conftest import make_role, make_user, bearer

# Path to the sample fixture
SAMPLE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "ingestion", "sample", "ocds_sample.json"
)


@pytest.fixture
def sample_records():
    with open(SAMPLE_PATH, "r") as f:
        package = json.load(f)
    return package["records"]


# --- Normalise unit tests ---

def test_normalise_clean_contract(sample_records):
    from ingestion.normalise import normalise_record
    record = next(r for r in sample_records if r["ocid"] == "ocds-zm-zppa-001")
    contract, supplier = normalise_record(record)

    assert contract["ocid"] == "ocds-zm-zppa-001"
    assert contract["procuring_entity"] == "Ministry of Health"
    assert contract["value"] == 4500000
    assert contract["currency"] == "ZMW"
    assert contract["signing_date"] is not None
    assert contract["award_date"] is not None
    assert contract["framework_parent"] is None
    assert contract["content_hash"] is not None
    assert len(contract["content_hash"]) == 64

    assert supplier is not None
    assert supplier["name"] == "Acme Medical Supplies Ltd"
    assert supplier["tpin"] == "1000012345"


def test_normalise_missing_signing_date(sample_records):
    from ingestion.normalise import normalise_record
    record = next(r for r in sample_records if r["ocid"] == "ocds-zm-zppa-002")
    contract, _ = normalise_record(record)
    assert contract["signing_date"] is None


def test_normalise_framework_calloff(sample_records):
    from ingestion.normalise import normalise_record
    record = next(r for r in sample_records if r["ocid"] == "ocds-zm-zppa-004")
    contract, _ = normalise_record(record)
    assert contract["framework_parent"] == "ocds-zm-zppa-fw-001"


def test_normalise_standstill_violation(sample_records):
    """Award 2024-06-25, signed 2024-06-26 = 1 day standstill — just data, check flags in engine."""
    from ingestion.normalise import normalise_record
    from datetime import date
    record = next(r for r in sample_records if r["ocid"] == "ocds-zm-zppa-003")
    contract, _ = normalise_record(record)
    assert contract["award_date"] == date(2024, 6, 25)
    assert contract["signing_date"] == date(2024, 6, 26)


def test_content_hash_stable(sample_records):
    """Same record → same hash on repeated calls."""
    from ingestion.normalise import normalise_record
    record = sample_records[0]
    c1, _ = normalise_record(record)
    c2, _ = normalise_record(record)
    assert c1["content_hash"] == c2["content_hash"]


def test_content_hash_changes_on_mutation(sample_records):
    """Mutating the record → different hash."""
    import copy
    from ingestion.normalise import normalise_record
    record = copy.deepcopy(sample_records[0])
    c1, _ = normalise_record(record)
    record["releases"][0]["contracts"][0]["value"]["amount"] = 9999999
    c2, _ = normalise_record(record)
    assert c1["content_hash"] != c2["content_hash"]


# --- Load / integration tests (in-memory SQLite via conftest) ---

@pytest_asyncio.fixture
async def admin_role_ing(db):
    return await make_role(db, "system_admin", "System Administrator",
                           ["system_admin", "read_public"])


@pytest_asyncio.fixture
async def admin_user_ing(db, admin_role_ing):
    return await make_user(db, admin_role_ing, email="admin2@sigtrace.zm", password="Admin2Pass!")


@pytest.mark.asyncio
async def test_load_sample_creates_contracts(db, sample_records):
    from ingestion.normalise import normalise_records
    from ingestion.load import run_load
    from app.models.contract import IngestionRun

    normalised = normalise_records(sample_records)
    run = IngestionRun(id=uuid.uuid4(), source="sample", status="running")
    db.add(run)
    await db.flush()

    await run_load(db, normalised, run)

    result = await db.execute(select(Contract))
    contracts = result.scalars().all()
    assert len(contracts) == 5
    assert run.status == "complete"
    assert run.records_loaded == 5
    assert run.records_updated == 0
    assert run.records_skipped == 0


@pytest.mark.asyncio
async def test_load_idempotent_no_duplicates(db, sample_records):
    """Running the same sample twice must NOT duplicate contracts."""
    from ingestion.normalise import normalise_records
    from ingestion.load import run_load
    from app.models.contract import IngestionRun

    normalised = normalise_records(sample_records)

    # First run
    run1 = IngestionRun(id=uuid.uuid4(), source="sample", status="running")
    db.add(run1)
    await db.flush()
    await run_load(db, normalised, run1)

    # Second run — same data
    run2 = IngestionRun(id=uuid.uuid4(), source="sample", status="running")
    db.add(run2)
    await db.flush()
    await run_load(db, normalised, run2)

    result = await db.execute(select(Contract))
    contracts = result.scalars().all()
    assert len(contracts) == 5  # still 5, not 10
    assert run2.records_skipped == 5
    assert run2.records_loaded == 0


@pytest.mark.asyncio
async def test_load_update_on_changed_content(db, sample_records):
    """A changed contract (new content_hash) triggers an update, not a duplicate."""
    import copy
    from ingestion.normalise import normalise_records
    from ingestion.load import run_load
    from app.models.contract import IngestionRun

    # First load
    normalised = normalise_records(sample_records)
    run1 = IngestionRun(id=uuid.uuid4(), source="sample", status="running")
    db.add(run1)
    await db.flush()
    await run_load(db, normalised, run1)

    # Mutate one record's value
    mutated = copy.deepcopy(sample_records)
    mutated[0]["releases"][0]["contracts"][0]["value"]["amount"] = 9999999
    normalised2 = normalise_records(mutated)

    run2 = IngestionRun(id=uuid.uuid4(), source="sample-mutated", status="running")
    db.add(run2)
    await db.flush()
    await run_load(db, normalised2, run2)

    result = await db.execute(select(Contract))
    contracts = result.scalars().all()
    assert len(contracts) == 5  # still 5
    assert run2.records_updated == 1
    assert run2.records_skipped == 4


@pytest.mark.asyncio
async def test_supplier_upserted_not_duplicated(db, sample_records):
    """Running sample twice — no duplicate supplier rows."""
    from ingestion.normalise import normalise_records
    from ingestion.load import run_load
    from app.models.contract import IngestionRun

    normalised = normalise_records(sample_records)
    for i in range(2):
        run = IngestionRun(id=uuid.uuid4(), source="sample", status="running")
        db.add(run)
        await db.flush()
        await run_load(db, normalised, run)

    result = await db.execute(select(Supplier))
    suppliers = result.scalars().all()
    # 5 contracts, each with 1 supplier → 5 unique suppliers
    assert len(suppliers) == 5


# --- API endpoint tests ---

@pytest.mark.asyncio
async def test_ingestion_runs_list_requires_auth(client):
    r = await client.get("/api/v1/ingestion/runs")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_ingestion_runs_list_returns_data(client, admin_user_ing):
    headers = bearer(admin_user_ing)
    r = await client.get("/api/v1/ingestion/runs", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert "runs" in body
    assert "total" in body


@pytest.mark.asyncio
async def test_trigger_run_creates_record(client, admin_user_ing, db):
    headers = bearer(admin_user_ing)
    r = await client.post("/api/v1/ingestion/runs", json={"source": "sample"}, headers=headers)
    assert r.status_code == 202
    body = r.json()
    assert body["status"] == "running"
    assert body["source"] == "sample"
    assert "id" in body


@pytest.mark.asyncio
async def test_get_run_not_found(client, admin_user_ing):
    headers = bearer(admin_user_ing)
    fake_id = str(uuid.uuid4())
    r = await client.get(f"/api/v1/ingestion/runs/{fake_id}", headers=headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_run_returns_detail(client, admin_user_ing, db):
    headers = bearer(admin_user_ing)
    # Create a run
    post_r = await client.post("/api/v1/ingestion/runs", json={"source": "test"}, headers=headers)
    run_id = post_r.json()["id"]
    # Retrieve it
    get_r = await client.get(f"/api/v1/ingestion/runs/{run_id}", headers=headers)
    assert get_r.status_code == 200
    assert get_r.json()["id"] == run_id
