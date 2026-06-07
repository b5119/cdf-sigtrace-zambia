// FAQ — its own page (distinct from How it works / Methodology).
import { useState } from "react";
import { Link } from "react-router-dom";
import { ROUTES } from "../lib/routes";

const FAQS = [
  { q: "Why two blockchains?", a: "Hyperledger Fabric (permissioned) anchors contract and audit hashes between institutions; Polygon (public) records multi-party project confirmations so a single party cannot mark a project complete alone. Together they give cross-institution trust plus a publicly auditable trail." },
  { q: "Is a flag the same as a finding of corruption?", a: "No. Every output is a risk signal that requires human review by the relevant oversight institution. It indicates a contract worth examining, not proven wrongdoing." },
  { q: "How is my data protected?", a: "Personal data stays off-chain and can be erased; only cryptographic hashes are anchored to the ledger. The public tier is fully de-identified — no supplier or official names. See the data-protection notice." },
  { q: "Where does the contract data come from?", a: "Procurement data is ingested from ZPPA's OCDS (Open Contracting Data Standard) feed. Field evidence comes from community monitors via the CDF Pulse app." },
  { q: "Can I verify a contract myself?", a: "Yes. On the Verify page you can drop a contract PDF; your browser computes its SHA-256 locally and checks it against the anchored hash — nothing leaves your device unencrypted." },
  { q: "Who can see the named, restricted data?", a: "Only authorised officers at the OAG, ACC and ZPPA, through the separate Oversight console with mandatory MFA. Every access is recorded in an immutable audit log." },
];

export default function Faq() {
  const [open, setOpen] = useState<number | null>(0);
  return (
    <main className="max-w-[820px] mx-auto px-6 md:px-12 py-10">
      <h1 className="disp text-2xl font-bold text-ink">Frequently asked questions</h1>
      <p className="text-sm text-on-surface-variant mt-1">Plain-language answers about how the public ledger works.</p>

      <div className="mt-6 space-y-2">
        {FAQS.map((f, i) => (
          <div key={i} className="bg-card border border-outline-variant rounded-xl overflow-hidden">
            <button type="button" onClick={() => setOpen(open === i ? null : i)}
              className="w-full flex items-center justify-between gap-3 px-4 py-3 text-left hover:bg-surface-2/50">
              <span className="text-sm font-semibold text-ink">{f.q}</span>
              <span className="material-symbols-outlined text-on-surface-variant transition-transform" style={{ transform: open === i ? "rotate(180deg)" : "none" }}>expand_more</span>
            </button>
            {open === i && <p className="px-4 pb-4 text-sm text-on-surface-variant">{f.a}</p>}
          </div>
        ))}
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <Link to={ROUTES.METHODOLOGY} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent">
          <span className="material-symbols-outlined">menu_book</span>Read the methodology
        </Link>
        <Link to={ROUTES.CONSENT} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 text-ink hover:bg-surface-2">
          <span className="material-symbols-outlined">shield</span>Data protection
        </Link>
      </div>
    </main>
  );
}
