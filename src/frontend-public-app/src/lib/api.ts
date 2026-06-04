import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1",
  timeout: 30_000,
});

// ── Types ─────────────────────────────────────────────────────────────────────

export interface NationalKPIs {
  total_contracts: number;
  total_value_zmw: number | null;
  verified_contracts: number;
  high_risk_contracts: number;
  ghost_project_signals: number;
  constituencies_covered: number;
}

export interface MapFeature {
  id: string;
  name: string;
  province: string;
  lat: number;
  lng: number;
  project_count: number;
  verified_count: number;
  risk_score: number | null;
  risk_tier: "high" | "medium" | "low" | null;
  cdf_allocation: number | null;
}

export interface MapResponse {
  type: string;
  count: number;
  features: MapFeature[];
}

export interface ConstituencySummary {
  id: string;
  name: string;
  province: string;
  project_count: number;
  verified_count: number;
  risk_aggregate: "high" | "medium" | "low" | null;
}

export interface ConstituencyDetail extends ConstituencySummary {
  cdf_allocation: number | null;
  geo: { type: string; coordinates: [number, number] } | null;
}

export interface RiskAggregateRow {
  entity_label: string;
  sector: string;
  contract_count: number;
  avg_risk_score: number | null;
  high_risk_count: number;
  total_value_zmw: number | null;
}

export interface RiskAggregateResponse {
  entities: RiskAggregateRow[];
  generated_at: string;
}

export interface OpenDataMeta {
  dataset: string;
  record_count: number;
  generated_at: string;
  note: string;
  data: Record<string, unknown>[];
}

export interface VerifyResponse {
  verdict: "match" | "mismatch" | "not_registered";
  message: string;
  provided_hash: string;
  anchored_hash: string | null;
  ledger: string | null;
  ledger_tx: string | null;
  block_ref: string | null;
  anchored_at: string | null;
}

// ── API calls ────────────────────────────────────────────────────────────────

export const publicApi = {
  overview: () => api.get<NationalKPIs>("/public/overview"),
  map: () => api.get<MapResponse>("/public/map"),
  constituencies: () => api.get<{ total: number; constituencies: ConstituencySummary[] }>("/public/constituencies"),
  constituency: (id: string) => api.get<ConstituencyDetail>(`/public/constituencies/${id}`),
  riskAggregate: () => api.get<RiskAggregateResponse>("/public/risk/aggregate"),
  opendata: (dataset: string) => api.get<OpenDataMeta>(`/public/opendata/${dataset}`),
  verifyContract: (ocid: string, file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return api.post<VerifyResponse>(`/public/verify-contract?ocid=${encodeURIComponent(ocid)}`, fd);
  },
  publicAnchor: (ocid: string) => api.get(`/public/anchors/${encodeURIComponent(ocid)}`),
};

export interface EvidenceItem {
  submission_id: string; ipfs_cid: string | null; lat: number; lng: number;
  category: string | null; captured_at: string; status: string;
  confirmation_count: number; onchain_tx: string | null;
}
export interface ProjectDetail {
  project_id: string; constituency_id: string | null; title: string; category: string;
  status: string; verified: boolean; disbursement_amount: number | null;
  disbursement_date: string | null; evidence_count: number; confirmed_count: number;
  location: { lat: number; lng: number } | null;
}

export const projectApi = {
  detail: (id: string) => api.get<ProjectDetail>(`/public/projects/${id}`),
  evidence: (id: string) => api.get<{ project_id: string; total: number; evidence: EvidenceItem[] }>(`/public/projects/${id}/evidence`),
  photoUrl: (cid: string) => `${api.defaults.baseURL}/public/evidence/${cid}`,
};
