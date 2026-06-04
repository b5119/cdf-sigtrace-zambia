// P5 — Public Project Detail (matches stitch_export/project_transparency_detail)
// Shows disbursement, photographic evidence (IPFS), verified location, confirmation status.
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { projectApi } from "../lib/api";
import { ROUTES } from "../lib/routes";

function fmt(n: number | null | undefined) {
  if (n == null) return "—";
  return `ZMW ${n.toLocaleString()}`;
}

const STATUS_BADGE: Record<string, string> = {
  confirmed: "bg-risk-low/10 text-risk-low border-risk-low/20",
  pending:   "bg-risk-mid/10 text-risk-mid border-risk-mid/20",
  rejected:  "bg-risk-high/10 text-risk-high border-risk-high/20",
};

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>();

  const { data: project, isLoading } = useQuery({
    queryKey: ["project", id],
    queryFn: () => projectApi.detail(id!).then(r => r.data),
    enabled: !!id,
  });
  const { data: evidence } = useQuery({
    queryKey: ["project-evidence", id],
    queryFn: () => projectApi.evidence(id!).then(r => r.data),
    enabled: !!id,
  });

  if (isLoading) return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-4">
      {[1,2,3].map(i => <div key={i} className="h-32 bg-surface-2 rounded-xl animate-pulse" />)}
    </div>
  );
  if (!project) return (
    <div className="max-w-4xl mx-auto px-4 py-16 text-center">
      <span className="material-symbols-outlined text-5xl text-outline mb-4 block">search_off</span>
      <h2 className="font-display text-xl font-bold mb-2">Project not found</h2>
      <Link to={ROUTES.MAP} className="text-primary hover:underline">← Back to map</Link>
    </div>
  );

  const items = evidence?.evidence ?? [];

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-on-surface-variant mb-6">
        <Link to={ROUTES.MAP} className="hover:text-primary">Map</Link>
        {project.constituency_id && (
          <>
            <span>/</span>
            <Link to={`/constituencies/${project.constituency_id}`} className="hover:text-primary">{project.constituency_id}</Link>
          </>
        )}
        <span>/</span>
        <span className="text-on-surface font-medium">{project.title}</span>
      </div>

      {/* Header */}
      <div className="bg-card border border-outline-variant rounded-2xl p-6 mb-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl font-bold">{project.title}</h1>
            <p className="text-on-surface-variant">{project.category}</p>
          </div>
          {project.verified ? (
            <span className="inline-flex items-center gap-1.5 bg-risk-low/10 text-risk-low border border-risk-low/20 rounded-full px-3 py-1 text-sm font-semibold">
              <span className="material-symbols-outlined text-base">verified</span>Verified Complete
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 bg-risk-mid/10 text-risk-mid border border-risk-mid/20 rounded-full px-3 py-1 text-sm font-semibold">
              <span className="material-symbols-outlined text-base">pending</span>{project.status}
            </span>
          )}
        </div>

        {/* Disbursement summary */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          {[
            ["Disbursement", fmt(project.disbursement_amount)],
            ["Date", project.disbursement_date ?? "—"],
            ["Evidence Items", project.evidence_count],
            ["Confirmed", project.confirmed_count],
          ].map(([label, value]) => (
            <div key={String(label)} className="bg-surface-2 rounded-lg p-3">
              <p className="text-xs text-on-surface-variant">{label}</p>
              <p className="font-display text-lg font-bold">{value}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Evidence gallery */}
        <div className="md:col-span-2">
          <h2 className="font-display font-semibold text-lg mb-3">Photographic Evidence</h2>
          {items.length === 0 ? (
            <div className="bg-card border border-outline-variant rounded-xl p-12 text-center text-on-surface-variant">
              <span className="material-symbols-outlined text-4xl mb-2 block">no_photography</span>
              <p className="text-sm">No field evidence submitted yet</p>
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 gap-4">
              {items.map(ev => (
                <div key={ev.submission_id} className="bg-card border border-outline-variant rounded-xl overflow-hidden">
                  {ev.ipfs_cid ? (
                    <img src={projectApi.photoUrl(ev.ipfs_cid)} alt="evidence"
                      className="w-full h-44 object-cover bg-surface-2"
                      onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
                  ) : (
                    <div className="w-full h-44 bg-surface-2 flex items-center justify-center text-on-surface-variant">
                      <span className="material-symbols-outlined text-3xl">image</span>
                    </div>
                  )}
                  <div className="p-3">
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-sm font-medium">{ev.category ?? "Evidence"}</span>
                      <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${STATUS_BADGE[ev.status] ?? STATUS_BADGE.pending}`}>
                        {ev.status}
                      </span>
                    </div>
                    <p className="text-xs text-on-surface-variant mono">{ev.lat.toFixed(4)}, {ev.lng.toFixed(4)}</p>
                    <p className="text-xs text-on-surface-variant">{new Date(ev.captured_at).toLocaleDateString()}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs text-on-surface-variant">
                        {ev.confirmation_count}/2 confirmations
                      </span>
                      {ev.onchain_tx && (
                        <span className="inline-flex items-center gap-1 text-xs text-risk-low">
                          <span className="material-symbols-outlined text-sm">link</span>on-chain
                        </span>
                      )}
                    </div>
                    {ev.ipfs_cid && (
                      <p className="text-[10px] text-on-surface-variant mono truncate mt-1.5" title={ev.ipfs_cid}>
                        IPFS {ev.ipfs_cid}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Verified location */}
        <div>
          <h2 className="font-display font-semibold text-lg mb-3">Verified Location</h2>
          <div className="bg-card border border-outline-variant rounded-xl overflow-hidden">
            {project.location ? (
              <>
                <div className="h-48 bg-surface-2 relative flex items-center justify-center">
                  <span className="material-symbols-outlined text-5xl text-primary">location_on</span>
                  <div className="absolute inset-0 bg-primary/5" />
                </div>
                <div className="p-3">
                  <p className="text-xs text-on-surface-variant mb-1">GPS-verified centroid</p>
                  <p className="mono text-sm">{project.location.lat.toFixed(5)}, {project.location.lng.toFixed(5)}</p>
                </div>
              </>
            ) : (
              <div className="h-48 flex items-center justify-center text-on-surface-variant text-sm">
                No location data
              </div>
            )}
          </div>

          <div className="bg-surface-2 border border-outline-variant rounded-lg p-3 mt-4 text-xs text-on-surface-variant">
            Evidence photos are stored on IPFS (content-addressed). Each confirmation is recorded on
            the Polygon ledger. This page shows de-identified data only.
          </div>
        </div>
      </div>
    </div>
  );
}
