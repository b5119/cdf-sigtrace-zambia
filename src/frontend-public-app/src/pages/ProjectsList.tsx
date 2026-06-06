// Projects — public index of CDF projects (distinct from the National map).
// Live data from GET /public/projects; falls back to a representative sample when offline.
import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { projectApi, type ProjectSummary } from "../lib/api";
import { projectPath } from "../lib/routes";

type Status = "verified" | "in_progress" | "flagged";
interface Row { id: string; title: string; sector: string; constituency: string; value: string; status: Status; }

// constituency id -> friendly name (the list endpoint returns ids)
const CONST_NAMES: Record<string, string> = {
  "LPV-002": "Milenge", "LSK-001": "Lusaka Central", "LSK-002": "Kafue",
  "CPB-001": "Ndola Central", "CPB-002": "Kitwe Central",
};
const fmtZmw = (n: number | null) => n == null ? "—" : `ZMW ${n.toLocaleString("en-US")}`;
function toRow(p: ProjectSummary): Row {
  return {
    id: p.project_id, title: p.title, sector: p.category,
    constituency: (p.constituency_id && (CONST_NAMES[p.constituency_id] ?? p.constituency_id)) || "—",
    value: fmtZmw(p.disbursement_amount),
    status: p.verified ? "verified" : "in_progress",
  };
}

const SAMPLE: Row[] = [
  { id: "proj-001", title: "District Clinic Modernization", sector: "Healthcare", constituency: "Lusaka Central", value: "ZMW 12,000,000", status: "verified" },
  { id: "proj-002", title: "Primary School Wing Extension", sector: "Education", constituency: "Lusaka Central", value: "ZMW 4,200,000", status: "verified" },
  { id: "proj-003", title: "Community Borehole Programme", sector: "Water", constituency: "Milenge", value: "ZMW 420,000", status: "flagged" },
  { id: "proj-004", title: "Ward Drainage Rehabilitation", sector: "Infrastructure", constituency: "Lusaka Central", value: "ZMW 1,200,000", status: "in_progress" },
  { id: "proj-005", title: "Classroom Block, Kafue", sector: "Education", constituency: "Kafue", value: "ZMW 730,094", status: "verified" },
  { id: "proj-006", title: "Rural Health Post", sector: "Healthcare", constituency: "Chinsali", value: "ZMW 2,450,000", status: "in_progress" },
  { id: "proj-007", title: "Market Shelter Construction", sector: "Infrastructure", constituency: "Ndola Central", value: "ZMW 980,000", status: "verified" },
  { id: "proj-008", title: "Solar Street Lighting", sector: "Energy", constituency: "Kitwe Central", value: "ZMW 2,450,000", status: "in_progress" },
];

function statusPill(s: Status) {
  if (s === "verified") return { label: "Verified", cls: "bg-risk-low/10 text-risk-low", icon: "verified" };
  if (s === "flagged") return { label: "Flagged", cls: "bg-risk-high/10 text-risk-high", icon: "gpp_maybe" };
  return { label: "In progress", cls: "bg-risk-mid/10 text-risk-mid", icon: "pending" };
}

export default function ProjectsList() {
  const { data } = useQuery({
    queryKey: ["projects"],
    queryFn: () => projectApi.list().then(r => r.data.projects),
    retry: 0,
  });
  const rows: Row[] = data && data.length ? data.map(toRow) : SAMPLE;
  const SECTORS = ["All", ...Array.from(new Set(rows.map(p => p.sector)))];

  const [sector, setSector] = useState("All");
  const list = sector === "All" ? rows : rows.filter(p => p.sector === sector);

  return (
    <main className="max-w-[1200px] mx-auto px-6 md:px-12 py-10">
      <div className="flex items-end justify-between mb-6 gap-4 flex-wrap">
        <div>
          <h1 className="disp text-2xl font-bold text-ink">Projects</h1>
          <p className="text-sm text-on-surface-variant mt-1">CDF-funded projects with their verification status. Click one for evidence and the ledger anchor.</p>
        </div>
        <div className="flex gap-2 flex-wrap">
          {SECTORS.map(s => (
            <button key={s} type="button" onClick={() => setSector(s)}
              className={`text-xs font-semibold px-3 py-1.5 rounded-full border transition-colors ${sector === s ? "bg-primary text-white border-primary" : "bg-card border-outline-variant text-on-surface-variant hover:bg-surface-2"}`}>
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {list.map(p => {
          const s = statusPill(p.status);
          return (
            <Link key={p.id} to={projectPath(p.id)}
              className="bg-card border border-outline-variant rounded-xl overflow-hidden hover:border-primary hover:-translate-y-0.5 transition-all block">
              <div className="aspect-video bg-surface-2 flex items-center justify-center relative">
                <span className="material-symbols-outlined text-outline" style={{ fontSize: 40 }}>image</span>
                <span className={`absolute top-2 right-2 text-[11px] font-semibold px-2 py-0.5 rounded-full inline-flex items-center gap-1 ${s.cls}`}>
                  <span className="material-symbols-outlined text-[14px]">{s.icon}</span>{s.label}
                </span>
              </div>
              <div className="p-4">
                <p className="text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold">{p.sector} · {p.constituency}</p>
                <h3 className="disp font-semibold text-ink mt-1 leading-snug">{p.title}</h3>
                <p className="mono text-sm text-primary mt-2">{p.value}</p>
              </div>
            </Link>
          );
        })}
      </div>
    </main>
  );
}
