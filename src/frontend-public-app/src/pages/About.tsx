// P9 — About / Methodology / FAQ (matches design/screens/P9_about.html)

const CHECKS = [
  { id: 1, key: "Signing",         weight: 15, desc: "Contract missing a recorded signing date — a required step before execution." },
  { id: 2, key: "Standstill",      weight: 20, desc: "Contract signed fewer than 14 days after Notice of Award, violating the statutory challenge window." },
  { id: 3, key: "Timeline Gap",    weight: 15, desc: "Identical or impossibly compressed stage dates — suggests fabricated timestamps." },
  { id: 4, key: "Forensic Pricing",weight: 15, desc: "Round-number bid value or awarded amount matching the estimate exactly — predetermined pricing signal." },
  { id: 5, key: "Supplier Network",weight: 10, desc: "Multiple bidders share address, phone, or TPIN — potential cartel or front-company arrangement." },
  { id: 6, key: "Score Variance",  weight:  5, desc: "Award value exceeds published tender estimate by more than 15% — budget gaming signal." },
  { id: 7, key: "Amendment Cap",   weight: 10, desc: "Cumulative amendments increase contract value beyond the permitted 15% threshold." },
  { id: 8, key: "Debarment",       weight: 10, desc: "Awarded supplier appears on the ZPPA debarment register at the time of award." },
];

export default function About() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="font-display text-3xl font-bold mb-2">About & Methodology</h1>
      <p className="text-on-surface-variant mb-10">How CDF Integrity works and what it does — and does not — claim.</p>

      {/* What it is */}
      <section className="mb-10">
        <h2 className="font-display text-xl font-bold mb-3">What this system is</h2>
        <p className="text-on-surface-variant leading-relaxed mb-3">
          CDF Integrity is a blockchain-anchored accountability framework for Zambia's Constituency Development Fund
          and government procurement. It ingests Open Contracting Data Standard (OCDS) records published by the Zambia
          Public Procurement Authority (ZPPA), runs an 8-check anomaly engine over each contract, and anchors the
          SHA-256 hash of each signed contract to a permissioned Hyperledger Fabric ledger.
        </p>
        <p className="text-on-surface-variant leading-relaxed">
          CDF Pulse (the delivery companion) allows vetted community monitors to submit GPS-tagged photographic evidence
          of project completion, confirmed on-chain via a Polygon smart contract multi-party confirmation.
        </p>
      </section>

      {/* What it is NOT */}
      <div className="bg-risk-high/5 border border-risk-high/20 rounded-xl p-5 mb-10">
        <h2 className="font-display text-base font-bold text-risk-high mb-2 flex items-center gap-2">
          <span className="material-symbols-outlined">warning</span>
          Important — what this system does NOT claim
        </h2>
        <ul className="space-y-1.5 text-sm text-on-surface-variant">
          <li>• Anomaly flags are <strong className="text-on-surface">risk signals requiring expert review</strong> — not findings of corruption or wrongdoing.</li>
          <li>• The system does not replace the OAG, ACC, ZPPA, or any judicial process.</li>
          <li>• False positives exist — framework call-offs, emergency procurement and cancelled contracts are excluded where possible.</li>
          <li>• Named data is available only to authorised oversight officers under a data-sharing agreement.</li>
        </ul>
      </div>

      {/* The 8 checks */}
      <section className="mb-10">
        <h2 className="font-display text-xl font-bold mb-4">The 8 Anomaly Checks</h2>
        <p className="text-on-surface-variant text-sm mb-4">Weighted 0–100 risk score. Each check is a deterministic, auditable computation — no opaque ML.</p>
        <div className="space-y-3">
          {CHECKS.map(c => (
            <div key={c.id} className="bg-card border border-outline-variant rounded-lg px-5 py-4 flex gap-4">
              <div className="shrink-0 w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-display font-bold text-sm">{c.id}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2 mb-0.5">
                  <span className="font-semibold text-sm">{c.key}</span>
                  <span className="mono text-xs text-on-surface-variant">{c.weight} pts</span>
                </div>
                <p className="text-xs text-on-surface-variant leading-relaxed">{c.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Legal basis */}
      <section className="mb-10">
        <h2 className="font-display text-xl font-bold mb-3">Legal & Regulatory Basis</h2>
        <div className="grid md:grid-cols-2 gap-3">
          {[
            ["Public Procurement Act No. 8 of 2020", "Standstill period, amendment cap, debarment rules"],
            ["Electronic Communications Act (ECTA)", "Legal recognition of digital signatures and electronic records"],
            ["Data Protection Act No. 3 of 2021", "Governs collection and use of personal data — PII is off-chain only"],
            ["Public Audit Act No. 6 of 2016", "OAG mandate for independent audit of public funds"],
          ].map(([title, desc]) => (
            <div key={title} className="bg-surface-2 border border-outline-variant rounded-lg p-4">
              <p className="font-semibold text-sm">{title}</p>
              <p className="text-xs text-on-surface-variant mt-1">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Data protection */}
      <section>
        <h2 className="font-display text-xl font-bold mb-3">Data Protection</h2>
        <p className="text-on-surface-variant text-sm leading-relaxed">
          Personal data (supplier identity, officer names, monitor identities) is stored off-chain and never written
          to any ledger. This public portal shows aggregated, de-identified data only. Named findings are released
          solely to authorised bodies (OAG, ACC, ZPPA) under executed data-sharing agreements.
          Citizens may request access to data concerning them under the DPA No. 3 of 2021.
        </p>
      </section>
    </div>
  );
}
