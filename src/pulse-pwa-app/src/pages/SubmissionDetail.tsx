import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import PhoneShell from "../components/PhoneShell";
import { getSubmission, type QueuedSubmission } from "../lib/db";

export default function SubmissionDetail() {
  const { id } = useParams<{ id: string }>();
  const [sub, setSub] = useState<QueuedSubmission | null>(null);

  useEffect(() => { if (id) getSubmission(id).then(s => setSub(s ?? null)); }, [id]);

  if (!sub) return (
    <PhoneShell title="Detail">
      <div className="p-8 text-center text-on-surface-variant">
        <p>Submission not found.</p>
        <Link to="/submissions" className="text-primary text-sm">← Back</Link>
      </div>
    </PhoneShell>
  );

  return (
    <PhoneShell title="Detail">
      <div className="p-4">
        <Link to="/submissions" className="text-sm text-on-surface-variant mb-3 inline-block">← Submissions</Link>
        {sub.photo_blob && (
          <img src={URL.createObjectURL(sub.photo_blob)} alt="evidence" className="w-full h-48 object-cover rounded-xl mb-4" />
        )}
        <div className="bg-card border border-outline-variant rounded-xl p-4 space-y-3 text-sm">
          {[
            ["Status", sub.sync_status],
            ["Category", sub.category ?? "—"],
            ["GPS", `${sub.lat.toFixed(5)}, ${sub.lng.toFixed(5)}`],
            ["Captured", new Date(sub.captured_at).toLocaleString()],
            ["Client ID", sub.client_uuid],
            ["Server ID", sub.server_id ?? "not synced"],
            ["IPFS CID", "pending (INC-011)"],
            ["Note", sub.note ?? "—"],
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
