"""Tests for risk scoring and two-tier projections (INC-005).

Covers:
- compute_score() unit tests (score formula, normalised, breakdown)
- risk_tier() labelling
- weights_version stability
- Two-tier projection: public caller gets no PII; restricted caller gets full data
- API: /contracts/{ocid}/risk, /contracts, /analysis/run
"""
import json
import os
import uuid
from datetime import date

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.models.contract import Contract, IngestionRun, Supplier
from app.models.anomaly import AnomalyFlag, CheckDefinition
from app.models.risk import RiskScore
from app.services.scoring_service import compute_score, risk_tier, _weights_version
from engine.models import CheckOutput, CheckResult, EngineOutput
from engine.runner import build_config
from tests.conftest import make_role, make_user, bearer

SAMPLE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "ingestion", "sample", "ocds_sample.json"
)


# ── Scoring unit tests ─────────────────────────────────────────────────────────

def _engine_output(ocid: str, outputs: list[CheckOutput]) -> EngineOutput:
    out = EngineOutput(contract_ocid=ocid)
    out.outputs = outputs
    return out


def _flag(check_id: int, key: str, weight: float) -> CheckOutput:
    return CheckOutput(check_id=check_id, check_key=key, result=CheckResult.FLAG,
                       evidence_note="test", weight_applied=weight)


def _ok(check_id: int, key: str) -> CheckOutput:
    return CheckOutput(check_id=check_id, check_key=key, result=CheckResult.OK,
                       evidence_note="ok", weight_applied=0.0)


def _skip(check_id: int, key: str) -> CheckOutput:
    return CheckOutput(check_id=check_id, check_key=key, result=CheckResult.SKIP,
                       evidence_note="skipped", weight_applied=0.0)


DEFAULT_WEIGHTS = {
    "signing": 15.0, "standstill": 20.0, "time_gap": 15.0,
    "forensics": 15.0, "supplier_net": 10.0, "score_var": 5.0,
    "amendment": 10.0, "debarment": 10.0,
}


class TestComputeScore:

    def test_zero_flags_gives_zero_score(self):
        outputs = [_ok(1, "signing"), _ok(2, "standstill")]
        eng = _engine_output("ocds-001", outputs)
        result = compute_score(eng, DEFAULT_WEIGHTS)
        assert result["score"] == 0
        assert result["normalised_score"] == 0
        assert result["flag_count"] == 0

    def test_single_flag_score_equals_weight(self):
        outputs = [_flag(1, "signing", 15.0), _ok(2, "standstill")]
        eng = _engine_output("ocds-001", outputs)
        result = compute_score(eng, DEFAULT_WEIGHTS)
        assert result["score"] == 15
        assert result["flag_count"] == 1

    def test_all_flags_score_is_100(self):
        """All 8 checks flagged → absolute score = 100 (weights sum to 100)."""
        outputs = [
            _flag(1, "signing", 15.0),
            _flag(2, "standstill", 20.0),
            _flag(3, "time_gap", 15.0),
            _flag(4, "forensics", 15.0),
            _flag(5, "supplier_net", 10.0),
            _flag(6, "score_var", 5.0),
            _flag(7, "amendment", 10.0),
            _flag(8, "debarment", 10.0),
        ]
        eng = _engine_output("ocds-001", outputs)
        result = compute_score(eng, DEFAULT_WEIGHTS)
        assert result["score"] == 100
        assert result["normalised_score"] == 100

    def test_normalised_score_adjusts_for_skips(self):
        """If standstill is skipped (20pt), 1 signing flag (15pt) of 80pt applicable = 19%."""
        outputs = [
            _flag(1, "signing", 15.0),
            _skip(2, "standstill"),
            _ok(3, "time_gap"),
            _ok(4, "forensics"),
            _ok(5, "supplier_net"),
            _ok(6, "score_var"),
            _ok(7, "amendment"),
            _ok(8, "debarment"),
        ]
        eng = _engine_output("ocds-001", outputs)
        result = compute_score(eng, DEFAULT_WEIGHTS)
        # applicable_max = 15+15+15+10+5+10+10 = 80
        # normalised = round(15/80*100) = 19
        assert result["normalised_score"] == 19
        assert result["score"] == 15

    def test_breakdown_contains_all_checks(self):
        outputs = [_flag(1, "signing", 15.0), _ok(2, "standstill")]
        eng = _engine_output("ocds-001", outputs)
        result = compute_score(eng, DEFAULT_WEIGHTS)
        assert "signing" in result["breakdown"]
        assert "standstill" in result["breakdown"]
        assert result["breakdown"]["signing"]["result"] == "flag"
        assert result["breakdown"]["standstill"]["result"] == "ok"

    def test_score_capped_at_100(self):
        """Score can't exceed 100 even with misconfigured weights."""
        outputs = [_flag(1, "signing", 200.0)]
        eng = _engine_output("ocds-001", outputs)
        result = compute_score(eng, {"signing": 200.0})
        assert result["score"] == 100
        assert result["normalised_score"] == 100

    def test_weights_version_is_stable(self):
        v1 = _weights_version(DEFAULT_WEIGHTS)
        v2 = _weights_version(DEFAULT_WEIGHTS)
        assert v1 == v2
        assert len(v1) == 8

    def test_weights_version_changes_on_weight_change(self):
        modified = {**DEFAULT_WEIGHTS, "signing": 25.0}
        assert _weights_version(DEFAULT_WEIGHTS) != _weights_version(modified)


