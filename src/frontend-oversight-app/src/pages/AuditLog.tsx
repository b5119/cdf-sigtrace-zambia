const EVENTS = [
  { actor: "officer@oag.gov.zm", action: "VIEW_CONTRACT", target: "ocds-zm-zppa-001", time: "2026-06-04 09:12" },
  { actor: "officer@oag.gov.zm", action: "ESCALATE_CASE", target: "case-001", time: "2026-06-04 09:30" },
  { actor: "analyst@acc.gov.zm", action: "EXPORT_REPORT", target: "high-risk.csv", time: "2026-06-04 10:05" },
  { actor: "admin@zppa.org.zm", action: "RUN_ANALYSIS", target: "all-contracts", time: "2026-06-04 11:00" },
];
export default function AuditLog() {
  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-ink mb-1">Audit Log</h1>
      <p className="text-sm text-on-surface-variant mb-6">Append-only record of every privileged action · periodically anchored to Fabric</p>
      <div className="bg-card border border-outline-variant rounded-xl overflow-hidden">
        <table className="w-full">
          <thead className="bg-surface-2">
            <tr>{["Actor", "Action", "Target", "Timestamp"].map(h => (
              <th key={h} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-3 px-4">{h}</th>
            ))}</tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/60">
            {EVENTS.map((e, i) => (
              <tr key={i} className="hover:bg-surface-2/50">
                <td className="py-3 px-4 text-sm">{e.actor}</td>
                <td className="py-3 px-4 text-sm"><span className="mono text-xs bg-surface-2 px-2 py-0.5 rounded">{e.action}</span></td>
                <td className="py-3 px-4 text-sm mono text-xs">{e.target}</td>
                <td className="py-3 px-4 text-sm text-on-surface-variant">{e.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
