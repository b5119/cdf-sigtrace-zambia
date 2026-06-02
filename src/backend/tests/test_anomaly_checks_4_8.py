"""Tests for anomaly engine checks 4–8 (INC-004).

Each check: ≥1 FLAG, ≥1 OK, ≥1 SKIP (false-positive safeguard).
"""
import json
import os
from datetime import date

import pytest

from engine.checks.check_04_forensics import ForensicsCheck
from engine.checks.check_05_supplier_network import SupplierNetworkCheck
from engine.checks.check_06_score_variance import ScoreVarianceCheck
from engine.checks.check_07_amendment import AmendmentCheck
from engine.checks.check_08_debarment import DebarmentCheck
from engine.models import CheckResult
from engine.runner import build_config, run_checks

CFG = build_config()

SAMPLE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "ingestion", "sample", "ocds_sample.json"
)


@pytest.fixture
def sample_contracts():
    with open(SAMPLE_PATH) as f:
        pkg = json.load(f)
    from ingestion.normalise import normalise_records
    return {c["ocid"]: c for c, _ in normalise_records(pkg["records"])}


# ── helpers ────────────────────────────────────────────────────────────────────

def contract(
    ocid="test-001",
    value=5_000_000.0,
    award_date=date(2024, 3, 15),
    signing_date=date(2024, 4, 2),
    framework_parent=None,
    raw_ocds=None,
    supplier_debarred_until=None,
):
    return {
        "ocid": ocid,
        "procuring_entity": "Test Ministry",
        "value": value,
        "currency": "ZMW",
        "award_date": award_date,
        "signing_date": signing_date,
        "status": "active",
        "framework_parent": framework_parent,
        "raw_ocds": raw_ocds or {},
        "supplier_debarred_until": supplier_debarred_until,
    }


def raw_with_estimate(estimate: float, method: str = "open") -> dict:
    return {
        "releases": [{
            "tender": {
                "procurementMethod": method,
                "value": {"amount": estimate, "currency": "ZMW"},
            }
        }]
    }


def raw_with_parties(parties: list[dict]) -> dict:
    return {"releases": [{"parties": parties}]}


def raw_with_amendments(original: float, deltas: list[float]) -> dict:
    amendments = [
        {
            "id": f"AMD-{i+1}",
            "changes": [{"property": "value.amount",
                         "oldValue": original,
                         "newValue": original + d}]
        }
        for i, d in enumerate(deltas)
    ]
    return {
        "releases": [{
            "contracts": [{"amendments": amendments}]
        }]
    }


# ── Check 4: Forensics ─────────────────────────────────────────────────────────

class TestForensicsCheck:
    chk = ForensicsCheck()

    def test_flag_award_equals_estimate_exactly(self):
        raw = raw_with_estimate(5_000_000.0)
        c = contract(value=5_000_000.0, raw_ocds=raw)
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.FLAG
        assert out.weight_applied == 15.0

    def test_flag_round_number_value(self):
        """Value is exact multiple of 1M but estimate differs — round-number only flag."""
        raw = raw_with_estimate(5_100_000.0)
        c = contract(value=5_000_000.0, raw_ocds=raw)
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.FLAG
        assert "round-number" in out.evidence_note.lower()

    def test_ok_non_round_differs_from_estimate(self):
        raw = raw_with_estimate(5_000_000.0)
        c = contract(value=4_876_543.50, raw_ocds=raw)
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.OK

    def test_ok_no_estimate_non_round(self):
        c = contract(value=3_456_789.0)
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.OK

    def test_skip_framework_calloff(self):
        c = contract(framework_parent="ocds-fw-001")
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.SKIP

    def test_skip_no_value(self):
        c = contract(value=None)
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.SKIP


# ── Check 5: Supplier Network ──────────────────────────────────────────────────

