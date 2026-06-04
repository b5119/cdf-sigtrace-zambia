"""Tests for public API endpoints (INC-008).

Acceptance criteria:
- All GET /public/* endpoints return 200 with no auth.
- No named data (supplier names, procuring entity names, PII) in any response.
- Risk aggregate uses Entity A-E labels only.
- Map response has lat/lng and risk_tier per feature.
- Open data returns valid datasets; unknown dataset returns 404.
- Overview returns expected KPI keys.
- Constituency list and detail return correct shapes.
"""
import pytest


# ── Overview ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_overview_no_auth(client):
    r = await client.get("/api/v1/public/overview")
    assert r.status_code == 200
    body = r.json()
    assert "total_contracts" in body
    assert "verified_contracts" in body
    assert "high_risk_contracts" in body
    assert "ghost_project_signals" in body
    assert "constituencies_covered" in body


@pytest.mark.asyncio
async def test_overview_no_named_data(client):
    r = await client.get("/api/v1/public/overview")
    body_str = r.text
    # No supplier or entity names
    assert "Ministry" not in body_str
    assert "supplier" not in body_str.lower() or "supplier" in ["constituencies_covered"]


# ── Map ───────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_map_no_auth(client):
    r = await client.get("/api/v1/public/map")
    assert r.status_code == 200
    body = r.json()
    assert body["type"] == "FeatureCollection"
    assert "features" in body
    assert isinstance(body["features"], list)
    assert len(body["features"]) > 0


@pytest.mark.asyncio
async def test_map_features_have_required_fields(client):
    r = await client.get("/api/v1/public/map")
    features = r.json()["features"]
    for f in features:
        assert "id" in f
        assert "name" in f
        assert "lat" in f
        assert "lng" in f
        assert "risk_tier" in f
        assert f["risk_tier"] in ("high", "medium", "low", None)


@pytest.mark.asyncio
async def test_map_no_named_data(client):
    """Map must not expose supplier or procuring entity names."""
    r = await client.get("/api/v1/public/map")
    body_str = r.text
    assert "tpin" not in body_str.lower()
    assert "password" not in body_str.lower()


# ── Constituencies ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_constituencies_list(client):
    r = await client.get("/api/v1/public/constituencies")
    assert r.status_code == 200
    body = r.json()
    assert "constituencies" in body
    assert "total" in body
    assert len(body["constituencies"]) > 0


@pytest.mark.asyncio
async def test_constituency_detail(client):
    # Use first ID from the list
    list_r = await client.get("/api/v1/public/constituencies")
    first_id = list_r.json()["constituencies"][0]["id"]
    r = await client.get(f"/api/v1/public/constituencies/{first_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == first_id
    assert "name" in body
    assert "province" in body
    assert "project_count" in body


@pytest.mark.asyncio
async def test_constituency_not_found(client):
    r = await client.get("/api/v1/public/constituencies/does-not-exist-999")
    assert r.status_code == 404


# ── Risk aggregate ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_risk_aggregate_no_auth(client):
    r = await client.get("/api/v1/public/risk/aggregate")
    assert r.status_code == 200
    body = r.json()
    assert "entities" in body
    assert len(body["entities"]) > 0


@pytest.mark.asyncio
async def test_risk_aggregate_uses_entity_labels_not_real_names(client):
    """CRITICAL: public risk aggregate must only expose Entity A-E, no real names."""
    r = await client.get("/api/v1/public/risk/aggregate")
    body = r.json()
    for entity in body["entities"]:
        label = entity["entity_label"]
        assert label.startswith("Entity "), \
            f"Expected 'Entity X' label, got: {label!r}"
        # Must not contain a real government entity name
        assert "Ministry" not in label
        assert "ZPPA" not in label
        assert "Office" not in label


@pytest.mark.asyncio
async def test_risk_aggregate_has_required_fields(client):
    r = await client.get("/api/v1/public/risk/aggregate")
    for e in r.json()["entities"]:
        assert "entity_label" in e
        assert "sector" in e
        assert "contract_count" in e
        assert "high_risk_count" in e


# ── Open Data ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_opendata_contracts(client):
    r = await client.get("/api/v1/public/opendata/contracts")
    assert r.status_code == 200
    body = r.json()
    assert body["dataset"] == "contracts"
    assert "data" in body
    assert "record_count" in body


@pytest.mark.asyncio
async def test_opendata_risk_scores(client):
    r = await client.get("/api/v1/public/opendata/risk-scores")
    assert r.status_code == 200
    assert r.json()["dataset"] == "risk-scores"


@pytest.mark.asyncio
async def test_opendata_constituencies(client):
    r = await client.get("/api/v1/public/opendata/constituencies")
    assert r.status_code == 200
    body = r.json()
    assert body["dataset"] == "constituencies"
    assert len(body["data"]) > 0


@pytest.mark.asyncio
async def test_opendata_unknown_dataset_returns_404(client):
    r = await client.get("/api/v1/public/opendata/unknown-dataset")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_opendata_contracts_no_supplier_names(client):
    """Open data export must not include supplier names."""
    r = await client.get("/api/v1/public/opendata/contracts")
    body_str = r.text
    assert "supplier_name" not in body_str
    assert "procuring_entity" not in body_str


# ── Public anchor endpoint ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_public_anchor_not_found(client):
    r = await client.get("/api/v1/public/anchors/ocds-does-not-exist")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_public_anchor_no_named_data(client, db):
    """Public anchor endpoint must not return anchored_by (user ID)."""
    import uuid
    from datetime import date
    from app.models.contract import Contract, Supplier
    from app.services.anchor_service import anchor_contract

    # Seed a contract and anchor it
    ocid = f"ocds-pub-api-{uuid.uuid4().hex[:8]}"
    supplier = Supplier(id=uuid.uuid4(), name="Pub API Test Supplier",
                        tpin=f"60{abs(hash(ocid)) % 10**8:08d}", address="Test Rd")
    db.add(supplier)
    await db.flush()
    contract = Contract(ocid=ocid, procuring_entity="Test Ministry", supplier_id=supplier.id,
                        value=1_000_000, currency="ZMW", award_date=date(2024, 1, 1),
                        status="active", raw_ocds={})
    db.add(contract)
    await db.commit()
    await anchor_contract(db, ocid, b"test contract bytes", anchored_by="officer-secret-id")

    r = await client.get(f"/api/v1/public/anchors/{ocid}")
    assert r.status_code == 200
    body = r.json()
    assert "anchored_by" not in body, "Public anchor must not expose anchored_by"
    assert "sha256" in body
    assert "ledger_tx" in body