class TestRiskTier:

    def test_high_at_60(self):
        assert risk_tier(60) == "high"
        assert risk_tier(100) == "high"

    def test_medium_between_30_and_59(self):
        assert risk_tier(30) == "medium"
        assert risk_tier(59) == "medium"

    def test_low_below_30(self):
        assert risk_tier(0) == "low"
        assert risk_tier(29) == "low"

    def test_custom_threshold(self):
        assert risk_tier(50, high_threshold=50) == "high"
        assert risk_tier(49, high_threshold=50) == "medium"


# ── Two-tier projection tests ─────────────────────────────────────────────────

class TestTwoTierProjection:
    """
    Verify that the public projection contains no named/PII fields
    and restricted projection contains full data.
    These are the core acceptance criteria for INC-005.
    """

    def _make_contract_dict(self):
        return {
            "ocid": "ocds-proj-001",
            "procuring_entity": "Ministry of Health",
            "value": 4_500_000.0,
            "currency": "ZMW",
            "award_date": date(2024, 3, 15),
            "signing_date": date(2024, 4, 2),
            "framework_parent": None,
            "status": "active",
            "risk_score": 35,
        }

    def test_public_projection_excludes_procuring_entity(self):
        from app.core.scoping import scope_response
        data = self._make_contract_dict()
        public = scope_response(data, "anonymous")
        assert "procuring_entity" not in public

    def test_restricted_projection_includes_procuring_entity(self):
        from app.core.scoping import scope_response
        data = self._make_contract_dict()
        restricted = scope_response(data, "oversight_officer")
        assert restricted["procuring_entity"] == "Ministry of Health"

    def test_public_keeps_non_pii_fields(self):
        from app.core.scoping import scope_response
        data = self._make_contract_dict()
        public = scope_response(data, "anonymous")
        assert public["ocid"] == "ocds-proj-001"
        assert public["risk_score"] == 35
        assert public["status"] == "active"

    def test_all_restricted_roles_see_named_data(self):
        from app.core.scoping import scope_response
        data = self._make_contract_dict()
        for role in ["oversight_officer", "analyst", "system_admin", "inst_confirmer"]:
            result = scope_response(data, role)
            assert "procuring_entity" in result, f"{role} should see named data"

    def test_public_roles_stripped(self):
        from app.core.scoping import scope_response
        data = self._make_contract_dict()
        for role in ["anonymous", "community_monitor"]:
            result = scope_response(data, role)
            assert "procuring_entity" not in result, f"{role} must not see named data"


# ── API tests ─────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def admin_role_sc(db):
    return await make_role(db, "system_admin", "System Admin",
                           ["system_admin", "read_named", "read_public"])


@pytest_asyncio.fixture
async def admin_user_sc(db, admin_role_sc):
    return await make_user(db, admin_role_sc, email="admin_sc@sigtrace.zm", password="ScAdmin123!")


