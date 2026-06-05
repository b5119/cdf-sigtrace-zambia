import { useEffect, useState, useCallback } from "react";
import PhoneShell from "../components/PhoneShell";
import { confirmApi, type SubmissionServer } from "../lib/api";

// Design-sample confirmation inbox — shown when the API is unavailable (demo).
const SAMPLE_CONFIRM: SubmissionServer[] = [
  { id: "srv-101", client_uuid: "c1", project_id: "proj-001", lat: -15.4101, lng: 28.3001, category: "Borehole", status: "pending", captured_at: "2026-06-04T10:00:00Z", ipfs_cid: "Qm…f1" },
  { id: "srv-102", client_uuid: "c2", project_id: "proj-002", lat: -15.4112, lng: 28.3025, category: "Clinic Annex", status: "pending", captured_at: "2026-06-04T11:30:00Z", ipfs_cid: null },
];

export default function Confirm() {
  const [subs, setSubs] = useState<SubmissionServer[]>(SAMPLE_CONFIRM);
  const [busy, setBusy] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const res = await confirmApi.listSubmissions();
      const pending = res.data.submissions.filter(s => s.status === "pending");
      // Confirmation inbox = submissions still pending; keep the sample when the server has none (demo).
      setSubs(pending.length ? pending : SAMPLE_CONFIRM);
    } catch { setSubs(SAMPLE_CONFIRM); }
  }, []);

  useEffect(() => { load(); }, [load]);

  async function doConfirm(id: string) {
    setBusy(id); setMsg(null);
    try {
      const r = await confirmApi.confirm(id);
      setMsg(r.data.complete ? "✓ Confirmed — submission now complete" : `Confirmed (${r.data.confirmation_count}/${r.data.required})`);
      await load();
    } catch (e: any) {
      setMsg(e?.response?.data?.detail ?? "Confirmation failed");
    } finally { setBusy(null); }
  }

  async function doReject(id: string) {
    const reason = prompt("Reason for rejection:");
    if (!reason) return;
    setBusy(id); setMsg(null);
    try {
      await confirmApi.reject(id, reason);
      setMsg("Submission rejected");
      await load();
    } catch (e: any) {
      setMsg(e?.response?.data?.detail ?? "Rejection failed");
    } finally { setBusy(null); }
  }

  return (
    <PhoneShell title="Confirm">
      <div className="p-4">
        <h2 className="font-display font-semibold mb-1">Confirmation inbox</h2>
        <p className="text-xs text-on-surface-variant mb-4">Submissions awaiting your institutional confirmation. Two distinct confirmers are required.</p>
        {msg && <div className="bg-primary/5 border border-primary/20 rounded-lg px-3 py-2 text-xs text-primary mb-3">{msg}</div>}
        <div className="space-y-3">
          {subs.map(s => (
            <div key={s.id} className="bg-card border border-outline-variant rounded-xl p-3">
              <p className="text-sm font-semibold">{s.category ?? "Evidence"}</p>
              <p className="text-xs text-on-surface-variant mono">{s.lat.toFixed(4)}, {s.lng.toFixed(4)}</p>
              <p className="text-xs text-on-surface-variant">{new Date(s.captured_at).toLocaleString()}</p>
              {s.ipfs_cid && <p className="text-[10px] text-on-surface-variant mono truncate mt-1">IPFS {s.ipfs_cid}</p>}
              <div className="flex gap-2 mt-3">
                <button disabled={busy === s.id} onClick={() => doConfirm(s.id)}
                  className="flex-1 bg-primary text-white text-sm font-semibold py-2 rounded-lg disabled:opacity-50 flex items-center justify-center gap-1">
                  <span className="material-symbols-outlined" style={{ fontSize: 18 }}>check</span>Confirm
                </button>
                <button disabled={busy === s.id} onClick={() => doReject(s.id)}
                  className="flex-1 border border-risk-high/30 text-risk-high text-sm font-semibold py-2 rounded-lg disabled:opacity-50 flex items-center justify-center gap-1">
                  <span className="material-symbols-outlined" style={{ fontSize: 18 }}>close</span>Reject
                </button>
              </div>
            </div>
          ))}
          {subs.length === 0 && (
            <div className="text-center py-12 text-on-surface-variant">
              <span className="material-symbols-outlined text-4xl">fact_check</span>
              <p className="text-sm mt-2">No submissions awaiting confirmation</p>
            </div>
          )}
        </div>
      </div>
    </PhoneShell>
  );
}
