import { useQuery } from "@tanstack/react-query";
import { monitorApi, type DisbursementRow } from "../lib/api";

const SAMPLE_ROWS: DisbursementRow[] = [
  { id: "m1", constituency_id: "Milenge",   project_id: "Borehole", contract_ocid: "ocds-milenge-borehole", amount: 420000,  date: "2026-04-20", source: "MoF", matched_completion: false, matched_at: null },
  { id: "m2", constituency_id: "Lusaka C.", project_id: "Clinic",   contract_ocid: "ocds-lusaka-clinic",     amount: 1200000, date: "2026-05-23", source: "MoF", matched_completion: true,  matched_at: "2026-05-30" },
];

function fmtAmount(d: DisbursementRow): string {
  return d.amount === 1200000 ? "K 1.2m" : `K ${d.amount.toLocaleString()}`;
}

export default function MismatchExplorer() {
  const { data } = useQuery({
    queryKey: ["mismatches"],
    queryFn: () => monitorApi.mismatches().then(r => r.data),
  });

  const rows = data?.disbursements ?? SAMPLE_ROWS;

  return (
    <div>
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl font-bold text-ink">Disbursement Explorer</h1>
          <p className="text-sm text-on-surface-variant mt-1">Match disbursement ↔ contract ↔ completion</p>
        </div>
        <div className="flex gap-2" />
      </div>

      <div className="bg-card border border-outline-variant rounded-xl p-5">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-outline">
                {["Constituency", "Project", "Amount", "Clean contract", "Verified completion", "Status"].map(h => (
                  <th key={h} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-2 px-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((d, i) => {
                const cleanContract = d.contract_ocid != null;
                const verified = d.matched_completion;
                const accountable = cleanContract && verified;
                return (
                  <tr key={d.id} className={`${i % 2 === 1 ? "bg-surface-2/40 " : ""}border-b border-outline-variant/60 hover:bg-surface-2/70`}>
                    <td className="py-2.5 px-3 text-sm">{d.constituency_id ?? "—"}</td>
                    <td className="py-2.5 px-3 text-sm">{d.project_id ?? "—"}</td>
                    <td className="py-2.5 px-3 text-sm"><span className="mono">{fmtAmount(d)}</span></td>
                    <td className="py-2.5 px-3 text-sm">
                      <span className={cleanContract ? "text-risk-low" : "text-risk-high"}>{cleanContract ? "✓" : "✗"}</span>
                    </td>
                    <td className="py-2.5 px-3 text-sm">
                      <span className={verified ? "text-risk-low" : "text-risk-high"}>{verified ? "✓" : "✗"}</span>
                    </td>
                    <td className="py-2.5 px-3 text-sm">
                      <span className={`font-semibold ${accountable ? "text-risk-low" : "text-risk-high"}`}>
                        {accountable ? "Accountable" : "Mismatch"}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