@pytest_asyncio.fixture
async def seeded_contract(db):
    """Insert a minimal contract + risk score into the test DB (get-or-create)."""
    # Supplier
    s_result = await db.execute(select(Supplier).where(Supplier.tpin == "9000000001"))
    supplier = s_result.scalar_one_or_none()
    if supplier is None:
        supplier = Supplier(id=uuid.uuid4(), name="Test Supplier Ltd",
                            tpin="9000000001", address="Test Address")
        db.add(supplier)
        await db.flush()

    # Contract
    c_result = await db.execute(select(Contract).where(Contract.ocid == "ocds-score-001"))
    contract = c_result.scalar_one_or_none()
    if contract is None:
        contract = Contract(
            ocid="ocds-score-001",
            procuring_entity="Ministry of Test",
            supplier_id=supplier.id,
            value=5_000_000.0,
            currency="ZMW",
            award_date=date(2024, 3, 15),
            signing_date=None,
            status="active",
            risk_score=15,
            raw_ocds={},
        )
        db.add(contract)
        await db.flush()

    # RiskScore
    rs_result = await db.execute(select(RiskScore).where(RiskScore.contract_ocid == "ocds-score-001"))
    rs = rs_result.scalar_one_or_none()
    if rs is None:
        rs = RiskScore(
            contract_ocid="ocds-score-001",
            score=15, normalised_score=19,
            breakdown={"signing": {"result": "flag", "weight_applied": 15.0, "evidence_note": "test"}},
            flag_count=1, applicable_max=80.0, weights_version="abc12345",
        )
        db.add(rs)

    await db.commit()
    return contract


@pytest.mark.asyncio
async def test_contracts_list_public_no_names(client):
    """Anonymous caller must receive no procuring_entity names."""
    r = await client.get("/api/v1/contracts")
    assert r.status_code == 200
    body = r.json()
    for item in body.get("contracts", []):
        assert "procuring_entity" not in item


@pytest.mark.asyncio
async def test_contracts_list_restricted_has_names(client, admin_user_sc, seeded_contract):
    """Restricted caller receives full named data."""
    r = await client.get("/api/v1/contracts", headers=bearer(admin_user_sc))
    assert r.status_code == 200
    body = r.json()
    names = [c.get("procuring_entity") for c in body.get("contracts", [])]
    assert any(n is not None for n in names)


@pytest.mark.asyncio
async def test_get_contract_requires_auth(client, seeded_contract):
    r = await client.get("/api/v1/contracts/ocds-score-001")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_get_contract_returns_named_data(client, admin_user_sc, seeded_contract):
    r = await client.get("/api/v1/contracts/ocds-score-001", headers=bearer(admin_user_sc))
    assert r.status_code == 200
    assert r.json()["procuring_entity"] == "Ministry of Test"


@pytest.mark.asyncio
async def test_get_contract_not_found(client, admin_user_sc):
    r = await client.get("/api/v1/contracts/does-not-exist", headers=bearer(admin_user_sc))
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_risk_score(client, admin_user_sc, seeded_contract):
    r = await client.get("/api/v1/contracts/ocds-score-001/risk", headers=bearer(admin_user_sc))
    assert r.status_code == 200
    body = r.json()
    assert body["score"] == 15
    assert body["normalised_score"] == 19
    assert body["tier"] == "low"
    assert body["flag_count"] == 1
    assert "signing" in body["breakdown"]


@pytest.mark.asyncio
async def test_get_risk_score_not_found(client, admin_user_sc):
    r = await client.get("/api/v1/contracts/no-such-ocid/risk", headers=bearer(admin_user_sc))
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_analysis_run_requires_admin(client, db):
    anon_role = await make_role(db, "analyst", "Analyst", ["read_named", "read_public"])
    anon_user = await make_user(db, anon_role, email="analyst_sc@sigtrace.zm", password="Analyst123!")
    r = await client.post("/api/v1/analysis/run", json={}, headers=bearer(anon_user))
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_analysis_run_returns_summary(client, admin_user_sc, seeded_contract):
    """POST /analysis/run should return a summary dict (even if no contracts are scored
    because the test DB engine can't import the anomaly engine in the service layer —
    the endpoint itself must respond correctly)."""
    r = await client.post("/api/v1/analysis/run", json={"ocids": []}, headers=bearer(admin_user_sc))
    assert r.status_code == 200
    body = r.json()
    assert "total" in body
    assert "high_risk" in body
    assert "errors" in body
