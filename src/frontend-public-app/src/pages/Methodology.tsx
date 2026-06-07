// Methodology — how the integrity score is computed (its own page, distinct from How it works).
import { Link } from "react-router-dom";
import { ROUTES } from "../lib/routes";

const CHECKS = [
  { n: 1, name: "Signing completeness", what: "Flags contracts missing a signing date or signed parties." },
  { n: 2, name: "Standstill compliance", what: "Award→signing gap under the statutory 14-day standstill (PPA No. 8 of 2020)." },
  { n: 3, name: "Stage time-gap", what: "Identical stage dates or a zero-day evaluation period — signs of compressed process." },
  { n: 4, name: "Document forensics", what: "Round-number bias and predetermined-pricing patterns in tender documents." },
  { n: 5, name: "Supplier network", what: "Shared address / phone / directors / TPIN across competing bidders." },
  { n: 6, name: "Score variance", what: "Award value far above the published estimate (>15% cap)." },
  { n: 7, name: "Amendment value", what: "Cumulative contract amendments exceeding the statutory cap." },
  { n: 8, name: "Debarment cross-reference", what: "Awarded supplier debarred on the ZPPA register at time of award." },
];

export default function Methodology() {
  return (
    <main className="max-w-[1000px] mx-auto px-6 md:px-12 py-10">
      <h1 className="disp text-2xl font-bold text-ink">Methodology</h1>
      <p className="text-sm text-on-surface-variant mt-1 max-w-2xl">How each contract's 0–100 integrity score is computed. Every output is a <b>risk signal requiring review</b>, never a determination of wrongdoing.</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 my-6">
        {[
          ["The 8 checks", "Each contract is run through eight independent checks, derived from the Public Procurement Act."],
          ["Weighted score", "Each check has a calibrated weight (set with the OAG). Skipped checks are excluded and the score re-normalised."],
          ["Risk tier", "0–39 low (green) · 40–69 medium (amber) · 70–100 high (red). High-risk contracts route to the oversight queue."],
        ].map(([t, d]) => (
          <div key={t} className="bg-card border border-outline-variant rounded-xl p-4">
            <h3 className="disp font-semibold text-ink">{t}</h3>
            <p className="text-sm text-on-surface-variant mt-1">{d}</p>
          </div>
        ))}
      </div>

      <div className="bg-card border border-outline-variant rounded-xl p-5">
        <h2 className="disp font-semibold text-ink mb-4">The eight integrity checks</h2>
        <div className="divide-y divide-outline-variant/60">
          {CHECKS.map(c => (
            <div key={c.n} className="flex gap-4 py-3">
              <span className="mono text-sm font-bold text-accent w-6 shrink-0">{c.n}</span>
              <div>
                <p className="text-sm font-semibold text-ink">{c.name}</p>
                <p className="text-sm text-on-surface-variant">{c.what}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <Link to={ROUTES.RISK} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 bg-primary text-white">
          <span className="material-symbols-outlined">monitoring</span>See aggregate risk
        </Link>
        <Link to={ROUTES.FAQ} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent">
          <span className="material-symbols-outlined">quiz</span>Read the FAQ
        </Link>
      </div>
    </main>
  );
}
