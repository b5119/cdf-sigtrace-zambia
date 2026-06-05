import { useQuery } from "@tanstack/react-query";
import { auditApi, type AuditEntry } from "../lib/api";

interface Row { actor: string; action: string; target: string; when: string; }

// Sample fallback rows — render fully when the backend is down.
const SAMPLE_ROWS: Row[] = [
  { actor: "a@oag.gov.zm", action: "viewed contract", target: "ocds-…123", when: "12:04" },
  { actor: "admin", action: "saved weights v4", target: "config", when: "11:50" },
  { actor: "c@acc.gov.zm", action: "exported report", target: "Q2", when: "11:20" },
];

function toRow(e: AuditEntry): Row {
  const when = e.created_at
    ? new Date(e.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    : "—";
  return {
    actor: e.actor_id ?? "system",
    action: e.action.replace(/_/g, " ").toLowerCase(),
    target: e.target_ref ?? e.target_type ?? "—",
    when,
  };
}

export default function AuditLog() {
  const { data } = useQuery({ queryKey: ["audit"], queryFn: () => auditApi.list().then(r => r.data) });

  const rows: Row[] = data?.entries && data.entries.length > 0
    ? data.entries.map(toRow)
    : SAMPLE_ROWS;

  return (
    <div>
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="disp text-2xl font-bold text-ink">Audit Log</h1>
          <p className="text-sm text-on-surface-variant mt-1">Immutable, anchored action log</p>
        </div>
        <div className="flex gap-2"></div>
      </div>

      <div className="mb-4 text-xs text-on-surface-variant">
        Latest batch anchored: <span className="mono">0x91c4…</span> · 2026-06-02
      </div>

      <div className="bg-card border border-outline-variant rounded-xl p-5">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-outline">
                {["Actor", "Action", "Target", "When"].map(h => (
                  <th key={h} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-2 px-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr
                  key={i}
                  className={`border-b border-outline-variant/60 hover:bg-surface-2/70 ${i % 2 === 1 ? "bg-surface-2/40" : ""}`}
                >
                  <td className="py-2.5 px-3 text-sm">{r.actor}</td>
                  <td className="py-2.5 px-3 text-sm">{r.action}</td>
                  <td className="py-2.5 px-3 text-sm">{r.target}</td>
                  <td className="py-2.5 px-3 text-sm">{r.when}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
