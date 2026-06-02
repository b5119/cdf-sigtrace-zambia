# contracts — Polygon smart contracts (Solidity + Hardhat)

The CDF Pulse **multi-party confirmation** contract: records a submission (IPFS CID + location hash +
metadata) and requires N distinct confirmations before a project is marked complete. A single party
cannot complete alone. Built in **INC-012**, used by INC-013.

```
contracts/
  PulseConfirmation.sol     submission registry + multi-sig confirmation + completion event
  scripts/deploy.ts         deploy to Polygon Amoy testnet
test/                       hardhat tests: N-1 ≠ complete; Nth completes; duplicate confirmer rejected
hardhat.config.ts
```
On-chain data is **non-personal only** (CIDs, hashes, addresses) — never personal data.
Anchoring of procurement contract hashes uses **Hyperledger Fabric** (in `backend/services/anchor`),
not this contract.
