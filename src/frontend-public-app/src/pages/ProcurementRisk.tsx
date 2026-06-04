// P7 — Procurement Risk Overview. Faithful port of design/screens/P7_procurement_risk.html.
// De-identified: entities are "Entity A…E" only.
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { publicApi } from "../lib/api";
import { ROUTES } from "../lib/routes";

function Bar({ label, value, suffix, color, width }: { label: string; value: string; suffix?: string; color: string; width: number }) {
  return (
    <div className="flex items-center gap-3 py-1.5">
      <span className="text-xs w-32 shrink-0 text-on-surface-variant">{label}</span>
      <div className="flex-1 h-3 rounded-full bg-surface-2"><div className="h-3 rounded-full" style={{ width: `${width}%`, background: color }} /></div>
      <span className="mono text-xs w-12 text-right">{value}{suffix}</span>
    </div>
  );
}

const SECTORS = [
  { label: "Works", v: 62, c: "#B91C1C" }, { label: "Consultancy", v: 41, c: "#B45309" },
  { label: "Goods", v: 24, c: "#138636" }, { label: "Services", v: 18, c: "#138636" },
];

export default function ProcurementRisk() {
  const { data } = useQuery({ queryKey: ["risk-aggregate"], queryFn: () => publicApi.riskAggregate().then(r => r.data), staleTime: 300_000 });
  const entities = data?.entities ?? [];
  const maxScore = Math.max(...entities.map(e => e.avg_risk_score ?? 0), 1);

  return (
    <main className="max-w-[1200px] mx-auto px-6 md:px-12 py-10">
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="disp text-2xl font-bold text-ink">Procurement Risk Overview</h1>
          <p className="text-sm text-on-surface-variant mt-1">Aggregated, de-identified integrity signals — not determinations of wrongdoing.</p>
        </div>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-card border border-outline-variant rounded-xl p-4 h-full">
          <p className="text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold">Contracts analysed</p>
          <p className="disp text-2xl font-bold text-ink mt-1">12,480</p></div>
        <div className="bg-card border border-outline-variant rounded-xl p-4 h-full">
          <p className="text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold">Flagged rate</p>
          <p className="disp text-2xl font-bold text-accent mt-1">8.2%</p></div>
        <div className="bg-card border border-outline-variant rounded-xl p-4 h-full">
          <p className="text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold">Average risk</p>
          <p className="disp text-2xl font-bold text-risk-low mt-1">31 / 100</p></div>
      </div>

      {/* Two bar panels */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-card border border-outline-variant rounded-xl p-5">
          <div className="flex items-center justify-between mb-4"><h3 className="disp font-semibold text-ink">Anomaly rate by sector</h3></div>
          <div className="py-2">
            {SECTORS.map(s => <Bar key={s.label} label={s.label} value={String(s.v)} suffix="%" color={s.c} width={s.v} />)}
          </div>
        </div>
        <div className="bg-card border border-outline-variant rounded-xl p-5">
          <div className="flex items-center justify-between mb-4"><h3 className="disp font-semibold text-ink">Risk by procuring entity</h3></div>
          <div className="py-2">
            {entities.length > 0
              ? entities.map(e => <Bar key={e.entity_label} label={e.entity_label} value={(e.avg_risk_score ?? 0).toFixed(0)} color="#B8762A" width={((e.avg_risk_score ?? 0) / maxScore) * 100} />)
              : [["Entity A",78],["Entity B",64],["Entity C",47],["Entity D",33],["Entity E",21]].map(([l,v]) => <Bar key={l as string} label={l as string} value={String(v)} color="#B8762A" width={v as number} />)}
          </div>
        </div>
      </div>

      <div className="mt-6">
        <div className="bg-card border border-outline-variant rounded-xl p-5">
          <div className="flex items-center justify-between mb-4"><h3 className="disp font-semibold text-ink">Methodology</h3></div>
          <p className="text-sm text-on-surface-variant mb-3">How these signals are computed is explained in the public methodology.</p>
          <Link to={ROUTES.ABOUT} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent">
            <span className="material-symbols-outlined">menu_book</span>Read the methodology
          </Link>
        </div>
      </div>
    </main>
  );
}
