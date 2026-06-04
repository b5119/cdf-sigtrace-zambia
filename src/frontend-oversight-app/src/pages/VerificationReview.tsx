import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { verifyApi } from "../lib/api";

const STATUS_STYLE: Record<string, string> = {
  pending:   "bg-risk-mid/10 text-risk-mid",
  confirmed: "bg-risk-low/10 text-risk-low",
  rejected:  "bg-risk-high/10 text-risk-high",
};

export default function VerificationReview() {
  const qc = useQueryClient();
  const [msg, setMsg] = useState<string | null>(null);

  const { data } = useQuery({
    queryKey: ["pulse-submissions"],
    queryFn: () => verifyApi.listSubmissions().then(r => r.data),
  });

  const confirmM = useMutation({
    mutationFn: (id: string) => verifyApi.confirm(id),
    onSuccess: (r) => {
      setMsg(r.data.complete ? "✓ Completed — 2 distinct confirmations recorded on Polygon" : `Confirmed (${r.data.confirmation_count}/${r.data.required})`);
      qc.invalidateQueries({ queryKey: ["pulse-submissions"] });
    },
    onError: (e: any) => setMsg(e?.response?.data?.detail ?? "Confirmation failed"),
  });

  const rejectM = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) => verifyApi.reject(id, reason),
    onSuccess: () => { setMsg("Submission rejected"); qc.invalidateQueries({ queryKey: ["pulse-submissions"] }); },
    onError: (e: any) => setMsg(e?.response?.data?.detail ?? "Rejection failed"),
  });

  const submissions = data?.submissions ?? [];

  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-ink mb-1">Project Verification Review</h1>
      <p className="text-sm text-on-surface-variant mb-6">Field submissions awaiting institutional confirmation. Two distinct confirmers required (recorded on Polygon).</p>

      {msg && <div className="bg-primary/5 border border-primary/20 rounded-lg px-4 py-2.5 text-sm text-primary mb-4">{msg}</div>}

      <div className="bg-card border border-outline-variant rounded-xl overflow-hidden">
        <table className="w-full">
          <thead className="bg-surface-2">
            <tr>{["Submission", "Project", "Location", "Captured", "IPFS CID", "Status", "Actions"].map(h => (
              <th key={h} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-3 px-3">{h}</th>
            ))}</tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/60">
            {submissions.map(s => (
              <tr key={s.id} className="hover:bg-surface-2/50">
                <td className="py-2.5 px-3 mono text-xs text-primary">{s.id.slice(0, 8)}…</td>
                <td className="py-2.5 px-3 text-sm">{s.project_id}</td>
                <td className="py-2.5 px-3 mono text-xs">{s.lat.toFixed(3)}, {s.lng.toFixed(3)}</td>
                <td className="py-2.5 px-3 text-xs text-on-surface-variant">{new Date(s.captured_at).toLocaleDateString()}</td>
                <td className="py-2.5 px-3 mono text-[10px] text-on-surface-variant">{s.ipfs_cid ? s.ipfs_cid.slice(0, 12) + "…" : "—"}</td>
                <td className="py-2.5 px-3"><span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${STATUS_STYLE[s.status]}`}>{s.status}</span></td>
                <td className="py-2.5 px-3">
                  {s.status === "pending" && (
                    <div className="flex gap-1.5">
                      <button onClick={() => confirmM.mutate(s.id)} disabled={confirmM.isPending}
                        className="text-xs font-semibold px-2.5 py-1 rounded bg-primary text-white hover:bg-primary-h disabled:opacity-50">Confirm</button>
                      <button onClick={() => { const r = prompt("Reason:"); if (r) rejectM.mutate({ id: s.id, reason: r }); }}
                        className="text-xs font-semibold px-2.5 py-1 rounded border border-risk-high/30 text-risk-high hover:bg-risk-high/5">Reject</button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
            {submissions.length === 0 && (
              <tr><td colSpan={7} className="py-8 text-center text-on-surface-variant text-sm">No field submissions yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
