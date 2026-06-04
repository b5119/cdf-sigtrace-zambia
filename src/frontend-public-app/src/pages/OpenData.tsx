// P8 — Open Data (matches design/screens/P8_open_data.html)
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { publicApi } from "../lib/api";

const DATASETS = [
  { id: "contracts",      label: "Contracts",      icon: "description", desc: "De-identified contract records with risk scores" },
  { id: "risk-scores",    label: "Risk Scores",    icon: "analytics",   desc: "Weighted anomaly scores per contract (0–100)" },
  { id: "constituencies", label: "Constituencies", icon: "location_city", desc: "Constituency summary: projects, verification rate, allocation" },
];

export default function OpenData() {
  const [active, setActive] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["opendata", active],
    queryFn: () => publicApi.opendata(active!).then(r => r.data),
    enabled: !!active,
    staleTime: 300_000,
  });

  function downloadJson() {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data.data, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `cdf-integrity-${data.dataset}-${new Date().toISOString().slice(0,10)}.json`;
    a.click();
  }

  function downloadCsv() {
    if (!data?.data?.length) return;
    const keys = Object.keys(data.data[0]);
    const csv = [keys.join(","), ...data.data.map((r: Record<string,unknown>) =>
      keys.map(k => JSON.stringify(r[k] ?? "")).join(",")
    )].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `cdf-integrity-${data.dataset}-${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold">Open Data</h1>
        <p className="text-on-surface-variant mt-1">
          Download de-identified datasets. All exports are aggregate only — no supplier or entity names.
        </p>
      </div>

      {/* Dataset cards */}
      <div className="grid md:grid-cols-3 gap-4 mb-8">
        {DATASETS.map(d => (
          <button key={d.id} onClick={() => setActive(d.id)}
            className={`text-left bg-card border rounded-xl p-5 transition-all ${
              active === d.id
                ? "border-primary ring-1 ring-primary/30"
                : "border-outline-variant hover:border-primary/40"
            }`}>
            <span className={`material-symbols-outlined text-2xl mb-2 block ${active === d.id ? "text-primary" : "text-on-surface-variant"}`}>
              {d.icon}
            </span>
            <p className="font-semibold text-sm">{d.label}</p>
            <p className="text-xs text-on-surface-variant mt-1">{d.desc}</p>
          </button>
        ))}
      </div>

      {/* Preview + download */}
      {active && (
        <div className="bg-card border border-outline-variant rounded-2xl overflow-hidden">
          <div className="px-6 py-4 border-b border-outline-variant flex items-center justify-between">
            <div>
              <h2 className="font-display font-semibold">{DATASETS.find(d => d.id === active)?.label}</h2>
              {data && <p className="text-xs text-on-surface-variant mt-0.5">{data.record_count} records · {data.note}</p>}
            </div>
            <div className="flex gap-2">
              <button onClick={downloadJson} disabled={!data}
                className="flex items-center gap-1 px-3 py-1.5 text-sm border border-outline-variant rounded hover:bg-surface-2 disabled:opacity-50 transition-colors">
                <span className="material-symbols-outlined text-base">download</span>JSON
              </button>
              <button onClick={downloadCsv} disabled={!data}
                className="flex items-center gap-1 px-3 py-1.5 text-sm bg-primary text-white rounded hover:bg-primary-h disabled:opacity-50 transition-colors">
                <span className="material-symbols-outlined text-base">table_view</span>CSV
              </button>
            </div>
          </div>
          <div className="overflow-x-auto max-h-96">
            {isLoading
              ? <div className="p-6 space-y-2">{[1,2,3].map(i => <div key={i} className="h-8 bg-surface-2 rounded animate-pulse" />)}</div>
              : data?.data?.length
                ? (
                  <table className="w-full text-xs">
                    <thead className="bg-surface-2 sticky top-0">
                      <tr>{Object.keys(data.data[0]).map(k => (
                        <th key={k} className="px-4 py-2 text-left font-semibold text-on-surface-variant uppercase tracking-wide whitespace-nowrap">{k}</th>
                      ))}</tr>
                    </thead>
                    <tbody className="divide-y divide-outline-variant">
                      {data.data.slice(0, 50).map((row, i) => (
                        <tr key={i} className="hover:bg-surface-2/50">
                          {Object.values(row).map((v, j) => (
                            <td key={j} className="px-4 py-2 mono whitespace-nowrap">{String(v ?? "—")}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )
                : <p className="p-6 text-on-surface-variant text-sm">No data available.</p>
            }
          </div>
        </div>
      )}

      {!active && (
        <div className="text-center py-16 text-on-surface-variant">
          <span className="material-symbols-outlined text-5xl mb-3 block">cloud_download</span>
          <p className="font-semibold">Select a dataset above to preview and download</p>
        </div>
      )}
    </div>
  );
}
