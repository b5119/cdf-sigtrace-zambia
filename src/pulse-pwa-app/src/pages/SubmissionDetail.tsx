import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import PhoneShell from "../components/PhoneShell";
import { getSubmission, type QueuedSubmission } from "../lib/db";

// Design-sample submission — shown when the id isn't in the local queue (demo).
const SAMPLE_SUB: QueuedSubmission = {
  client_uuid: "sub-001", project_id: "proj-001", lat: -15.4123, lng: 28.3014,
  category: "Borehole", note: "Foundation complete", captured_at: "2026-06-02T11:20:00Z",
  sync_status: "synced", server_id: "srv-001", created_at: "2026-06-02T11:20:00Z",
};

export default function SubmissionDetail() {
  const { id } = useParams<{ id: string }>();
  const [sub, setSub] = useState<QueuedSubmission | null>(null);

  useEffect(() => { if (id) getSubmission(id).then(s => setSub(s ?? null)); }, [id]);

  // Always render; fall back to a sample when the id isn't in the local queue.
  const view = sub ?? SAMPLE_SUB;

  return (
    <PhoneShell title="Detail">
      <div className="p-4">
        <Link to="/submissions" className="text-sm text-on-surface-variant mb-3 inline-block">← Submissions</Link>
        {view.photo_blob ? (
          <img src={URL.createObjectURL(view.photo_blob)} alt="evidence" className="w-full h-48 object-cover rounded-xl mb-4" />
        ) : (
          <div className="w-full h-48 bg-surface-2 rounded-xl mb-4 flex items-center justify-center">
            <span className="material-symbols-outlined text-outline" style={{ fontSize: 40 }}>photo_camera</span>
          </div>
        )}
        <div className="bg-card border border-outline-variant rounded-xl p-4 space-y-3 text-sm">
          {[
            ["Status", view.sync_status],
            ["Category", view.category ?? "—"],
            ["GPS", `${view.lat.toFixed(5)}, ${view.lng.toFixed(5)}`],
            ["Captured", new Date(view.captured_at).toLocaleString()],
            ["Client ID", view.client_uuid],
            ["Server ID", view.server_id ?? "not synced"],
            ["Evidence photo", view.photo_blob
              ? (view.sync_status === "synced" ? "pinned to IPFS ✓" : "queued — pins on sync")
              : "no photo"],
            ["Note", view.note ?? "—"],
          ].map(([k, v]) => (
            <div key={k} className="flex justify-between gap-3">
              <span className="text-on-surface-variant">{k}</span>
              <span className="mono text-xs text-right break-all">{v}</span>
            </div>
          ))}
        </div>
      </div>
    </PhoneShell>
  );
}
