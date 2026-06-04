import { useQuery } from "@tanstack/react-query";
import { ingestionApi } from "../lib/api";

export default function Admin() {
  const { data } = useQuery({
    queryKey: ["ingestion-runs"],
    queryFn: () => ingestionApi.runs({ size: 5 }).then(r => r.data).catch(() => null),
  });
  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-ink mb-1">Admin</h1>
      <p className="text-sm text-on-surface-variant mb-6">System health, ingestion, weights & thresholds (full console at INC-017)</p>
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-card border border-outline-variant rounded-xl p-5">
          <h3 className="font-display font-semibold mb-4">Component Health</h3>
          {[["PostgreSQL","ok"],["Redis","ok"],["Hyperledger Fabric","mock"],["Anomaly Engine","ok"]].map(([c, s]) => (
            <div key={c} className="flex items-center justify-between py-2 border-b border-outline-variant/60 last:border-0">
              <span className="text-sm">{c}</span>
              <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${s === "ok" ? "bg-risk-low/10 text-risk-low" : "bg-risk-mid/10 text-risk-mid"}`}>{s}</span>
            </div>
          ))}
        </div>
        <div className="bg-card border border-outline-variant rounded-xl p-5">
          <h3 className="font-display font-semibold mb-4">Recent Ingestion Runs</h3>
          {data?.runs?.length
            ? data.runs.map((r: any) => (
              <div key={r.id} className="flex items-center justify-between py-2 border-b border-outline-variant/60 last:border-0 text-sm">
                <span className="mono text-xs">{r.source}</span>
                <span className="text-xs">{r.records_loaded} loaded</span>
                <span className={`text-xs ${r.status === "complete" ? "text-risk-low" : "text-on-surface-variant"}`}>{r.status}</span>
              </div>
            ))
            : <p className="text-sm text-on-surface-variant">No ingestion runs yet.</p>}
        </div>
      </div>
    </div>
  );
}
