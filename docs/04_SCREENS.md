# 04 · Screens (complete inventory, by role)

Every screen the whole system will have. Schematics for the major dashboards are in `schematics/`.
Each screen lists: **role(s)**, **purpose**, **key components**, **data/endpoints**, **actions**.
WCAG 2.1 AA is the target for all public + Pulse screens.

Legend of apps: **PUB** = public portal · **OVS** = oversight console · **PWA** = CDF Pulse ·
**ADM** = admin (within OVS).

---

## A. Public portal (role: `anonymous`)  — app PUB
Schematic: `wf_public_dashboard.png`, `wf_verification_portal.png`

| # | Screen | Purpose / components | Data |
|---|--------|----------------------|------|
| P1 | **Landing / Home** | Mission, entry points (verify, explore map, methodology), top-line KPIs | `/public/overview` |
| P2 | **National Dashboard** | KPI cards (allocation, projects, verified, ghost flags); constituency risk heat-map; recent verified projects/flags feed | `/public/overview`, `/public/map` |
| P3 | **Project Map** | MapLibre choropleth of 156 constituencies; click → constituency; layer toggles (verified/pending/mismatch) | `/public/map` |
| P4 | **Constituency Detail** | Allocation, project list with status, aggregate risk | `/public/constituencies/{id}` |
| P5 | **Project Detail (public)** | Disbursement summary, photographic evidence (from IPFS), verified location on mini-map, confirmation status | `/public/projects/{id}`, `/pulse/projects/{id}/evidence` |
| P6 | **Contract Verification Portal** | Drag-drop a contract PDF → local SHA-256 → match/mismatch result with anchor metadata | `POST /public/verify-contract` |
| P7 | **Procurement Risk Overview** | De-identified risk by procuring entity / sector (aggregate only — no names) | `/public/risk/aggregate` |
| P8 | **Open Data** | Downloadable aggregated datasets (CSV/JSON), API docs link | `/public/opendata/{dataset}` |
| P9 | **About / Methodology / FAQ** | How checks work, "signals not findings" disclaimer, data-protection notice | static |

---

## B. CDF Pulse field app (roles: `community_monitor`, `inst_confirmer`)  — app PWA
Schematic: `wf_pulse_mobile.png`. Offline-first; installable.

| # | Screen | Purpose / components | Data |
|---|--------|----------------------|------|
| M1 | **Login / device registration** | Monitor sign-in; device-bound credential; offline grace | `/auth/login`, `/auth/mfa/verify` |
| M2 | **Home / assignments** | Assigned constituency + project list; "New capture" | `/pulse/assignments` |
| M3 | **Capture submission** | Camera viewfinder; auto GPS lock + timestamp; category, notes; offline indicator | `POST /pulse/submissions` |
| M4 | **Review & submit** | Confirm photo/location/metadata before queueing | (local) |
| M5 | **My submissions / sync queue** | List with sync status (synced / pending-offline); manual sync | `/pulse/submissions`, `POST /pulse/sync` |
| M6 | **Submission detail** | Photo, IPFS CID, location, confirmation status | `/pulse/submissions/{id}` |
| M7 | **Confirmation inbox** *(inst_confirmer)* | Submissions awaiting my confirmation; confirm/reject | `POST /pulse/submissions/{id}/confirm` · `/reject` |
| M8 | **Profile / settings** | Account, storage/sync settings, sign-out | `/auth/me` |

---

## C. Oversight console (roles: `oversight_officer`, `analyst`)  — app OVS
Schematics: `wf_oag_dashboard.png`, `wf_contract_detail.png`, `wf_ghost_project_queue.png`

