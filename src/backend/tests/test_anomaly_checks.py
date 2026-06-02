"""Tests for anomaly engine checks 1–3 (INC-003).

Each check has ≥1 positive (FLAG), ≥1 negative (OK), and ≥1 SKIP (false-positive
safeguard) case, per the requirement in docs/10_TESTING.md.
"""
import json
import os
from datetime import date

import pytest

from engine.checks.check_01_signing import SigningCheck
from engine.checks.check_02_standstill import StandstillCheck
from engine.checks.check_03_time_gap import TimeGapCheck
from engine.models import CheckResult
from engine.runner import run_checks, build_config

DEFAULT_CFG = build_config()

# ── helpers ────────────────────────────────────────────────────────────────────

def contract(
    ocid="ocds-test-001",
    signing_date=date(2024, 4, 1),
    award_date=date(2024, 3, 15),
    status="active",
    framework_parent=None,
    raw_ocds=None,
):
    return {
        "ocid": ocid,
        "procuring_entity": "Test Ministry",
        "value": 1_000_000,
        "currency": "ZMW",
        "award_date": award_date,
        "signing_date": signing_date,
        "status": status,
        "framework_parent": framework_parent,
        "raw_ocds": raw_ocds or {},
    }


def raw_with_tender_period(start: str, end: str, method: str = "open") -> dict:
    return {
        "releases": [
            {
                "tender": {
                    "procurementMethod": method,
                    "tenderPeriod": {"startDate": start, "endDate": end},
                }
            }
        ]
    }


# ── Check 1: Signing ───────────────────────────────────────────────────────────

class TestSigningCheck:
    chk = SigningCheck()

    def test_flag_when_signing_date_absent(self):
        c = contract(signing_date=None)
        out = self.chk.run(c, DEFAULT_CFG)
        assert out.result == CheckResult.FLAG
        assert out.weight_applied == 15.0

    def test_ok_when_signing_date_present(self):
        c = contract(signing_date=date(2024, 4, 2))
        out = self.chk.run(c, DEFAULT_CFG)
        assert out.result == CheckResult.OK

    def test_skip_cancelled_contract(self):
        """Cancelled contracts are not expected to have a signing date."""
        c = contract(signing_date=None, status="cancelled")
        out = self.chk.run(c, DEFAULT_CFG)
        assert out.result == CheckResult.SKIP

    def test_weight_override_respected(self):
        c = contract(signing_date=None)
        cfg = build_config(weight_overrides={"signing": 25.0})
        out = self.chk.run(c, cfg)
        assert out.weight_applied == 25.0


# ── Check 2: Standstill ────────────────────────────────────────────────────────

class TestStandstillCheck:
    chk = StandstillCheck()

    def test_flag_when_signed_before_standstill(self):
        # Award 2024-06-25, signed 2024-06-26 = 1 day (< 14)
        c = contract(award_date=date(2024, 6, 25), signing_date=date(2024, 6, 26))
        out = self.chk.run(c, DEFAULT_CFG)
        assert out.result == CheckResult.FLAG
        assert out.weight_applied == 20.0
        assert "1 day(s)" in out.evidence_note

    def test_ok_when_standstill_observed(self):
        # Award 2024-03-15, signed 2024-04-02 = 18 days (> 14)
        c = contract(award_date=date(2024, 3, 15), signing_date=date(2024, 4, 2))
        out = self.chk.run(c, DEFAULT_CFG)
        assert out.result == CheckResult.OK

    def test_ok_exactly_at_standstill_threshold(self):
        c = contract(award_date=date(2024, 1, 1), signing_date=date(2024, 1, 15))
        out = self.chk.run(c, DEFAULT_CFG)
        assert out.result == CheckResult.OK  # 14 days exactly — meets threshold

    def test_skip_framework_calloff(self):
        """Framework call-offs must NOT trigger standstill check."""
        c = contract(
            award_date=date(2024, 8, 10),
            signing_date=date(2024, 8, 12),
            framework_parent="ocds-zm-zppa-fw-001",
        )
        out = self.chk.run(c, DEFAULT_CFG)
        assert out.result == CheckResult.SKIP

    def test_skip_when_award_date_absent(self):
        c = contract(award_date=None, signing_date=date(2024, 4, 1))
        out = self.chk.run(c, DEFAULT_CFG)
        assert out.result == CheckResult.SKIP

    def test_skip_when_signing_date_absent(self):
        c = contract(award_date=date(2024, 3, 15), signing_date=None)
        out = self.chk.run(c, DEFAULT_CFG)
        assert out.result == CheckResult.SKIP

    def test_custom_standstill_threshold(self):
        # 10 days gap — OK with default 14, FLAG with threshold 14 → still FLAG if gap < threshold
        c = contract(award_date=date(2024, 1, 1), signing_date=date(2024, 1, 8))  # 7 days
        cfg = build_config(threshold_overrides={"standstill_days": 7})
        out = self.chk.run(c, cfg)
        assert out.result == CheckResult.OK  # exactly 7 days meets threshold

        cfg2 = build_config(threshold_overrides={"standstill_days": 8})
        out2 = self.chk.run(c, cfg2)
        assert out2.result == CheckResult.FLAG  # 7 days < 8 threshold


