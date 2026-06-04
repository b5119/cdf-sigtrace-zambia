"""Tests for the backend Polygon client mirror (INC-012).

The MockPolygonClient mirrors CDFConfirmation.sol exactly — these tests assert
the same multi-party guarantees the Solidity tests assert, so the backend
confirmation workflow (INC-013) can rely on identical behaviour off-chain.
"""
import pytest

from app.services.polygon_client import (
    MockPolygonClient,
    submission_key,
)

CID = "bafkreiabc123"


@pytest.fixture
def chain():
    return MockPolygonClient()


def test_record_submission(chain):
    key = submission_key("sub-001")
    tx = chain.record_submission(key, CID, 2, monitor="0xMonitor")
    assert tx.startswith("0x")
    assert chain.confirmation_count(key) == 0
    assert chain.is_complete(key) is False


def test_record_rejects_duplicate(chain):
    key = submission_key("sub-001")
    chain.record_submission(key, CID, 2, monitor="0xMonitor")
    with pytest.raises(ValueError, match="already recorded"):
        chain.record_submission(key, CID, 2, monitor="0xMonitor")


def test_record_rejects_zero_required(chain):
    key = submission_key("sub-001")
    with pytest.raises(ValueError, match="required must be > 0"):
        chain.record_submission(key, CID, 0, monitor="0xMonitor")


def test_n_minus_1_does_not_complete(chain):
    key = submission_key("sub-001")
    chain.record_submission(key, CID, 2, monitor="0xMonitor")
    res = chain.confirm(key, "0xConfirmerA")
    assert res["count"] == 1
    assert res["complete"] is False
    assert chain.is_complete(key) is False


def test_nth_distinct_completes(chain):
    key = submission_key("sub-001")
    chain.record_submission(key, CID, 2, monitor="0xMonitor")
    chain.confirm(key, "0xConfirmerA")
    res = chain.confirm(key, "0xConfirmerB")
    assert res["count"] == 2
    assert res["complete"] is True
    assert chain.is_complete(key) is True


def test_single_party_cannot_complete_alone(chain):
    key = submission_key("sub-001")
    chain.record_submission(key, CID, 2, monitor="0xMonitor")
    chain.confirm(key, "0xConfirmerA")
    with pytest.raises(ValueError, match="duplicate confirmation"):
        chain.confirm(key, "0xConfirmerA")
    assert chain.confirmation_count(key) == 1
    assert chain.is_complete(key) is False


def test_monitor_cannot_self_confirm(chain):
    key = submission_key("sub-001")
    chain.record_submission(key, CID, 2, monitor="0xMonitor")
    with pytest.raises(ValueError, match="monitor cannot self-confirm"):
        chain.confirm(key, "0xMonitor")


def test_confirm_unknown_submission(chain):
    with pytest.raises(ValueError, match="unknown submission"):
        chain.confirm(submission_key("nope"), "0xConfirmerA")


def test_confirm_after_complete_rejected(chain):
    key = submission_key("sub-001")
    chain.record_submission(key, CID, 2, monitor="0xMonitor")
    chain.confirm(key, "0xConfirmerA")
    chain.confirm(key, "0xConfirmerB")
    with pytest.raises(ValueError, match="already complete"):
        chain.confirm(key, "0xConfirmerC")


def test_3_of_3(chain):
    key = submission_key("sub-001")
    chain.record_submission(key, CID, 3, monitor="0xMonitor")
    chain.confirm(key, "0xA")
    chain.confirm(key, "0xB")
    assert chain.is_complete(key) is False
    chain.confirm(key, "0xC")
    assert chain.is_complete(key) is True


def test_submission_key_deterministic():
    assert submission_key("sub-001") == submission_key("sub-001")
    assert submission_key("sub-001") != submission_key("sub-002")
    assert submission_key("sub-001").startswith("0x")
