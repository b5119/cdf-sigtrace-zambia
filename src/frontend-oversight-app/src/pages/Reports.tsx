import { useState } from "react";

interface HistoryRow { report: string; date: string; format: string; }

// Sample history — renders fully when no backend is wired.
const HISTORY: HistoryRow[] = [
  { report: "High-risk Q2", date: "2026-06-01", format: "PDF" },
];

export default function Reports() {
  const [scope, setScope] = useState("");
  const [range, setRange] = useState("");
  const [format, setFormat] = useState("");

  return (
    <div>
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="disp text-2xl font-bold text-ink">Reports &amp; Exports</h1>
          <p className="text-sm text-on-surface-variant mt-1">Generate restricted reports (audit-logged)</p>
        </div>
        <div className="flex gap-2"></div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* New report */}
        <div>
          <div className="bg-card border border-outline-variant rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="disp font-semibold text-ink">New report</h3>
            </div>

            <label className="block mb-3">
              <span className="block text-xs font-semibold text-on-surface-variant mb-1">Scope</span>
              <input
                type="text"
                placeholder="High-risk contracts"
                value={scope}
                onChange={e => setScope(e.target.value)}
                className="w-full rounded-lg border border-outline-variant bg-card px-3 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary"
              />
            </label>

            <label className="block mb-3">
              <span className="block text-xs font-semibold text-on-surface-variant mb-1">Date range</span>
              <input
                type="text"
                placeholder="2026-01-01 → 2026-06-01"
                value={range}
                onChange={e => setRange(e.target.value)}
                className="w-full rounded-lg border border-outline-variant bg-card px-3 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary"
              />
            </label>

            <label className="block mb-3">
              <span className="block text-xs font-semibold text-on-surface-variant mb-1">Format</span>
              <input
                type="text"
                placeholder="PDF"
                value={format}
                onChange={e => setFormat(e.target.value)}
                className="w-full rounded-lg border border-outline-variant bg-card px-3 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary"
              />
            </label>

            <button className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 bg-primary text-white">
              <span className="material-symbols-outlined">summarize</span>Generate
            </button>
          </div>
        </div>

        {/* History */}
        <div>
          <div className="bg-card border border-outline-variant rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="disp font-semibold text-ink">History</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-outline">
                    {["Report", "Date", "Format", ""].map((h, i) => (
                      <th key={i} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-2 px-3">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {HISTORY.map((r, i) => (
                    <tr key={i} className="border-b border-outline-variant/60 hover:bg-surface-2/70">
                      <td className="py-2.5 px-3 text-sm">{r.report}</td>
                      <td className="py-2.5 px-3 text-sm">{r.date}</td>
                      <td className="py-2.5 px-3 text-sm">{r.format}</td>
                      <td className="py-2.5 px-3 text-sm">
                        <button className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 text-ink hover:bg-surface-2">
                          <span className="material-symbols-outlined">download</span>Download
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