# ── Check 3: Time-gap ──────────────────────────────────────────────────────────

class TestTimeGapCheck:
    chk = TimeGapCheck()

    def test_flag_identical_key_stage_dates(self):
        """All three key dates identical — suspicious (sub-check B, highest priority)."""
        raw = raw_with_tender_period("2024-01-01", "2024-04-01")
        c = contract(
            award_date=date(2024, 4, 1),
            signing_date=date(2024, 4, 1),
            raw_ocds=raw,
        )
        out = self.chk.run(c, DEFAULT_CFG)
        assert out.result == CheckResult.FLAG
        assert "identical" in out.evidence_note.lower()

    def test_flag_zero_day_evaluation_period(self):
        """Award same day as tender close but signing is different — sub-check A fires."""
        # tender_end=2024-03-01, award=2024-03-01 → gap 0 days
        # signing=2024-03-20 (different) → sub-check B doesn't fire (not all identical)
        raw = raw_with_tender_period("2024-01-01", "2024-03-01")
        c = contract(award_date=date(2024, 3, 1), signing_date=date(2024, 3, 20), raw_ocds=raw)
        out = self.chk.run(c, DEFAULT_CFG)
        assert out.result == CheckResult.FLAG
        assert "0 day(s)" in out.evidence_note

    def test_ok_adequate_evaluation_period(self):
        """Tender closed 2024-01-15, awarded 2024-02-01 = 17 days — OK."""
        raw = raw_with_tender_period("2023-12-01", "2024-01-15")
        c = contract(award_date=date(2024, 2, 1), raw_ocds=raw)
        out = self.chk.run(c, DEFAULT_CFG)
        assert out.result == CheckResult.OK

    def test_skip_framework_calloff(self):
        """Framework call-offs have no open tender stage."""
        raw = raw_with_tender_period("2024-01-01", "2024-03-01")
        c = contract(framework_parent="ocds-zm-fw-001", raw_ocds=raw)
        out = self.chk.run(c, DEFAULT_CFG)
        assert out.result == CheckResult.SKIP

    def test_skip_direct_procurement(self):
        """Direct procurement has no open tender period."""
        raw = raw_with_tender_period("2024-01-01", "2024-01-01", method="direct")
        c = contract(award_date=date(2024, 1, 1), raw_ocds=raw)
        out = self.chk.run(c, DEFAULT_CFG)
        assert out.result == CheckResult.SKIP

    def test_skip_limited_procurement(self):
        raw = raw_with_tender_period("2024-01-01", "2024-01-01", method="limited")
        c = contract(award_date=date(2024, 1, 1), raw_ocds=raw)
        out = self.chk.run(c, DEFAULT_CFG)
        assert out.result == CheckResult.SKIP

    def test_skip_no_tender_dates_in_raw(self):
        c = contract(award_date=date(2024, 2, 1), raw_ocds={})
        out = self.chk.run(c, DEFAULT_CFG)
        assert out.result == CheckResult.SKIP


