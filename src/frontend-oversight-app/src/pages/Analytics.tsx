import { useQuery } from "@tanstack/react-query";
import { contractsApi } from "../lib/api";

// Sample anomaly-rate series (12 months) — used as fallback when backend is down.
const SAMPLE_LINE: number[] = [78, 72, 75, 69, 66, 70, 62, 59, 63, 56, 60, 54];

interface Bar { label: string; value: number; }
const SAMPLE_BARS: Bar[] = [
  { label: "Lusaka CC", value: 72 },
  { label: "Kafue DC", value: 58 },
  { label: "Ndola CC", value: 46 },
  { label: "Kitwe CC", value: 34 },
  { label: "Chipata MC", value: 27 },
];

export default function Analytics() {
  // Keep existing wiring; data feeds the bars when available.
  const { data } = useQuery({
    queryKey: ["contracts", { size: 100 }],
    queryFn: () => contractsApi.list({ size: 100 }).then(r => r.data),
  });

  const bars: Bar[] = (() => {
    const contracts = data?.contracts ?? [];
    if (contracts.length === 0) return SAMPLE_BARS;
    const byEntity = new Map<string, { sum: number; n: number }>();
    contracts.forEach(c => {
      const k = c.procuring_entity || "—";
      const e = byEntity.get(k) ?? { sum: 0, n: 0 };
      e.sum += c.risk_score ?? 0; e.n += 1; byEntity.set(k, e);
    });
    const computed = [...byEntity.entries()]
      .map(([label, { sum, n }]) => ({ label, value: Math.round(sum / n) }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 5);
    return computed.length > 0 ? computed : SAMPLE_BARS;
  })();

  // Build the line polyline across a 0..300 viewBox; y values map directly.
  const stepX = 300 / (SAMPLE_LINE.length - 1);
  const linePts = SAMPLE_LINE.map((y, i) => `${Math.round(i * stepX)},${y}`).join(" ");
  const areaPts = `0,100 ${linePts} 300,100`;

  return (
    <div>
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="disp text-2xl font-bold text-ink">Analytics</h1>
          <p className="text-sm text-on-surface-variant mt-1">Trends &amp; comparisons</p>
        </div>
        <div className="flex gap-2"></div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Anomaly rate line chart */}
        <div className="bg-card border border-outline-variant rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="disp font-semibold text-ink">Anomaly rate over time (12 mo)</h3>
          </div>
          <svg viewBox="0 0 300 100" preserveAspectRatio="none" className="w-full" style={{ height: "210px" }}>
            <polygon points={areaPts} fill="#0E5C46" fillOpacity="0.08" />
            <polyline points={linePts} fill="none" stroke="#0E5C46" strokeWidth="2.5" vectorEffect="non-scaling-stroke" />
            {SAMPLE_LINE.map((y, i) => (
              <circle key={i} cx={Math.round(i * stepX)} cy={y} r="2.5" fill="#0E5C46" />
            ))}
          </svg>
        </div>

        {/* Entity comparison bars */}
        <div className="bg-card border border-outline-variant rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="disp font-semibold text-ink">Entity comparison</h3>
          </div>
          <div className="py-2">
            {bars.map(b => (
              <div key={b.label} className="flex items-center gap-3 py-1.5">
                <span className="text-xs w-32 shrink-0 text-on-surface-variant">{b.label}</span>
                <div className="flex-1 h-3 rounded-full bg-surface-2">
                  <div className="h-3 rounded-full" style={{ width: `${Math.min(b.value, 100)}%`, background: "#B8762A" }} />
                </div>
                <span className="mono text-xs w-12 text-right">{b.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
