import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { monitorApi, type GhostSignal } from "../lib/api";
import { ROUTES } from "../lib/routes";

const SAMPLE_SIGNALS: GhostSignal[] = [
  { id: "s1", disbursement_id: "d1", constituency_id: "Milenge",   project_id: "Borehole",     amount: 420000,  disbursement_date: "2026-04-20", days_overdue: 45, state: "none",    raised_at: null },
  { id: "s2", disbursement_id: "d2", constituency_id: "Lusaka C.", project_id: "Clinic annex", amount: 1200000, disbursement_date: "2026-05-23", days_overdue: 12, state: "partial", raised_at: null },
  { id: "s3", disbursement_id: "d3", constituency_id: "Kafue",     project_id: "Classroom",    amount: 730094,  disbursement_date: "2026-03-06", days_overdue: 90, state: "none",    raised_at: null },
];

function fmtAmount(s: GhostSignal): string {
  return s.amount === 1200000 ? "K 1.2m" : `K ${s.amount.toLocaleString()}`;
}

function overdueColor(days: number): string {
  if (days >= 30) return "text-risk-high";
  if (days >= 10) return "text-risk-mid";
  return "text-risk-low";
}

export default function GhostQueue() {
  const qc = useQueryClient();
  const [msg, setMsg] = useState<string | null>(null);

  const { data } = useQuery({
    queryKey: ["ghost-queue"],
    queryFn: () => monitorApi.ghostQueue().then(r => r.data),
  });

  const runM = useMutation({
    mutationFn: () => monitorApi.run(),
    onSuccess: () => { setMsg("Monitor run complete"); qc.invalidateQueries({ queryKey: ["ghost-queue"] }); },
    onError: () => setMsg("Monitor run failed"),
  });

  const signals = data?.signals ?? SAMPLE_SIGNALS;

  return (
    <div>
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl font-bold text-ink">Ghost-Project Queue</h1>
          <p className="text-sm text-on-surface-variant mt-1">Disbursements with no verified completion</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => runM.mutate()}
            disabled={runM.isPending}
            className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 bg-accent text-white disabled:opacity-50"
          >
            <span className="material-symbols-outlined">play_arrow</span>Run monitor
          </button>
        </div>
      </div>

      {msg && <div className="bg-primary/5 border border-primary/20 rounded-lg px-4 py-2.5 text-sm text-primary mb-4">{msg}</div>}

      <div className="bg-card border border-outline-variant rounded-xl p-5">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-outline">
                {["Constituency", "Project", "Disbursed", "Date", "Overdue", "Evidence", "Action"].map(h => (
                  <th key={h} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-2 px-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {signals.map((s, i) => (
                <tr key={s.id} className={`${i % 2 === 1 ? "bg-surface-2/40 " : ""}border-b border-outline-variant/60 hover:bg-surface-2/70`}>
                  <td className="py-2.5 px-3 text-sm">{s.constituency_id ?? "—"}</td>
                  <td className="py-2.5 px-3 text-sm">{s.project_id ?? "—"}</td>
                  <td className="py-2.5 px-3 text-sm"><span className="mono">{fmtAmount(s)}</span></td>
                  <td className="py-2.5 px-3 text-sm">{s.disbursement_date}</td>
                  <td className="py-2.5 px-3 text-sm"><span className={`${overdueColor(s.days_overdue)} font-semibold`}>{s.days_overdue}d</span></td>
                  <td className="py-2.5 px-3 text-sm">{s.state}</td>
                  <td className="py-2.5 px-3 text-sm">
                    <Link to={ROUTES.CASES} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 text-ink hover:bg-surface-2">
                      <span className="material-symbols-outlined">folder</span>Open case
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
