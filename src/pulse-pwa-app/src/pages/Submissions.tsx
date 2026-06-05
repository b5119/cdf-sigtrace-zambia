import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import PhoneShell from "../components/PhoneShell";
import { getAllSubmissions, type QueuedSubmission } from "../lib/db";
import { syncPending, onReconnect } from "../lib/sync";
import { useOnline } from "../store/useOnline";

// Design-sample queue — shown when the local queue is empty (fresh device / demo).
const SAMPLE_SUBS: QueuedSubmission[] = [
  { client_uuid: "sub-001", project_id: "proj-001", lat: -15.412, lng: 28.301, category: "Borehole", captured_at: "2026-06-02T11:20:00Z", sync_status: "synced", server_id: "srv-001", created_at: "2026-06-02T11:20:00Z" },
  { client_uuid: "sub-002", project_id: "proj-002", lat: -15.413, lng: 28.302, category: "Clinic Annex", captured_at: "2026-06-03T09:05:00Z", sync_status: "synced", server_id: "srv-002", created_at: "2026-06-03T09:05:00Z" },
  { client_uuid: "sub-003", project_id: "proj-003", lat: -15.414, lng: 28.303, category: "Classroom Block", captured_at: "2026-06-04T14:40:00Z", sync_status: "pending", created_at: "2026-06-04T14:40:00Z" },
];

export default function Submissions() {
  const online = useOnline();
  const [subs, setSubs] = useState<QueuedSubmission[]>([]);
  const [syncing, setSyncing] = useState(false);
  const [lastSync, setLastSync] = useState<string | null>(null);

  const refresh = useCallback(async () => setSubs(await getAllSubmissions()), []);

  const doSync = useCallback(async () => {
    setSyncing(true);
    const res = await syncPending();
    setLastSync(`${res.synced} synced, ${res.duplicates} already on server`);
    await refresh();
    setSyncing(false);
  }, [refresh]);

  useEffect(() => { refresh(); }, [refresh]);
  // Auto-sync on reconnect
  useEffect(() => onReconnect(() => { doSync(); }), [doSync]);
  // Auto-sync on mount if online + pending
  useEffect(() => { if (online) doSync(); /* eslint-disable-next-line */ }, []);

  const pendingCount = subs.filter(s => s.sync_status === "pending").length;

  return (
    <PhoneShell title="Submissions">
      <div className="p-4">
        {/* Sync bar */}
        <div className="bg-card border border-outline-variant rounded-xl p-3 mb-4 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold">{pendingCount} pending</p>
            {lastSync && <p className="text-xs text-on-surface-variant">{lastSync}</p>}
          </div>
          <button onClick={doSync} disabled={!online || syncing || pendingCount === 0}
            className="text-sm font-semibold px-3 py-1.5 rounded-lg bg-primary text-white disabled:opacity-50 flex items-center gap-1">
            <span className={`material-symbols-outlined ${syncing ? "animate-spin" : ""}`} style={{ fontSize: 18 }}>sync</span>
            {syncing ? "Syncing…" : "Sync now"}
          </button>
        </div>

        {!online && (
          <div className="bg-risk-mid/5 border border-risk-mid/30 rounded-lg p-2.5 mb-4 text-xs text-risk-mid flex items-center gap-2">
            <span className="material-symbols-outlined" style={{ fontSize: 16 }}>wifi_off</span>
            Offline — submissions will sync automatically when reconnected
          </div>
        )}

        {/* Submission list (sample rows shown when the local queue is empty) */}
        <div className="space-y-3">
          {(subs.length ? subs : SAMPLE_SUBS).map(s => (
            <Link key={s.client_uuid} to={`/submissions/${s.client_uuid}`}
              className="block bg-card border border-outline-variant rounded-xl p-3 hover:border-primary/40">
              <div className="flex items-center justify-between">
                <div className="min-w-0">
                  <p className="text-sm font-semibold truncate">{s.category ?? "Evidence"}</p>
                  <p className="text-xs text-on-surface-variant mono">{s.lat.toFixed(3)}, {s.lng.toFixed(3)}</p>
                  <p className="text-xs text-on-surface-variant">{new Date(s.captured_at).toLocaleString()}</p>
                </div>
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                  s.sync_status === "synced" ? "bg-risk-low/10 text-risk-low" :
                  s.sync_status === "error" ? "bg-risk-high/10 text-risk-high" :
                  "bg-risk-mid/10 text-risk-mid"
                }`}>
                  {s.sync_status === "synced" ? "✓ synced" : s.sync_status === "error" ? "error" : "pending"}
                </span>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </PhoneShell>
  );
}
