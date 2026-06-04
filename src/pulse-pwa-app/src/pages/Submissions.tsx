import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import PhoneShell from "../components/PhoneShell";
import { getAllSubmissions, type QueuedSubmission } from "../lib/db";
import { syncPending, onReconnect } from "../lib/sync";
import { useOnline } from "../store/useOnline";

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

        {/* Submission list */}
        <div className="space-y-3">
          {subs.map(s => (
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
          {subs.length === 0 && (
            <div className="text-center py-12 text-on-surface-variant">
              <span className="material-symbols-outlined text-4xl">inbox</span>
              <p className="text-sm mt-2">No submissions yet</p>
              <Link to="/capture" className="text-primary text-sm font-semibold mt-2 inline-block">Capture your first →</Link>
            </div>
          )}
        </div>
      </div>
    </PhoneShell>
  );
}
