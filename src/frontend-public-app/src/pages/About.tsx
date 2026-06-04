// P9 — How it works. Faithful port of design/screens/P9_about.html.
import { Link } from "react-router-dom";
import { ROUTES } from "../lib/routes";

const CHECKS = [
  "Signing completeness", "Standstill compliance", "Stage time-gap", "Document forensics",
  "Supplier network", "Score variance", "Amendment value", "Debarment cross-reference",
];

export default function About() {
  return (
    <main className="max-w-[1200px] mx-auto px-6 md:px-12 py-10">
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="disp text-2xl font-bold text-ink">How it works</h1>
          <p className="text-sm text-on-surface-variant mt-1">Plain-language methodology, the eight checks, and our commitments.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-card border border-outline-variant rounded-xl p-5">
          <div className="flex items-center justify-between mb-4"><h3 className="disp font-semibold text-ink">The eight integrity checks</h3></div>
          <ol className="text-sm text-on-surface-variant space-y-1 list-decimal pl-4">
            {CHECKS.map(c => <li key={c}>{c}</li>)}
          </ol>
        </div>
        <div className="bg-card border border-outline-variant rounded-xl p-5">
          <div className="flex items-center justify-between mb-4"><h3 className="disp font-semibold text-ink">Our commitment</h3></div>
          <p className="text-sm text-on-surface-variant">
            Every output is a <b>risk signal requiring review</b>, never a determination of wrongdoing.
            Personal data stays off-chain; only hashes are anchored.
          </p>
        </div>
      </div>

      <div className="mt-6">
        <div className="bg-card border border-outline-variant rounded-xl p-5">
          <div className="flex items-center justify-between mb-4"><h3 className="disp font-semibold text-ink">FAQ</h3></div>
          <div className="text-sm text-on-surface-variant space-y-2">
            <p>▸ Why two blockchains?</p>
            <p>▸ Is this legally admissible?</p>
            <p>▸ How is my data protected?</p>
          </div>
          <div className="mt-3">
            <Link to={ROUTES.VERIFY} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 bg-primary text-white">
              <span className="material-symbols-outlined">shield</span>Verify a contract now
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
