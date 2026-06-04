# INC-012 · Polygon Confirmation Contract

- **Status:** DONE
- **Started:** 2026-06-04  ·  **Completed:** 2026-06-04
- **Owner / session:** Claude Code
- **Weight:** 6%

## Goal
Solidity multi-party confirmation contract for the CDF Pulse delivery layer.
A field-evidence submission requires N **distinct** institutional confirmations before
it is marked complete — a single party cannot complete a submission alone. Deployable
to Polygon Amoy testnet. Plus a backend mock client mirroring the contract for INC-013.

## Deliverables

### Smart contract — `src/contracts/`
- [x] `contracts/CDFConfirmation.sol` — the confirmation contract (Solidity 0.8.24)
- [x] `hardhat.config.js` — Hardhat + Amoy network config (chainId 80002)
- [x] `test/CDFConfirmation.test.js` — 14 tests
- [x] `scripts/deploy.js` — deploy to Amoy
- [x] `.env.example` — Amoy RPC + signer key template
- [x] `package.json` — Hardhat toolbox

### Contract logic (the on-chain guarantees)
- `recordSubmission(bytes32 id, string ipfsCid, uint8 required)` — register a submission
- `confirm(bytes32 id)` — a distinct, authorized confirmer confirms
- `addConfirmer / removeConfirmer` — owner-governed institutional whitelist
- Invariants enforced on-chain:
  - **N distinct confirmations** required (per-address `hasConfirmed` mapping)
  - **single party cannot complete alone** — duplicate confirm from same address reverts
  - **monitor cannot self-confirm** their own submission
  - non-authorized addresses rejected; confirmation after completion rejected
  - `SubmissionCompleted` event fires only when count reaches N

### Backend mirror — `app/services/polygon_client.py`
- [x] MockPolygonClient — in-memory mirror enforcing the SAME invariants (for INC-013 workflow, fully testable off-chain)
- [x] Web3PolygonClient — real client stub (wired at deployment, INC-020)
- [x] `submission_key()` — keccak-style 0x key from off-chain UUID (mirrors `ethers.id()`)
- [x] `POLYGON_MOCK_MODE` config flag
- [x] `tests/test_polygon_client.py` — 11 tests asserting the same guarantees as the Solidity tests

## Acceptance criteria — results
| Criterion | Solidity test | Mirror test | Result |
|-----------|---------------|-------------|:------:|
| N-1 confirmations ≠ complete | `N-1 confirmations does NOT complete` | `test_n_minus_1_does_not_complete` | ✅ |
| Nth distinct confirmation completes | `Nth distinct confirmation completes` | `test_nth_distinct_completes` | ✅ |
| Single party cannot complete alone | `a single party CANNOT complete alone` | `test_single_party_cannot_complete_alone` | ✅ |
| Replay/duplicate confirmer rejected | `duplicate confirmation` revert | `test_single_party_cannot_complete_alone` | ✅ |
| Monitor cannot self-confirm | `monitor cannot self-confirm` | `test_monitor_cannot_self_confirm` | ✅ |
| Non-authorized rejected | `rejects confirmation from a non-authorized address` | — | ✅ |
| 3-of-3 requires all three | `requires all 3 distinct confirmers` | `test_3_of_3` | ✅ |
| Owner-only governance | `only owner can add confirmers` | — | ✅ |

## Tests
- **Solidity (Hardhat):** 14 passing — `npx hardhat test`
- **Backend mirror (pytest):** 11 passing
- **Full backend suite:** 299/299 green
- **Combined:** 313 tests green

```
CDFConfirmation
  recording submissions (3) ✔
  multi-party confirmation — the core guarantee (8) ✔
  3-of-3 confirmation (1) ✔
  confirmer governance (2) ✔
14 passing
```

## Decisions / deviations
- Solidity 0.8.24 with optimizer (200 runs).
- Confirmer whitelist is owner-governed — in production the owner is the backend signer
  managed by the platform; institutional confirmers (council/ward officers, OAG) are added per their MSP.
- The backend mock mirrors the contract so INC-013 (confirmation workflow) can be built and
  tested without a live testnet; the real Web3 client is wired at deployment (INC-020).
- Hardhat artifacts/cache/node_modules are gitignored (already in `.gitignore`).

## Follow-ups
- INC-013: confirmation workflow — backend records submissions on-chain via the client, M7/O8 UI
- Real Amoy deployment + `POLYGON_CONTRACT_ADDRESS` wiring → INC-020
- web3.py integration in Web3PolygonClient → INC-020

## Progress update
- INC-012 = **DONE** — Overall: **69%**.
