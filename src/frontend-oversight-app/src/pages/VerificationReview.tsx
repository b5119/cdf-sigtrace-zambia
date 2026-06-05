import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { verifyApi, type PulseSubmissionRow } from "../lib/api";

const SAMPLE_SUBMISSIONS: PulseSubmissionRow[] = [
  { id: "p1", client_uuid: "c1", project_id: "1", lat: -15.41, lng: 28.30, category: null, status: "pending", captured_at: "2026-05-28", ipfs_cid: null },
  { id: "p2", client_uuid: "c2", project_id: "2", lat: -15.41, lng: 28.30, category: null, status: "pending", captured_at: "2026-05-29", ipfs_cid: null },
  { id: "p3", client_uuid: "c3", project_id: "3", lat: -15.41, lng: 28.30, category: null, status: "pending", captured_at: "2026-05-30", ipfs_cid: null },
  { id: "p4", client_uuid: "c4", project_id: "4", lat: -15.41, lng: 28.30, category: null, status: "pending", captured_at: "2026-05-31", ipfs_cid: null },
];

export default function VerificationReview() {
  const qc = useQueryClient();
  const [msg, setMsg] = useState<string | null>(null);

  const { data } = useQuery({
    queryKey: ["pulse-submissions"],
    queryFn: () => verifyApi.listSubmissions().then(r => r.data),
  });

  const confirmM = useMutation({
    mutationFn: (id: string) => verifyApi.confirm(id),
    onSuccess: () => { setMsg("Submission confirmed"); qc.invalidateQueries({ queryKey: ["pulse-submissions"] }); },
    onError: (e: any) => setMsg(e?.response?.data?.detail ?? "Confirmation failed"),
  });

  const rejectM = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) => verifyApi.reject(id, reason),
    onSuccess: () => { setMsg("Submission rejected"); qc.invalidateQueries({ queryKey: ["pulse-submissions"] }); },
    onError: (e: any) => setMsg(e?.response?.data?.detail ?? "Rejection failed"),
  });

  const submissions = data?.submissions ?? SAMPLE_SUBMISSIONS;

  return (
    <div>
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl font-bold text-ink">Verification Review</h1>
          <p className="text-sm text-on-surface-variant mt-1">Field submissions awaiting confirmation</p>
        </div>
        <div className="flex gap-2" />
      </div>

      {msg && <div className="bg-primary/5 border border-primary/20 rounded-lg px-4 py-2.5 text-sm text-primary mb-4">{msg}</div>}

      <div className="grid grid-cols-2 gap-4">
        {submissions.map(s => (
          <div key={s.id} className="bg-card border border-outline-variant rounded-xl p-5">
            <div className="flex gap-3">
              <div className="w-24 h-24 rounded-lg bg-surface-2 shrink-0 flex items-center justify-center">
                <span className="material-symbols-outlined text-outline">image</span>
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold">Project #{s.project_id}</p>
                <p className="mono text-xs text-on-surface-variant">
                  {s.lat.toFixed(2)}, {s.lng.toFixed(2)} · {s.captured_at}
                </p>
                <div className="flex gap-2 mt-3">
                  <button
                    onClick={() => confirmM.mutate(s.id)}
                    disabled={confirmM.isPending}
                    className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 bg-primary text-white disabled:opacity-50"
                  >
                    <span className="material-symbols-outlined">check</span>Confirm
                  </button>
                  <button
                    onClick={() => { const r = prompt("Reason:"); if (r) rejectM.mutate({ id: s.id, reason: r }); }}
                    className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 text-ink hover:bg-surface-2"
                  >
                    <span className="material-symbols-outlined">close</span>Reject
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