class TestSupplierNetworkCheck:
    chk = SupplierNetworkCheck()

    def _supplier(self, sid, name, address=None, phone=None, tpin=None):
        p = {"id": sid, "name": name, "roles": ["supplier"]}
        if address:
            p["address"] = {"streetAddress": address}
        if phone:
            p["contactPoint"] = {"telephone": phone}
        if tpin:
            p["identifier"] = {"scheme": "ZM-TPIN", "id": tpin}
        return p

    def test_flag_shared_address(self):
        parties = [
            self._supplier("s1", "Alpha Ltd", address="Plot 15, Cairo Road, Lusaka"),
            self._supplier("s2", "Beta Ltd",  address="Plot 15, Cairo Road, Lusaka"),
        ]
        c = contract(raw_ocds=raw_with_parties(parties))
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.FLAG
        assert "address" in out.evidence_note.lower()

    def test_flag_shared_phone(self):
        parties = [
            self._supplier("s1", "Alpha Ltd", phone="+260-211-111111"),
            self._supplier("s2", "Beta Ltd",  phone="+260-211-111111"),
        ]
        c = contract(raw_ocds=raw_with_parties(parties))
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.FLAG
        assert "phone" in out.evidence_note.lower()

    def test_flag_shared_tpin(self):
        parties = [
            self._supplier("s1", "Alpha Ltd", tpin="1000099999"),
            self._supplier("s2", "Beta Ltd",  tpin="1000099999"),
        ]
        c = contract(raw_ocds=raw_with_parties(parties))
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.FLAG
        assert "tpin" in out.evidence_note.lower()

    def test_ok_distinct_suppliers(self):
        parties = [
            self._supplier("s1", "Alpha Ltd", address="Plot 1, Cairo Road",   phone="+260-211-111111"),
            self._supplier("s2", "Beta Ltd",  address="Plot 99, Great East Rd", phone="+260-212-999999"),
        ]
        c = contract(raw_ocds=raw_with_parties(parties))
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.OK

    def test_skip_framework_calloff(self):
        parties = [self._supplier("s1", "A", address="X"), self._supplier("s2", "B", address="X")]
        c = contract(framework_parent="fw-001", raw_ocds=raw_with_parties(parties))
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.SKIP

    def test_skip_single_supplier(self):
        parties = [self._supplier("s1", "Only Ltd", address="Plot 1")]
        c = contract(raw_ocds=raw_with_parties(parties))
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.SKIP

    def test_skip_direct_procurement(self):
        raw = {"releases": [{"tender": {"procurementMethod": "direct"}, "parties": []}]}
        c = contract(raw_ocds=raw)
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.SKIP

    def test_skip_no_suppliers_in_record(self):
        c = contract(raw_ocds={})
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.SKIP


# ── Check 6: Score variance ────────────────────────────────────────────────────

class TestScoreVarianceCheck:
    chk = ScoreVarianceCheck()

    def test_flag_award_far_above_estimate(self):
        raw = raw_with_estimate(10_000_000.0)
        c = contract(value=12_000_000.0, raw_ocds=raw)  # 20% over — above 15% cap
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.FLAG
        assert "20.0%" in out.evidence_note

    def test_ok_award_within_cap(self):
        raw = raw_with_estimate(10_000_000.0)
        c = contract(value=11_400_000.0, raw_ocds=raw)  # 14% over — under cap
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.OK

    def test_ok_award_below_estimate(self):
        raw = raw_with_estimate(10_000_000.0)
        c = contract(value=9_000_000.0, raw_ocds=raw)   # -10% — not flagged
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.OK

    def test_skip_framework_calloff(self):
        raw = raw_with_estimate(10_000_000.0)
        c = contract(framework_parent="fw-001", raw_ocds=raw)
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.SKIP

    def test_skip_no_estimate(self):
        c = contract(value=5_000_000.0, raw_ocds={})
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.SKIP

    def test_skip_no_value(self):
        raw = raw_with_estimate(5_000_000.0)
        c = contract(value=None, raw_ocds=raw)
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.SKIP

    def test_custom_cap_threshold(self):
        raw = raw_with_estimate(10_000_000.0)
        c = contract(value=10_800_000.0, raw_ocds=raw)   # 8% over
        cfg_strict = build_config(threshold_overrides={"amendment_cap_pct": 5.0})
        out = self.chk.run(c, cfg_strict)
        assert out.result == CheckResult.FLAG  # 8% > 5% strict cap


# ── Check 7: Amendment ────────────────────────────────────────────────────────

class TestAmendmentCheck:
    chk = AmendmentCheck()

    def test_flag_amendments_exceed_cap(self):
        # original 18M, delta +6M = 33% > 15% cap
        raw = raw_with_amendments(18_000_000, [6_000_000])
        c = contract(value=18_000_000.0, raw_ocds=raw)
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.FLAG
        assert "33.3%" in out.evidence_note

    def test_flag_multiple_amendments_cumulative(self):
        # original 10M, two amendments of +1M each = 20% > 15%
        raw = raw_with_amendments(10_000_000, [1_000_000, 1_000_000])
        c = contract(value=10_000_000.0, raw_ocds=raw)
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.FLAG

    def test_ok_amendments_within_cap(self):
        # original 10M, delta +1M = 10% < 15% cap
        raw = raw_with_amendments(10_000_000, [1_000_000])
        c = contract(value=10_000_000.0, raw_ocds=raw)
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.OK

    def test_ok_no_amendments(self):
        c = contract(raw_ocds={})
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.OK

    def test_skip_no_original_value(self):
        raw = raw_with_amendments(0, [1_000_000])
        c = contract(value=None, raw_ocds=raw)
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.SKIP

    def test_sample_006_amendment_flagged(self, sample_contracts):
        c = sample_contracts["ocds-zm-zppa-006"]
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.FLAG  # 33% increase on housing contract


