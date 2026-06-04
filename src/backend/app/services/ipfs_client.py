"""IPFS client for field-evidence photos (INC-011).

IPFS is content-addressed: the CID is derived from the file bytes via SHA-256,
so any change to the photo produces a different CID. This is the tamper-evidence
property — a stored CID is a cryptographic commitment to exact photo content.

In dev/test (IPFS_MOCK_MODE=true or no Kubo node), MockIPFSClient keeps content
in memory but computes a *real-format* CIDv1 (raw codec, sha2-256, base32) so the
CID behaves exactly like a production IPFS CID. KuboIPFSClient talks to a real
Kubo node's HTTP API.
"""
import base64
import hashlib
import logging
from typing import Optional

from app.core.config import settings

log = logging.getLogger(__name__)


def compute_cid(data: bytes) -> str:
    """Compute a CIDv1 (raw codec, sha2-256, base32 multibase) for the given bytes.

    Format: multibase('b') + base32( CIDv1(0x01) + raw-codec(0x55) + multihash )
    multihash = sha2-256(0x12) + length(0x20=32) + digest.
    Raw-codec CIDv1 strings start with 'bafkrei…' — identical to real IPFS output.
    """
    digest = hashlib.sha256(data).digest()
    multihash = bytes([0x12, 0x20]) + digest          # sha2-256, 32-byte digest
    cid_bytes = bytes([0x01, 0x55]) + multihash        # CIDv1, raw codec
    b32 = base64.b32encode(cid_bytes).decode("ascii").lower().rstrip("=")
    return "b" + b32


# ── In-memory mock (dev / test) ────────────────────────────────────────────────

_mock_store: dict[str, bytes] = {}


class MockIPFSClient:
    """Content-addressed in-memory IPFS mock. Deterministic, no network."""

    def add(self, data: bytes) -> str:
        cid = compute_cid(data)
        _mock_store[cid] = data
        log.debug("MockIPFS: pinned %d bytes → %s", len(data), cid)
        return cid

    def cat(self, cid: str) -> Optional[bytes]:
        return _mock_store.get(cid)

    def pin(self, cid: str) -> bool:
        return cid in _mock_store

    def exists(self, cid: str) -> bool:
        return cid in _mock_store

    def clear(self) -> None:
        """Test helper — reset in-memory state."""
        _mock_store.clear()


# ── Real Kubo HTTP API client ──────────────────────────────────────────────────

class KuboIPFSClient:
    """Talks to a real Kubo (go-ipfs) node via its HTTP API.

    Requires a running Kubo node reachable at settings.IPFS_API_URL.
    Uses CIDv1 to match the mock's output format.
    """

    def add(self, data: bytes) -> str:
        import httpx
        files = {"file": ("evidence", data)}
        params = {"cid-version": "1", "pin": "true"}
        with httpx.Client(timeout=30) as client:
            resp = client.post(f"{settings.IPFS_API_URL}/api/v0/add", files=files, params=params)
            resp.raise_for_status()
            return resp.json()["Hash"]

    def cat(self, cid: str) -> Optional[bytes]:
        import httpx
        with httpx.Client(timeout=30) as client:
            resp = client.post(f"{settings.IPFS_API_URL}/api/v0/cat", params={"arg": cid})
            if resp.status_code != 200:
                return None
            return resp.content

    def pin(self, cid: str) -> bool:
        import httpx
        with httpx.Client(timeout=30) as client:
            resp = client.post(f"{settings.IPFS_API_URL}/api/v0/pin/add", params={"arg": cid})
            return resp.status_code == 200

    def exists(self, cid: str) -> bool:
        return self.cat(cid) is not None


def get_ipfs_client() -> MockIPFSClient | KuboIPFSClient:
    """Return the mock or real IPFS client based on runtime config."""
    if settings.IPFS_MOCK_MODE:
        return MockIPFSClient()
    return KuboIPFSClient()
