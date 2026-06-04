import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { monitorApi } from "../lib/api";

export default function GhostQueue() {
  const qc = useQueryClient();
  const [msg, setMsg] = useState<string | null>(null);

  const { data } = useQuery({
    queryKey: ["ghost-queue"],
    queryFn: () => monitorApi.ghostQueue().then(r => r.data),
  });

  const clearM = useMutation({
    mutationFn: ({ id, justification }: { id: string; justification: string }) => monitorApi.clear(id, justification),
    onSuccess: () => { setMsg("Signal cleared"); qc.invalidateQueries({ queryKey: ["ghost-queue"] }); },
  });

  const signals = data?.signals ?? [];

  return (
    <div>
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl font-bold text-ink">Ghost-Project Queue</h1>
          <p className="text-sm text-on-surface-variant mt-1">Disbursements with no verified completion within the window — {data?.total ?? 0} open signals</p>
        </div>
      </div>

      {msg && <div className="bg-primary/5 border border-primary/20 rounded-lg px-4 py-2.5 text-sm text-primary mb-4">{msg}</div>}

      <div className="bg-card border border-outline-variant rounded-xl overflow-hidden">
        <table className="w-full">
          <thead className="bg-surface-2">
            <tr>{["Constituency", "Project", "Amount", "Disbursed", "Days Overdue", "State", "Action"].map(h => (
              <th key={h} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-3 px-3">{h}</th>
            ))}</tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/60">
            {signals.map(s => (
              <tr key={s.id} className="hover:bg-surface-2/50">
                <td className="py-2.5 px-3 text-sm">{s.constituency_id ?? "—"}</td>
                <td className="py-2.5 px-3 text-sm mono text-xs">{s.project_id ?? "—"}</td>
                <td className="py-2.5 px-3 text-sm mono text-xs">K {s.amount.toLocaleString()}</td>
                <td className="py-2.5 px-3 text-xs text-on-surface-variant">{s.disbursement_date}</td>
                <td className="py-2.5 px-3"><span className="mono text-white text-xs font-semibold px-2 py-0.5 rounded bg-risk-high">{s.days_overdue}d</span></td>
                <td className="py-2.5 px-3"><span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-accent/10 text-accent">{s.state}</span></td>
                <td className="py-2.5 px-3">
                  <button onClick={() => { const j = prompt("Justification to clear:"); if (j) clearM.mutate({ id: s.id, justification: j }); }}
                    className="text-xs font-semibold px-2.5 py-1 rounded border border-outline-variant hover:bg-surface-2">Clear</button>
                </td>
              </tr>
            ))}
            {signals.length === 0 && (
              <tr><td colSpan={7} className="py-8 text-center text-on-surface-variant text-sm">No open ghost signals. Run the monitor to detect.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