# ── Check 8: Debarment ────────────────────────────────────────────────────────

class TestDebarmentCheck:
    chk = DebarmentCheck()

    def test_flag_supplier_debarred_at_award(self):
        c = contract(
            award_date=date(2024, 3, 15),
            supplier_debarred_until=date(2024, 12, 31),  # still debarred
        )
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.FLAG
        assert "2024-12-31" in out.evidence_note

    def test_flag_debarment_ends_same_day_as_award(self):
        """Debarred until award date — still ineligible (inclusive)."""
        c = contract(
            award_date=date(2024, 3, 15),
            supplier_debarred_until=date(2024, 3, 15),
        )
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.FLAG

    def test_ok_debarment_expired_before_award(self):
        c = contract(
            award_date=date(2024, 3, 15),
            supplier_debarred_until=date(2023, 12, 31),  # expired before award
        )
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.OK

    def test_skip_debarment_info_absent(self):
        """Absence of data must not be treated as debarment."""
        c = contract(supplier_debarred_until=None)
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.SKIP

    def test_skip_unparseable_date(self):
        c = contract(supplier_debarred_until="not-a-date")
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.SKIP

    def test_flag_with_string_dates(self):
        """Dates may come in as ISO strings from JSON deserialisation."""
        c = contract(
            award_date="2024-03-15",
            supplier_debarred_until="2025-06-30",
        )
        out = self.chk.run(c, CFG)
        assert out.result == CheckResult.FLAG


# ── Full runner: all 8 checks ─────────────────────────────────────────────────

class TestRunnerAllChecks:

    def test_runner_produces_8_outputs(self):
        c = contract(raw_ocds=raw_with_estimate(5_000_000.0))
        out = run_checks(c, build_config())
        assert len(out.outputs) == 8

    def test_runner_check_ids_are_1_to_8(self):
        c = contract()
        out = run_checks(c, build_config())
        ids = [o.check_id for o in out.outputs]
        assert ids == [1, 2, 3, 4, 5, 6, 7, 8]

    def test_runner_score_sums_flagged_weights(self):
        c = contract(
            signing_date=None,          # check 1 FLAG (15)
            award_date=date(2024, 1, 1),
            supplier_debarred_until=date(2025, 1, 1),  # check 8 FLAG (10)
        )
        out = run_checks(c, build_config())
        expected = sum(o.weight_applied for o in out.outputs if o.result == CheckResult.FLAG)
        assert out.raw_score == expected
        assert out.raw_score >= 25.0  # at least checks 1 + 8

    def test_high_risk_contract_all_flags_possible(self):
        """Craft a contract that trips as many checks as possible."""
        parties = [
            {"id": "s1", "name": "Alpha", "roles": ["supplier"],
             "address": {"streetAddress": "Same Address"},
             "contactPoint": {"telephone": "0211-111111"}},
            {"id": "s2", "name": "Beta",  "roles": ["supplier"],
             "address": {"streetAddress": "Same Address"},
             "contactPoint": {"telephone": "0211-111111"}},
        ]
        amendments = [{"id": "A1", "changes": [
            {"property": "value.amount", "oldValue": 5_000_000, "newValue": 7_000_000}
        ]}]
        raw = {
            "releases": [{
                "tender": {
                    "procurementMethod": "open",
                    "value": {"amount": 5_000_000, "currency": "ZMW"},
                    "tenderPeriod": {"startDate": "2024-01-01", "endDate": "2024-02-01"},
                },
                "parties": parties,
                "contracts": [{"amendments": amendments}],
            }]
        }
        c = contract(
            value=5_000_000.0,          # equals estimate → forensics FLAG
            signing_date=None,           # check 1 FLAG
            award_date=date(2024, 2, 1), # same as tender close → time_gap (identical dates edge)
            supplier_debarred_until=date(2025, 1, 1),  # check 8 FLAG
            raw_ocds=raw,
        )
        out = run_checks(c, build_config())
        flag_count = out.flag_count
        assert flag_count >= 3, f"Expected ≥3 flags, got {flag_count}: {[o for o in out.outputs if o.result == CheckResult.FLAG]}"
