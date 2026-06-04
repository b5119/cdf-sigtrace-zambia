# contracts — Polygon Confirmation Smart Contract

Solidity multi-party confirmation contract for CDF Pulse field-evidence delivery.
A submission requires **N distinct institutional confirmations** before it is marked
complete — a single party cannot complete a submission alone.

## Layout
```
contracts/CDFConfirmation.sol   the confirmation contract (Solidity 0.8.24)
test/CDFConfirmation.test.js     Hardhat tests (14, all green)
scripts/deploy.js                deploy to Polygon Amoy
hardhat.config.js                Hardhat + Amoy network config
```

## Commands
```bash
npm install
npx hardhat compile
npx hardhat test                 # 14 passing
npx hardhat run scripts/deploy.js --network amoy   # needs funded Amoy key in .env
```

## On-chain guarantees (enforced in CDFConfirmation.sol)
- N distinct confirmations required before `complete`
- a single party cannot complete alone (duplicate confirm from same address reverts)
- the recording monitor cannot self-confirm
- only owner-whitelisted institutional confirmers may confirm
- `SubmissionCompleted` event fires only when the Nth distinct confirmation lands

The backend mirrors this contract in `src/backend/app/services/polygon_client.py`
(`MockPolygonClient`) so the confirmation workflow (INC-013) is testable without a
live testnet. The real web3 client is wired at deployment (INC-020).

Built in **INC-012**. Confirmation workflow wiring + UI is **INC-013**.
