import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1",
  timeout: 30_000,
});

// Attach JWT from storage on every request
api.interceptors.request.use(cfg => {
  const token = localStorage.getItem("access_token");
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

// ── Types ─────────────────────────────────────────────────────────────────────

export interface LoginResponse { mfa_challenge_token?: string; access_token?: string; refresh_token?: string; token_type?: string; }
export interface MeResponse { id: string; name: string; email: string; role: { key: string; name: string; permissions: string[] }; institution?: { id: string; name: string; type: string } | null; mfa_enabled: boolean; }
export interface ContractRestricted { ocid: string; procuring_entity: string; supplier?: { id: string; name: string; tpin?: string; debarred_until?: string } | null; value?: number; currency: string; award_date?: string; signing_date?: string; framework_parent?: string; status: string; risk_score?: number; content_hash?: string; created_at: string; updated_at: string; }
export interface ContractListResponse { contracts: ContractRestricted[]; total: number; page: number; size: number; }
export interface CheckResult { check_id: number; check_key: string; result: string; evidence_note: string; weight_applied: number; }
export interface RiskScoreOut { contract_ocid: string; score: number; normalised_score: number; tier: string; flag_count: number; applicable_max: number; weights_version: string; breakdown: Record<string, { result: string; weight_applied: number; evidence_note: string }>; computed_at?: string; }

// ── Auth ─────────────────────────────────────────────────────────────────────

export const authApi = {
  login: (email: string, password: string) =>
    api.post<LoginResponse>("/auth/login", { email, password }),
  mfaVerify: (mfa_challenge_token: string, totp_code: string) =>
    api.post<LoginResponse>("/auth/mfa/verify", { mfa_challenge_token, totp_code }),
  me: () => api.get<MeResponse>("/auth/me"),
  logout: (refresh_token: string) =>
    api.post("/auth/logout", { refresh_token }),
};

// ── Contracts ─────────────────────────────────────────────────────────────────

export const contractsApi = {
  list: (params?: { page?: number; size?: number; min_score?: number; status?: string }) =>
    api.get<ContractListResponse>("/contracts", { params }),
  get: (ocid: string) => api.get<ContractRestricted>(`/contracts/${ocid}`),
  checks: (ocid: string) => api.get<CheckResult[]>(`/contracts/${ocid}/checks`),
  risk: (ocid: string) => api.get<RiskScoreOut>(`/contracts/${ocid}/risk`),
};

// ── Ingestion ─────────────────────────────────────────────────────────────────

export const ingestionApi = {
  runs: (params?: { page?: number; size?: number }) => api.get("/ingestion/runs", { params }),
  trigger: (source: string) => api.post("/ingestion/runs", { source }),
};

export interface PulseSubmissionRow {
  id: string; client_uuid: string; project_id: string; lat: number; lng: number;
  category: string | null; status: string; captured_at: string; ipfs_cid: string | null;
}

export const verifyApi = {
  listSubmissions: () => api.get<{ submissions: PulseSubmissionRow[]; total: number }>("/pulse/submissions"),
  confirm: (id: string) => api.post(`/pulse/submissions/${id}/confirm`, {}),
  reject: (id: string, reason: string) => api.post(`/pulse/submissions/${id}/reject`, { reason }),
};

export interface GhostSignal {
  id: string; disbursement_id: string; constituency_id: string | null; project_id: string | null;
  amount: number; disbursement_date: string; days_overdue: number; state: string; raised_at: string | null;
}
export interface DisbursementRow {
  id: string; constituency_id: string | null; project_id: string | null; contract_ocid: string | null;
  amount: number; date: string; source: string; matched_completion: boolean; matched_at: string | null;
}

export const monitorApi = {
  ghostQueue: () => api.get<{ total: number; signals: GhostSignal[] }>("/monitor/ghost-projects"),
  disbursements: () => api.get<{ total: number; disbursements: DisbursementRow[] }>("/monitor/disbursements"),
  mismatches: () => api.get<{ total: number; disbursements: DisbursementRow[] }>("/monitor/mismatches"),
  run: () => api.post("/monitor/run", {}),
  clear: (id: string, justification: string) => api.post(`/monitor/ghost-projects/${id}/clear`, { justification }),
};

export interface CaseNote { id: string; case_id: string; author_id: string; body: string; created_at: string; }
export interface CaseItem {
  id: string; subject_type: string; subject_ref: string; title: string; assignee_id: string | null;
  status: string; priority: string; created_by: string; created_at: string; closed_at: string | null; notes: CaseNote[];
}
export interface NotificationItem { id: string; type: string; payload: Record<string, unknown>; read: boolean; created_at: string; }

export const casesApi = {
  list: () => api.get<{ total: number; cases: CaseItem[] }>("/cases"),
  get: (id: string) => api.get<CaseItem>(`/cases/${id}`),
  create: (body: { subject_type: string; subject_ref: string; title: string; priority?: string }) => api.post<CaseItem>("/cases", body),
  update: (id: string, body: { status?: string; priority?: string }) => api.patch<CaseItem>(`/cases/${id}`, body),
  addNote: (id: string, bodyText: string) => api.post(`/cases/${id}/notes`, { body: bodyText }),
  escalate: (id: string, target = "ACC") => api.post(`/cases/${id}/escalate`, { target }),
};

export const notificationsApi = {
  list: () => api.get<{ total: number; unread: number; notifications: NotificationItem[] }>("/notifications"),
  markRead: (id: string) => api.post(`/notifications/${id}/read`),
};
