import axios from "axios";
import type { QueuedSubmission } from "./db";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1",
  timeout: 20_000,
});

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem("pulse_token");
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

export interface AssignmentProject { id: string; title: string; category: string; status: string; constituency_id: string; constituency_name: string; }
export interface AssignmentsResponse { constituency_id: string; constituency_name: string; projects: AssignmentProject[]; }
export interface SyncResult { synced: number; duplicates: number; submissions: { id: string; client_uuid: string }[]; }

export const pulseApi = {
  login: (email: string, password: string) =>
    api.post("/auth/login", { email, password }),
  mfaVerify: (mfa_challenge_token: string, totp_code: string) =>
    api.post("/auth/mfa/verify", { mfa_challenge_token, totp_code }),
  assignments: () => api.get<AssignmentsResponse>("/pulse/assignments"),
  syncBatch: (subs: QueuedSubmission[]) =>
    api.post<SyncResult>("/pulse/sync", {
      submissions: subs.map(s => ({
        client_uuid: s.client_uuid,
        project_id: s.project_id,
        constituency_id: s.constituency_id,
        lat: s.lat,
        lng: s.lng,
        category: s.category,
        note: s.note,
        captured_at: s.captured_at,
      })),
    }),
};

export const evidenceApi = {
  uploadPhoto: (submissionId: string, photo: Blob) => {
    const fd = new FormData();
    fd.append("file", photo, "evidence.jpg");
    return api.post(`/pulse/submissions/${submissionId}/photo`, fd);
  },
};

export interface SubmissionServer {
  id: string; client_uuid: string; project_id: string; lat: number; lng: number;
  category: string | null; status: string; captured_at: string; ipfs_cid: string | null;
}

export const confirmApi = {
  listSubmissions: () => api.get<{ submissions: SubmissionServer[]; total: number }>("/pulse/submissions"),
  confirm: (id: string) => api.post(`/pulse/submissions/${id}/confirm`, {}),
  reject: (id: string, reason: string) => api.post(`/pulse/submissions/${id}/reject`, { reason }),
};
