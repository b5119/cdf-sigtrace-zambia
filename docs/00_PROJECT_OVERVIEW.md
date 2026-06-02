# 00 · Project Overview

## Problem
Two accountability gaps in Zambian public spending:

1. **Signature gap (procurement).** The e-GP system publishes 21 OCDS analytics reports, but none
   verifies contract signing, signature method, or the authorising officer. Contracts are printed,
   signed, scanned, and uploaded — legally accepted but cryptographically meaningless.
2. **Delivery gap (CDF projects).** IFMIS records that funds were disbursed and the SMART Zambia
   dashboard records self-reported status, but neither independently verifies that a funded project
   physically exists, is where it is claimed, and was actually completed.

CDF is now ~K6.245 billion per year (K40 million × 156 constituencies), so a monitoring weakness now
costs billions, not millions.

## What the system does
- **SigTrace Zambia** — ingests OCDS data, runs 8 integrity checks over contract execution, computes a
  weighted 0–100 risk score, anchors a SHA-256 hash of each signed contract to a permissioned ledger,
  and exposes a public document-vs-hash verification portal.
- **CDF Pulse** — an offline-first PWA for community monitors to capture GPS-tagged photographic
  evidence of project completion, stored on IPFS, confirmed by multiple parties via a Polygon smart
  contract, and published on a constituency dashboard.
- **Integrated monitor** — matches disbursement ↔ clean-integrity contract ↔ verified completion; a
  disbursement with no verified completion within a window is a **ghost-project signal**.

## Goals of the prototype
1. Demonstrate per-contract anomaly flagging the existing aggregate reports cannot produce.
2. Demonstrate tamper-evident contract verification and independent delivery confirmation.
3. Show the approach is feasible and legally compatible (ECTA, DPA No. 3 of 2021, Public Audit Act
   No. 6 of 2016).

## Out of scope (prototype)
- National production rollout / hardened multi-institution operations.
- Replacing e-GP, IFMIS, CPMS or the SMART dashboard — the framework augments them.
- Automated determinations of wrongdoing — outputs are review signals only.

## Non-negotiable design principles
- **Personal data off-chain.** Only hashes / non-personal metadata go on any ledger.
- **Two-tier output.** Aggregated, de-identified public tier; named findings restricted to authorised
  oversight bodies under a data-sharing arrangement.
- **Explainable checks.** Every flag is an explicit, reproducible computation — no opaque ML.
- **No false positives by design.** Framework-agreement call-offs excluded from single-source logic;
  lawful emergency procurement flagged only when its justification document is absent.

## Glossary
| Term | Meaning |
|------|---------|
| **CDF** | Constituency Development Fund |
| **e-GP** | Electronic Government Procurement system (ZPPA) |
| **OCDS** | Open Contracting Data Standard (the published procurement data format) |
| **OCID** | Open Contracting ID — unique id of a contracting process |
| **ZPPA** | Zambia Public Procurement Authority |
| **OAG** | Office of the Auditor General |
| **ACC** | Anti-Corruption Commission |
| **CPMS** | Contract Performance Management System (separate e-GP module) |
| **IFMIS** | Integrated Financial Management Information System (records disbursements) |
| **Standstill** | Statutory 14-day period between Notice of Award and contract signing |
| **Anchor** | Writing a SHA-256 hash of a document to a ledger as tamper-evidence |
| **Ghost project** | A disbursement with no independently verified completion |
| **Two-tier** | Public (aggregated/de-identified) vs restricted (named) output model |
| **PWA** | Progressive Web App (installable, offline-capable web app) |
