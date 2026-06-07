// Public API documentation — its own page (distinct from Open Data datasets).
import { Link } from "react-router-dom";
import { ROUTES } from "../lib/routes";

const BASE = (import.meta.env.VITE_API_BASE_URL as string) ?? "http://localhost:8000/api/v1";

const ENDPOINTS: { method: string; path: string; desc: string }[] = [
  { method: "GET", path: "/public/overview", desc: "National KPIs — allocation, projects, verified, flags." },
  { method: "GET", path: "/public/map", desc: "Constituency risk choropleth features." },
  { method: "GET", path: "/public/constituencies", desc: "List of constituencies with counts + aggregate risk." },
  { method: "GET", path: "/public/constituencies/{id}", desc: "A single constituency's allocation and projects." },
  { method: "GET", path: "/public/projects", desc: "Project index with verification status." },
  { method: "GET", path: "/public/projects/{id}", desc: "A project's disbursement, evidence and verified location." },
  { method: "GET", path: "/public/risk/aggregate", desc: "De-identified procurement risk by entity & sector." },
  { method: "GET", path: "/public/opendata/{dataset}", desc: "Downloadable aggregated datasets (CSV/JSON)." },
  { method: "POST", path: "/public/verify-contract", desc: "Verify an uploaded contract against its ledger anchor." },
  { method: "GET", path: "/public/anchors/{ocid}", desc: "Latest anchored hash + tx for a contract (no named data)." },
];

const mColor = (m: string) => m === "GET" ? "bg-primary/10 text-primary" : "bg-accent/10 text-accent";

export default function ApiDocs() {
  return (
    <main className="max-w-[1000px] mx-auto px-6 md:px-12 py-10">
      <h1 className="disp text-2xl font-bold text-ink">Public API</h1>
      <p className="text-sm text-on-surface-variant mt-1 max-w-2xl">Programmatic, read-only access to the public tier. All responses are de-identified — no supplier or official names. No authentication required.</p>

      <div className="bg-ink text-white rounded-xl p-4 mt-6 flex items-center justify-between gap-4 flex-wrap">
        <div>
          <p className="text-[11px] uppercase tracking-wider text-white/50 font-semibold">Base URL</p>
          <p className="mono text-sm">{BASE}</p>
        </div>
        <a href={`${BASE.replace(/\/api\/v1$/, "")}/docs`} target="_blank" rel="noreferrer"
          className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 bg-accent text-white">
          <span className="material-symbols-outlined">open_in_new</span>Interactive docs (Swagger)
        </a>
      </div>

      <div className="bg-card border border-outline-variant rounded-xl overflow-hidden mt-6">
        <table className="w-full">
          <thead><tr className="border-b border-outline">
            {["Method", "Endpoint", "Description"].map(h => (
              <th key={h} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-3 px-4">{h}</th>
            ))}
          </tr></thead>
          <tbody>
            {ENDPOINTS.map((e, i) => (
              <tr key={e.path} className={`${i % 2 ? "bg-surface-2/40" : ""} border-b border-outline-variant/60`}>
                <td className="py-3 px-4"><span className={`mono text-[11px] font-semibold px-2 py-0.5 rounded ${mColor(e.method)}`}>{e.method}</span></td>
                <td className="py-3 px-4 mono text-sm text-ink">{e.path}</td>
                <td className="py-3 px-4 text-sm text-on-surface-variant">{e.desc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="bg-card border border-outline-variant rounded-xl p-5 mt-6">
        <h3 className="disp font-semibold text-ink mb-2">Example</h3>
        <pre className="mono text-xs bg-ink text-[#8fd5b8] rounded-lg p-3 overflow-x-auto">curl {BASE}/public/overview</pre>
      </div>

      <div className="mt-6">
        <Link to={ROUTES.OPEN_DATA} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent">
          <span className="material-symbols-outlined">download</span>Or download the datasets
        </Link>
      </div>
    </main>
  );
}
