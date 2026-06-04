import { useQuery } from "@tanstack/react-query";
import { monitorApi } from "../lib/api";

export default function MismatchExplorer() {
  const { data } = useQuery({
    queryKey: ["disbursements"],
    queryFn: () => monitorApi.disbursements().then(r => r.data),
  });
  const rows = data?.disbursements ?? [];
  const matched = rows.filter(d => d.matched_completion).length;

  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-ink mb-1">Disbursement / Mismatch Explorer</h1>
      <p className="text-sm text-on-surface-variant mb-6">{rows.length} disbursements · {matched} matched to verified completion · {rows.length - matched} unmatched</p>

      <div className="bg-card border border-outline-variant rounded-xl overflow-hidden">
        <table className="w-full">
          <thead className="bg-surface-2">
            <tr>{["Constituency", "Project", "Contract", "Amount", "Date", "Source", "Match Status"].map(h => (
              <th key={h} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-3 px-3">{h}</th>
            ))}</tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/60">
            {rows.map(d => (
              <tr key={d.id} className="hover:bg-surface-2/50">
                <td className="py-2.5 px-3 text-sm">{d.constituency_id ?? "—"}</td>
                <td className="py-2.5 px-3 mono text-xs">{d.project_id ?? "—"}</td>
                <td className="py-2.5 px-3 mono text-xs text-primary">{d.contract_ocid ?? "—"}</td>
                <td className="py-2.5 px-3 mono text-xs">K {d.amount.toLocaleString()}</td>
                <td className="py-2.5 px-3 text-xs text-on-surface-variant">{d.date}</td>
                <td className="py-2.5 px-3 text-xs">{d.source}</td>
                <td className="py-2.5 px-3">
                  {d.matched_completion
                    ? <span className="inline-flex items-center gap-1 text-xs font-semibold text-risk-low"><span className="material-symbols-outlined text-sm">check_circle</span>Matched</span>
                    : <span className="inline-flex items-center gap-1 text-xs font-semibold text-risk-high"><span className="material-symbols-outlined text-sm">error</span>No completion</span>}
                </td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr><td colSpan={7} className="py-8 text-center text-on-surface-variant text-sm">No disbursements loaded.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
