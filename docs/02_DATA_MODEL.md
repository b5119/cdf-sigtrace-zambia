# 02 · Data Model

See `schematics/erd.png` for the visual ERD. Field lists are indicative; finalise types in
`backend/models` + Alembic migrations. PII is marked **(PII — off-chain, restricted)**.

## Core procurement (SigTrace)
### Contract
| Field | Type | Notes |
|-------|------|-------|
| ocid | str PK | Open Contracting ID |
| procuring_entity | str | |
| supplier_id | FK → Supplier | awarded supplier |
| value | numeric | contract value (ZMW) |
| award_date | date | Notice of Award |
| signing_date | date \| null | may be absent (check 1) |
| signing_doc_ref | str \| null | object-store key of scanned PDF |
| framework_parent | str \| null | OCID of parent framework (excludes call-off from single-source logic) |
| status | enum | active / complete / cancelled |
| risk_score | int | 0–100, computed |
| raw_ocds | jsonb | original record |

### CheckDefinition
`id (1–8)`, `key`, `name`, `basis`, `severity`, `weight` (configurable), `enabled`.

### AnomalyFlag
`id PK`, `contract_ocid FK`, `check_id FK`, `result` (flag/ok), `weight_applied`, `evidence_note`, `created_at`.

### RiskScore (or computed on Contract)
`contract_ocid FK`, `score`, `breakdown jsonb`, `computed_at`, `weights_version`.

### Supplier
`id PK`, `name`, `tpin`, `address`, `phone`, `shareholders jsonb`, `debarred_until date|null`.

### SupplierLink
`id PK`, `supplier_a FK`, `supplier_b FK`, `shared_attr` (address/phone/shareholder), `tender_ref`.

### AnchorRecord
`id PK`, `contract_ocid FK`, `sha256`, `ledger` (fabric), `ledger_tx`, `block_ref`, `anchored_at`.

## Delivery (CDF Pulse)
### Constituency
`id PK`, `name`, `province`, `geo jsonb` (boundary), `cdf_allocation`.

### Project
`id PK`, `constituency_id FK`, `title`, `category`, `status`, `verified bool`, `created_at`.

### Disbursement
`id PK`, `constituency_id FK`, `project_id FK|null`, `amount`, `date`, `source` (IFMIS),
`matched_completion bool`, `matched_at`.

### PulseSubmission
| Field | Type | Notes |
|-------|------|-------|
| id PK | uuid | |
| project_id | FK | |
| monitor_id | FK → User | **(PII — off-chain, restricted)** |
| ipfs_cid | str | content hash of the photo |
| lat / lng | float | captured at photo time |
| captured_at | datetime | device timestamp |
| synced_at | datetime\|null | offline → online |
| status | enum | pending / confirmed / rejected |
| onchain_tx | str\|null | Polygon tx of the submission record |

### Confirmation
`id PK`, `submission_id FK`, `confirmer_id FK → User`, `signature`, `confirmed_at`, `onchain_tx`.

### GhostProjectSignal
`id PK`, `disbursement_id FK`, `days_overdue`, `state` (open/cleared/escalated), `raised_at`.

## Oversight & platform
### User  **(PII — restricted)**
`id PK`, `name`, `email`, `password_hash`, `mfa_secret`, `role FK`, `institution_id FK|null`,
`active`, `created_at`, `last_login`.

### Role
`id PK`, `key` (anonymous/community_monitor/inst_confirmer/oversight_officer/analyst/system_admin),
`name`, `permissions jsonb`.

### Institution
`id PK`, `name` (OAG/ACC/ZPPA/…), `type`, `data_sharing_agreement_ref`.

### Case
`id PK`, `subject_type` (contract/ghost_project), `subject_ref`, `assignee_id FK`, `status`,
`priority`, `created_at`, `closed_at`.

### CaseNote
`id PK`, `case_id FK`, `author_id FK`, `body`, `created_at`.

### Notification
`id PK`, `user_id FK`, `type`, `payload jsonb`, `read bool`, `created_at`.

### IngestionRun
`id PK`, `started_at`, `finished_at`, `records_in`, `records_loaded`, `errors jsonb`, `status`.

### Config
`key` PK (e.g. `weights`, `standstill_days`, `amendment_cap`, `ghost_window_days`,
`high_risk_threshold`), `value jsonb`, `updated_by FK`, `updated_at`, `version`.

### AuditLog (append-only)
`id PK`, `actor_id FK|null`, `action`, `target_type`, `target_ref`, `meta jsonb`, `created_at`,
`anchor_hash` (periodic batch anchored to Fabric for tamper-evidence).

## Relationships (summary)
- Contract 1—* AnomalyFlag; Contract 1—1 AnchorRecord; Contract *—1 Supplier.
- Supplier *—* Supplier via SupplierLink.
- Constituency 1—* Project 1—* Disbursement; Project 1—* PulseSubmission 1—* Confirmation.
- Disbursement 1—0..1 GhostProjectSignal.
- User *—1 Role; User *—0..1 Institution; Case 1—* CaseNote.
