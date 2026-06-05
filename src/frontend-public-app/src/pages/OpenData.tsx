// P8 — Open Data. Faithful port of design/screens/P8_open_data.html, downloads wired to the live API.
import { publicApi } from "../lib/api";
import { Link } from "react-router-dom";
import { ROUTES } from "../lib/routes";

const DATASETS = [
  { name: "Constituency summaries", desc: "Allocation, projects, verification status", fmt: "CSV · JSON", updated: "2026-06-01", key: "constituencies" },
  { name: "Procurement risk (aggregate)", desc: "De-identified risk by entity & sector", fmt: "CSV", updated: "2026-06-01", key: "risk-scores" },
  { name: "Verified projects", desc: "Public project + evidence index", fmt: "JSON", updated: "2026-05-30", key: "contracts" },
];

async function download(key: string) {
  const { data } = await publicApi.opendata(key);
  const rows = data.data;
  let blob: Blob, ext: string;
  if (rows.length && key !== "contracts") {
    const keys = Object.keys(rows[0]);
    const csv = [keys.join(","), ...rows.map(r => keys.map(k => JSON.stringify((r as Record<string, unknown>)[k] ?? "")).join(","))].join("\n");
    blob = new Blob([csv], { type: "text/csv" }); ext = "csv";
  } else {
    blob = new Blob([JSON.stringify(rows, null, 2)], { type: "application/json" }); ext = "json";
  }
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `cdf-${key}-${new Date().toISOString().slice(0, 10)}.${ext}`;
  a.click();
}

export default function OpenData() {
  return (
    <main className="max-w-[1200px] mx-auto px-6 md:px-12 py-10">
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="disp text-2xl font-bold text-ink">Open Data</h1>
          <p className="text-sm text-on-surface-variant mt-1">Download the underlying aggregated datasets, or use the public API.</p>
        </div>
      </div>

      <div className="bg-card border border-outline-variant rounded-xl p-5">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead><tr className="border-b border-outline">
              {["Dataset", "Description", "Format", "Updated", "Download"].map(h => (
                <th key={h} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-2 px-3">{h}</th>
              ))}
            </tr></thead>
            <tbody>
              {DATASETS.map((d, i) => (
                <tr key={d.key} className={`${i % 2 ? "bg-surface-2/40" : ""} border-b border-outline-variant/60 hover:bg-surface-2/70`}>
                  <td className="py-2.5 px-3 text-sm">{d.name}</td>
                  <td className="py-2.5 px-3 text-sm">{d.desc}</td>
                  <td className="py-2.5 px-3 text-sm">{d.fmt}</td>
                  <td className="py-2.5 px-3 text-sm">{d.updated}</td>
                  <td className="py-2.5 px-3 text-sm">
                    <button onClick={() => download(d.key)} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent">
                      <span className="material-symbols-outlined">download</span>Download
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="mt-6">
        <div id="api" className="scroll-mt-20 bg-card border border-outline-variant rounded-xl p-5">
          <div className="flex items-center justify-between mb-4"><h3 className="disp font-semibold text-ink">Public API</h3></div>
          <p className="text-sm text-on-surface-variant mb-3">Programmatic access to the public tier. See the API documentation.</p>
          <Link to={ROUTES.ABOUT} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent">
            <span className="material-symbols-outlined">api</span>API documentation
          </Link>
        </div>
      </div>
    </main>
  );
}
