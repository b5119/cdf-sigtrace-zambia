"""Polygon confirmation-contract client (INC-012).

Bridges the backend to the CDFConfirmation Solidity contract on Polygon (Amoy
testnet). In dev/test (POLYGON_MOCK_MODE=true or no signer key), MockPolygonClient
mirrors the on-chain contract's multi-party confirmation logic in memory so the
confirmation workflow (INC-013) is fully testable without a live chain.

The Solidity source of truth is src/contracts/contracts/CDFConfirmation.sol.
This mock enforces the SAME invariants:
  - N distinct confirmations required before complete
  - a single party cannot complete alone (duplicate confirmer rejected)
  - the recording monitor cannot self-confirm
"""
import hashlib
import logging
import uuid
from dataclasses import dataclass, field

from app.core.config import settings

log = logging.getLogger(__name__)


def submission_key(submission_uuid: str) -> str:
    """keccak-like 0x key from an off-chain submission UUID (mirrors ethers.id())."""
    return "0x" + hashlib.sha256(submission_uuid.encode()).hexdigest()


@dataclass
class _OnChainSubmission:
    ipfs_cid: str
    required: int
    monitor: str
    confirmers: set[str] = field(default_factory=set)
    complete: bool = False
    tx_recorded: str = ""


class MockPolygonClient:
    """In-memory mirror of CDFConfirmation.sol — same confirmation invariants."""

    def __init__(self) -> None:
        self._subs: dict[str, _OnChainSubmission] = {}

    def _tx(self) -> str:
        return "0x" + uuid.uuid4().hex + uuid.uuid4().hex[:24]

    def record_submission(self, key: str, ipfs_cid: str, required: int, monitor: str) -> str:
        if key in self._subs:
            raise ValueError("already recorded")
        if required < 1:
            raise ValueError("required must be > 0")
        tx = self._tx()
        self._subs[key] = _OnChainSubmission(
            ipfs_cid=ipfs_cid, required=required, monitor=monitor, tx_recorded=tx
        )
        log.debug("MockPolygon: recorded %s required=%d tx=%s", key[:12], required, tx)
        return tx

    def confirm(self, key: str, confirmer: str) -> dict:
        s = self._subs.get(key)
        if not s:
            raise ValueError("unknown submission")
        if s.complete:
            raise ValueError("already complete")
        if confirmer == s.monitor:
            raise ValueError("monitor cannot self-confirm")
        if confirmer in s.confirmers:
            raise ValueError("duplicate confirmation")

        s.confirmers.add(confirmer)
        tx = self._tx()
        if len(s.confirmers) >= s.required:
            s.complete = True
        return {"tx": tx, "count": len(s.confirmers), "complete": s.complete}

    def is_complete(self, key: str) -> bool:
        s = self._subs.get(key)
        return bool(s and s.complete)

    def confirmation_count(self, key: str) -> int:
        s = self._subs.get(key)
        return len(s.confirmers) if s else 0

    def clear(self) -> None:
        """Test helper."""
        self._subs.clear()


class Web3PolygonClient:
    """Real Polygon client via web3.py + the deployed CDFConfirmation contract.

    Requires web3, a funded Amoy signer key, and POLYGON_CONTRACT_ADDRESS.
    Stub — wired up at deployment (INC-020).
    """

    def record_submission(self, key: str, ipfs_cid: str, required: int, monitor: str) -> str:
        raise NotImplementedError("Real Polygon client wired at deployment (INC-020)")

    def confirm(self, key: str, confirmer: str) -> dict:
        raise NotImplementedError("Real Polygon client wired at deployment (INC-020)")


# Single shared mock instance (in-memory state persists across calls within a process)
_mock_singleton = MockPolygonClient()


def get_polygon_client():
    """Return the mock or real Polygon client based on runtime config."""
    use_mock = getattr(settings, "POLYGON_MOCK_MODE", True) or not settings.POLYGON_SIGNER_KEY
    if use_mock:
        return _mock_singleton
    return Web3PolygonClient()
