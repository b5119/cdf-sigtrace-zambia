import { useQuery } from "@tanstack/react-query";
import { contractsApi } from "../lib/api";

export default function Analytics() {
  const { data } = useQuery({
    queryKey: ["contracts", { size: 100 }],
    queryFn: () => contractsApi.list({ size: 100 }).then(r => r.data),
  });
  const contracts = data?.contracts ?? [];
  const buckets = { low: 0, mid: 0, high: 0 };
  contracts.forEach(c => {
    const s = c.risk_score ?? 0;
    if (s >= 70) buckets.high++; else if (s >= 40) buckets.mid++; else buckets.low++;
  });
  const max = Math.max(buckets.low, buckets.mid, buckets.high, 1);

  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-ink mb-1">Analytics</h1>
      <p className="text-sm text-on-surface-variant mb-6">Anomaly-rate trends and risk distribution</p>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-card border border-outline-variant rounded-xl p-5">
          <h3 className="font-display font-semibold text-ink mb-4">Risk distribution</h3>
          <div className="space-y-3">
            {[["Low (0-39)", buckets.low, "#138636"], ["Medium (40-69)", buckets.mid, "#B45309"], ["High (70+)", buckets.high, "#B91C1C"]].map(([label, val, color]) => (
              <div key={label as string} className="flex items-center gap-3">
                <span className="text-xs w-28 text-on-surface-variant">{label}</span>
                <div className="flex-1 h-4 rounded-full bg-surface-2">
                  <div className="h-4 rounded-full" style={{ width: `${((val as number) / max) * 100}%`, background: color as string }} />
                </div>
                <span className="mono text-xs w-8 text-right">{val as number}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-card border border-outline-variant rounded-xl p-5">
          <h3 className="font-display font-semibold text-ink mb-4">Summary</h3>
          <dl className="space-y-3 text-sm">
            <div className="flex justify-between"><dt className="text-on-surface-variant">Total contracts</dt><dd className="mono font-semibold">{data?.total ?? 0}</dd></div>
            <div className="flex justify-between"><dt className="text-on-surface-variant">Scored</dt><dd className="mono font-semibold">{contracts.length}</dd></div>
            <div className="flex justify-between"><dt className="text-on-surface-variant">High-risk rate</dt><dd className="mono font-semibold text-risk-high">{contracts.length ? Math.round((buckets.high / contracts.length) * 100) : 0}%</dd></div>
          </dl>
        </div>
      </div>
    </div>
  );
}