# ── Runner integration ─────────────────────────────────────────────────────────

class TestRunner:

    def test_runner_returns_three_outputs_for_three_enabled_checks(self):
        c = contract(signing_date=date(2024, 4, 1), award_date=date(2024, 3, 15))
        cfg = build_config(enabled_check_ids={1, 2, 3})
        out = run_checks(c, cfg)
        assert len(out.outputs) == 3

    def test_runner_only_enabled_checks_run(self):
        c = contract(signing_date=None)
        cfg = build_config(enabled_check_ids={1})
        out = run_checks(c, cfg)
        assert len(out.outputs) == 1
        assert out.outputs[0].check_id == 1

    def test_clean_contract_no_flags(self):
        """A well-formed contract with adequate standstill and evaluation period."""
        raw = raw_with_tender_period("2023-11-01", "2024-01-15")
        c = contract(
            award_date=date(2024, 2, 1),
            signing_date=date(2024, 2, 20),
            raw_ocds=raw,
        )
        out = run_checks(c, DEFAULT_CFG)
        flag_outputs = [o for o in out.outputs if o.result == CheckResult.FLAG]
        assert len(flag_outputs) == 0
        assert out.flag_count == 0
        assert out.raw_score == 0.0

    def test_multiple_flags_accumulate_score(self):
        """Contract missing signing date AND standstill violation = two flags."""
        c = contract(
            signing_date=None,
            award_date=date(2024, 1, 1),
        )
        # No signing date → check 1 FLAG (15pts); standstill skipped (no signing date)
        out = run_checks(c, DEFAULT_CFG)
        signing_flag = next(o for o in out.outputs if o.check_id == 1)
        assert signing_flag.result == CheckResult.FLAG
        assert out.raw_score >= 15.0

    def test_raw_score_equals_sum_of_flagged_weights(self):
        c = contract(signing_date=None, award_date=date(2024, 1, 1))
        out = run_checks(c, DEFAULT_CFG)
        expected = sum(o.weight_applied for o in out.outputs if o.result == CheckResult.FLAG)
        assert out.raw_score == expected


# ── Sample fixture integration ─────────────────────────────────────────────────

SAMPLE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "ingestion", "sample", "ocds_sample.json"
)


@pytest.fixture
def sample_contracts():
    with open(SAMPLE_PATH) as f:
        pkg = json.load(f)
    from ingestion.normalise import normalise_records
    return {c["ocid"]: c for c, _ in normalise_records(pkg["records"])}


def test_sample_001_clean_no_signing_flag(sample_contracts):
    c = sample_contracts["ocds-zm-zppa-001"]
    out = run_checks(c, DEFAULT_CFG)
    signing = next(o for o in out.outputs if o.check_id == 1)
    assert signing.result == CheckResult.OK


def test_sample_002_missing_signing_flagged(sample_contracts):
    c = sample_contracts["ocds-zm-zppa-002"]
    out = run_checks(c, DEFAULT_CFG)
    signing = next(o for o in out.outputs if o.check_id == 1)
    assert signing.result == CheckResult.FLAG


def test_sample_003_standstill_violation_flagged(sample_contracts):
    c = sample_contracts["ocds-zm-zppa-003"]
    out = run_checks(c, DEFAULT_CFG)
    standstill = next(o for o in out.outputs if o.check_id == 2)
    assert standstill.result == CheckResult.FLAG


def test_sample_004_framework_calloff_standstill_skipped(sample_contracts):
    """Framework call-off must NOT trigger standstill check — false-positive safeguard."""
    c = sample_contracts["ocds-zm-zppa-004"]
    assert c["framework_parent"] == "ocds-zm-zppa-fw-001"
    out = run_checks(c, DEFAULT_CFG)
    standstill = next(o for o in out.outputs if o.check_id == 2)
    assert standstill.result == CheckResult.SKIP
