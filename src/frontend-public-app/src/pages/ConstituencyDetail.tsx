// P4 — Constituency Detail (matches stitch_export/constituency_detail)
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { publicApi, type ConstituencyDetail as ConstituencyDTO } from "../lib/api";
import { ROUTES, projectPath } from "../lib/routes";
import ZambiaMap from "../components/ui/ZambiaMap";

function fmtZmw(n: number | null | undefined) {
  if (n == null) return "—";
  return `ZMW ${n.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
}

// Representative sample projects — generic, no real names. Real data arrives via INC-010/014.
// IDs mirror the backend pulse project ids so the public project page (P5) resolves.
const SAMPLE_PROJECTS = [
  {
    id: "proj-001",
    sector: "Education Sector",
    title: "Primary School Wing Extension",
    statusLabel: "85% COMPLETE",
    statusStyle: "bg-primary/10 text-primary",
    value: "ZMW 4,200,000",
    ref: "CDF-2026-ED-012",
    verified: true,
    cta: "View Details",
    ctaIcon: "arrow_forward",
    placeholderIcon: "image",
  },
  {
    id: "proj-002",
    sector: "Healthcare Sector",
    title: "District Clinic Modernization",
    statusLabel: "IN PROGRESS",
    statusStyle: "bg-primary/10 text-primary",
    value: "ZMW 7,850,000",
    ref: "CDF-2026-HC-045",
    verified: true,
    cta: "View Details",
    ctaIcon: "arrow_forward",
    placeholderIcon: "image",
  },
  {
    id: "proj-003",
    sector: "Infrastructure Sector",
    title: "Ward Drainage Rehabilitation",
    statusLabel: "UNDER REVIEW",
    statusStyle: "bg-accent/10 text-accent",
    value: "ZMW 1,200,000",
    ref: "CDF-2026-IN-009",
    verified: false,
    cta: "View Details",
    ctaIcon: "arrow_forward",
    placeholderIcon: "image",
  },
  {
    id: "proj-004",
    sector: "Public Safety",
    title: "Constituency Solar Street Lighting",
    statusLabel: "PLANNING",
    statusStyle: "bg-surface-2 text-on-surface-variant",
    value: "ZMW 2,450,000",
    ref: "CDF-2026-PS-022",
    verified: false,
    cta: "View RFP",
    ctaIcon: "open_in_new",
    placeholderIcon: "add_circle",
  },
];

const SECTORS = [
  { label: "Education", pct: 45 },
  { label: "Healthcare", pct: 30 },
  { label: "Public Safety", pct: 15 },
  { label: "Infrastructure", pct: 10 },
];

// caps label style — prototype's font-label-caps (the app's tailwind config has no such token)
const CAPS = "font-semibold tracking-[0.05em] uppercase";

const SAMPLE_CONSTITUENCY: ConstituencyDTO = {
  id: "LSK-001", name: "Lusaka Central", province: "Lusaka",
  project_count: 24, verified_count: 18, risk_aggregate: "medium",
  cdf_allocation: 28_300_000,
  geo: { type: "Point", coordinates: [28.3245, -15.4241] },
};

export default function ConstituencyDetail() {
  const { id } = useParams<{ id: string }>();

  const { data: apiData } = useQuery({
    queryKey: ["constituency", id],
    queryFn: () => publicApi.constituency(id!).then(r => r.data),
    enabled: !!id,
    retry: 0,
  });
  // Always render the design; fall back to a representative sample when the API is unavailable.
  const data: ConstituencyDTO = apiData ?? SAMPLE_CONSTITUENCY;

  const verifRate = data.project_count
    ? Math.round((data.verified_count / data.project_count) * 100)
    : null;

  const coords = data.geo?.coordinates
    ? `${data.geo.coordinates[1].toFixed(2)}, ${data.geo.coordinates[0].toFixed(2)}`
    : "-15.41, 28.30";

  return (
    <main className="px-4 md:px-12 py-8">
      {/* Breadcrumbs */}
      <nav className="flex items-center gap-2 mb-4 text-on-surface-variant">
        <Link to={ROUTES.MAP} className="hover:text-primary transition-colors flex items-center gap-1">
          <span className="material-symbols-outlined text-[18px]">home</span>
          <span className={`${CAPS} text-[11px]`}>National Map</span>
        </Link>
        <span className="material-symbols-outlined text-[14px]">chevron_right</span>
        <span className={`${CAPS} text-[11px] text-primary`}>{data.name}</span>
      </nav>

      {/* Constituency Header */}
      <section className="bg-card rounded-xl border border-outline-variant p-8 mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className={`bg-accent/10 text-accent px-2 py-0.5 rounded ${CAPS} text-[10px]`}>
              PROVINCE: {data.province}
            </span>
            <span className={`bg-primary/10 text-primary px-2 py-0.5 rounded ${CAPS} text-[10px]`}>
              ID: {data.id}
            </span>
          </div>
          <h1 className="font-display text-2xl md:text-[32px] md:leading-[40px] font-bold text-on-surface mb-2">
            {data.name} Constituency
          </h1>
          <p className="text-on-surface-variant max-w-2xl">
            A vital economic and administrative hub, currently overseeing {data.project_count} project{data.project_count === 1 ? "" : "s"} funded
            through the National Constituency Development Fund (CDF).
          </p>
        </div>
        <div className="flex flex-col items-start md:items-end gap-2">
          <div className="md:text-right">
            <p className={`${CAPS} text-[12px] text-on-surface-variant mb-1`}>TOTAL CDF ALLOCATION (2026)</p>
            <p className="font-mono text-[24px] font-bold text-primary">{fmtZmw(data.cdf_allocation)}</p>
          </div>
          <div className="flex items-center gap-4 mt-2">
            <div className="flex flex-col items-center justify-center p-3 rounded-full bg-surface-2 border border-accent w-24 h-24 shrink-0">
              <span className="material-symbols-outlined text-accent" style={{ fontVariationSettings: "'FILL' 1" }}>verified</span>
              <span className="text-[8px] font-bold text-center leading-tight mt-1">VERIFIED ON LEDGER</span>
            </div>
            <div className="text-right">
              <span className={`bg-primary text-white px-3 py-1 rounded-full ${CAPS} text-[10px] inline-block mb-1`}>
                {verifRate != null ? `${verifRate}% VERIFIED` : "VERIFIED"}
              </span>
              <p className="font-mono text-[10px] text-on-surface-variant">
                {data.verified_count}/{data.project_count} VERIFIED
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Content Grid: Map & Projects */}
      <div className="grid grid-cols-12 gap-6">
        {/* Left Column: Metrics & Map */}
        <div className="col-span-12 xl:col-span-4 space-y-6">
          {/* Locator Map Card */}
          <div className="bg-card rounded-xl border border-outline-variant overflow-hidden shadow-sm">
            <div className="p-4 border-b border-outline-variant flex justify-between items-center">
              <h3 className="font-display text-[24px] font-medium">Geographic Scope</h3>
              <span className="material-symbols-outlined text-on-surface-variant">map</span>
            </div>
            <div className="relative">
              <ZambiaMap height="aspect-square" locator={{ x: 560, y: 592, label: data.name, gps: coords }} />
            </div>
            <div className="p-4 bg-surface-2">
              <div className="flex items-center justify-between mb-2">
                <span className={`${CAPS} text-[11px] text-on-surface-variant`}>TOTAL PROJECTS</span>
                <span className="font-mono text-[13px]">{data.project_count}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className={`${CAPS} text-[11px] text-on-surface-variant`}>VERIFIED PROJECTS</span>
                <span className="font-mono text-[13px]">{data.verified_count}</span>
              </div>
            </div>
          </div>

          {/* Sector Distribution */}
          <div className="bg-card rounded-xl border border-outline-variant p-4 shadow-sm">
            <h3 className="font-display text-[24px] font-medium mb-4">Allocation by Sector</h3>
            <div className="space-y-4">
              {SECTORS.map(s => (
                <div key={s.label}>
                  <div className={`flex justify-between ${CAPS} text-[11px] mb-1`}>
                    <span>{s.label}</span>
                    <span>{s.pct}%</span>
                  </div>
                  <div className="w-full h-2 bg-surface-2 rounded-full overflow-hidden">
                    <div className="bg-primary h-full" style={{ width: `${s.pct}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Project Grid */}
        <div className="col-span-12 xl:col-span-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display text-[24px] font-medium">Active Ledger Projects</h2>
            <div className="flex gap-2">
              <button className="bg-card border border-outline-variant p-2 rounded-lg flex items-center">
                <span className="material-symbols-outlined text-[20px]">filter_list</span>
              </button>
              <button className="bg-card border border-outline-variant p-2 rounded-lg flex items-center">
                <span className="material-symbols-outlined text-[20px]">sort</span>
              </button>
            </div>
          </div>

          <p className={`${CAPS} text-[10px] text-on-surface-variant mb-4`}>
            De-identified public view — representative sample
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {SAMPLE_PROJECTS.map(p => (
              <Link
                key={p.id}
                to={projectPath(p.id)}
                className="bg-card rounded-xl border border-outline-variant overflow-hidden group hover:border-primary hover:-translate-y-0.5 transition-all block"
              >
                <div className="aspect-video relative overflow-hidden bg-surface-2 flex items-center justify-center">
                  <span className="material-symbols-outlined text-outline" style={{ fontSize: "40px" }}>
                    {p.placeholderIcon}
                  </span>
                  {p.verified && (
                    <div className="absolute top-2 right-2">
                      <div className="bg-card/90 backdrop-blur-sm p-2 rounded-full shadow-sm">
                        <span
                          className="material-symbols-outlined text-accent text-[20px]"
                          style={{ fontVariationSettings: "'FILL' 1" }}
                        >
                          verified
                        </span>
                      </div>
                    </div>
                  )}
                </div>
                <div className="p-4">
                  <span className={`${CAPS} text-[10px] text-on-surface-variant tracking-widest mb-1 block`}>
                    {p.sector}
                  </span>
                  <h4 className="font-display text-[18px] leading-tight mb-2">{p.title}</h4>
                  <div className="flex justify-between items-center mb-4">
                    <span className={`${p.statusStyle} px-3 py-1 rounded-full ${CAPS} text-[10px]`}>
                      {p.statusLabel}
                    </span>
                    <span className="font-mono text-[14px] text-primary">{p.value}</span>
                  </div>
                  <div className="pt-2 border-t border-outline-variant flex items-center justify-between">
                    <span className={`${CAPS} text-[10px] text-on-surface-variant`}>REF: {p.ref}</span>
                    <span className="text-primary font-bold text-[12px] flex items-center gap-1 group-hover:underline">
                      {p.cta}
                      <span className="material-symbols-outlined text-[16px]">{p.ctaIcon}</span>
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
