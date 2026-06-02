"""Hyperledger Fabric gateway client (INC-006).

Wraps the Fabric Gateway SDK with a clean interface.
In dev/test (FABRIC_MOCK_MODE=true or no gateway endpoint configured),
uses an in-memory mock so the service logic is fully testable without
a running Fabric network.

Real Fabric path (production):
  pip install fabric-gateway grpcio grpcio-tools
  Requires: gateway endpoint, TLS cert, client identity cert+key, MSP ID.

Chaincode interface expected on channel FABRIC_CHANNEL, chaincode FABRIC_CHAINCODE:
  SetHash(ocid string, sha256 string) → txID string
  GetHash(ocid string)               → sha256 string (or "" if not found)
  GetHistory(ocid string)            → JSON array of {txID, sha256, timestamp}
"""
import hashlib
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.core.config import settings

log = logging.getLogger(__name__)

# ── In-memory mock (dev / test) ────────────────────────────────────────────────

_mock_store: dict[str, dict] = {}  # ocid → {sha256, tx_id, block_ref, anchored_at}


class MockFabricClient:
    """Deterministic in-memory Fabric mock — no network, no crypto."""

    def submit_set_hash(self, ocid: str, sha256: str) -> dict:
        tx_id = f"mock-tx-{uuid.uuid4().hex[:16]}"
        block_ref = f"mock-block-{len(_mock_store) + 1}"
        _mock_store[ocid] = {
            "sha256": sha256,
            "tx_id": tx_id,
            "block_ref": block_ref,
            "anchored_at": datetime.now(timezone.utc).isoformat(),
        }
        log.debug("MockFabric: anchored %s sha256=%s tx=%s", ocid, sha256[:8], tx_id)
        return {"tx_id": tx_id, "block_ref": block_ref}

    def query_get_hash(self, ocid: str) -> Optional[str]:
        record = _mock_store.get(ocid)
        return record["sha256"] if record else None

    def query_get_history(self, ocid: str) -> list[dict]:
        record = _mock_store.get(ocid)
        if not record:
            return []
        return [{"tx_id": record["tx_id"], "sha256": record["sha256"],
                 "timestamp": record["anchored_at"]}]

    def clear(self):
        """Test helper — reset in-memory state between test runs."""
        _mock_store.clear()


# ── Real Fabric Gateway client ─────────────────────────────────────────────────

class FabricGatewayClient:
    """
    Thin wrapper around the Hyperledger Fabric Gateway Python SDK.

    Requires fabric-gateway and grpcio packages (not in requirements.txt
    by default — add them when deploying against a real Fabric network).

    Connection is established lazily on first use and cached.
    """

    def __init__(self):
        self._gateway = None
        self._network = None
        self._contract = None

    def _connect(self):
        if self._contract is not None:
            return
        try:
            import grpc
            from grpc import ssl_channel_credentials
            import fabric_gateway as gw

            with open(settings.FABRIC_TLS_CERT_PATH, "rb") as f:
                tls_cert = f.read()
            with open(settings.FABRIC_CLIENT_CERT_PATH, "rb") as f:
                client_cert = f.read()
            with open(settings.FABRIC_CLIENT_KEY_PATH, "rb") as f:
                client_key = f.read()

            credentials = ssl_channel_credentials(
                root_certificates=tls_cert,
                private_key=client_key,
                certificate_chain=client_cert,
            )
            channel = grpc.secure_channel(settings.FABRIC_GATEWAY_ENDPOINT, credentials)

            identity = gw.identity.X509Identity(
                msp_id=settings.FABRIC_MSP_ID,
                certificate=client_cert.decode(),
            )
            signer = gw.identity.PrivateKeySigner(
                private_key=gw.identity._crypto.load_private_key(client_key)
            )

            self._gateway = gw.Gateway(identity=identity, signer=signer, channel=channel)
            self._network = self._gateway.get_network(settings.FABRIC_CHANNEL)
            self._contract = self._network.get_contract(settings.FABRIC_CHAINCODE)
            log.info("Connected to Fabric gateway at %s", settings.FABRIC_GATEWAY_ENDPOINT)
        except Exception as e:
            log.error("Fabric gateway connection failed: %s", e)
            raise

    def submit_set_hash(self, ocid: str, sha256: str) -> dict:
        self._connect()
        result = self._contract.submit_transaction("SetHash", ocid, sha256)
        tx_id = result.transaction_id
        block_ref = str(result.block_number)
        return {"tx_id": tx_id, "block_ref": block_ref}

    def query_get_hash(self, ocid: str) -> Optional[str]:
        self._connect()
        result = self._contract.evaluate_transaction("GetHash", ocid)
        val = result.decode().strip()
        return val if val else None

    def query_get_history(self, ocid: str) -> list[dict]:
        self._connect()
        import json
        result = self._contract.evaluate_transaction("GetHistory", ocid)
        return json.loads(result.decode())


# ── Factory — returns mock or real client based on config ─────────────────────

def get_fabric_client() -> MockFabricClient | FabricGatewayClient:
    """Return the appropriate Fabric client based on runtime config."""
    use_mock = (
        settings.FABRIC_MOCK_MODE
        or not settings.FABRIC_GATEWAY_ENDPOINT
    )
    if use_mock:
        return MockFabricClient()
    return FabricGatewayClient()