| # | Screen | Purpose / components | Data |
|---|--------|----------------------|------|
| O1 | **Login (MFA)** | Restricted-tier sign-in | `/auth/*` |
| O2 | **Risk Dashboard (home)** | KPI cards (open flags, high-risk contracts, ghost signals, open cases); trend charts; alert feed | `/contracts`, `/monitor/ghost-projects`, `/cases` |
| O3 | **Contract Risk List** | Sortable/filterable table: OCID, entity, risk score (colour), flags, anchor status, action | `/contracts` |
| O4 | **Contract Detail / Anomaly Review** | The 8 check results with evidence; value/dates; hash/anchor status; actions (add to case, escalate, mark reviewed) | `/contracts/{ocid}/checks`, `/anchors/{ocid}` |
| O5 | **Supplier Network Graph** | Related-party graph (shared address/phone/shareholders) for a tender | `/suppliers/network` |
| O6 | **Ghost-Project Queue** | Disbursements with no verified completion; days overdue; evidence status; open case | `/monitor/ghost-projects` |
| O7 | **Disbursement / Mismatch Explorer** | All disbursements + match status; drill to contract & delivery | `/monitor/disbursements`, `/monitor/mismatches` |
| O8 | **Project Verification Review** | Field submissions awaiting institutional confirmation; confirm/reject | `/pulse/submissions`, confirm/reject |
| O9 | **Document Verification Console** | Verify any uploaded contract vs anchor (named context) | `POST /verify`, `POST /anchors` |
| O10 | **Cases** | Case list, detail, notes, status, assignee, escalate | `/cases/*` |
| O11 | **Analytics** *(analyst)* | Anomaly-rate trends, entity comparisons, saved views | `/public/risk/aggregate`, `/contracts` |
| O12 | **Reports & Exports** | Generate restricted reports (PDF/CSV); export with audit entry | `/contracts`, `/monitor/*` |
| O13 | **Notifications** | Alerts (new high-risk, new ghost signal, confirmation requests) | `/notifications` |

---

## D. Admin console (role: `system_admin`)  — app ADM
Schematic: `wf_admin_console.png`

| # | Screen | Purpose / components | Data |
|---|--------|----------------------|------|
| S1 | **Admin Home** | System health (DB, Redis, Fabric peers, Polygon RPC, IPFS, pipeline); quick links | `/admin/health` |
| S2 | **Users & Roles** | CRUD users; assign role + institution; activate/deactivate; force MFA reset | `/admin/users`, `/admin/roles` |
| S3 | **Check Weights** | Tune the 8 check weights (sliders); versioned; calibrate with OAG | `/admin/config/weights` |
| S4 | **Thresholds** | Standstill days, amendment cap %, time-gap min, high-risk threshold, ghost-project window | `/admin/config/thresholds` |
| S5 | **Ingestion Management** | OCDS pipeline status; run/schedule; error log; record counts | `/ingestion/runs` |
| S6 | **Ledger & Node Governance** | Fabric peers/MSP status; Polygon contract address & signer; anchor backlog | `/admin/ledger/nodes` |
| S7 | **Institutions & Agreements** | Institutions + data-sharing agreements that govern restricted access | `/admin/institutions` |
| S8 | **Audit Log Viewer** | Immutable, filterable action log; anchor batch status | `/admin/audit` |
| S9 | **Notification Templates / Config** | Alert rules and templates | `/admin/config/*` |

---

## E. Shared / system screens (all roles as applicable)
| # | Screen | Purpose |
|---|--------|---------|
| X1 | **Login** | Email+password (restricted) |
| X2 | **MFA Challenge** | TOTP entry |
| X3 | **Forgot / Reset Password** | Self-service reset |
| X4 | **Account / Session Settings** | Profile, MFA device, active sessions, sign-out everywhere |
| X5 | **Error / 403 / 404 / Offline** | Friendly states; PWA offline screen |
| X6 | **Consent / Data-Protection Notice** | Plain-language privacy notice (public + monitor onboarding) |

---

## Screen count summary
- Public: **9** · CDF Pulse: **8** · Oversight: **13** · Admin: **9** · Shared: **6** → **~45 screens**.

## Build mapping (which increment delivers which screens)
- INC-007 → P6 · INC-008 → P1–P4, P7–P9 · INC-014 → P5 (Pulse evidence)
- INC-001 → X1–X4, O1, M1 · INC-009 → O2–O5, O11–O13
- INC-010 → M2–M6, M8 · INC-013 → M7, O8 · INC-015 → O6, O7
- INC-016 → O10 · INC-017 → S1–S9 · INC-018/019 → X5, X6, accessibility passes
