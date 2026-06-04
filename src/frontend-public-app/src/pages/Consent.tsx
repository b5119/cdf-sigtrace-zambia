// X6 — Consent / Data-Protection Notice (plain language, WCAG AA)
import { Link } from "react-router-dom";
import { ROUTES } from "../lib/routes";

export default function Consent() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="font-display text-3xl font-bold mb-2">Data Protection Notice</h1>
      <p className="text-on-surface-variant mb-8">
        How CDF Integrity handles your data, under the Zambia Data Protection Act No. 3 of 2021.
      </p>

      <div className="space-y-6 text-on-surface-variant leading-relaxed">
        <section>
          <h2 className="font-display text-xl font-bold text-on-surface mb-2">What this public portal collects</h2>
          <p>
            Nothing about you. This public portal requires no login and collects no personal data.
            We do not use tracking cookies. Documents you upload to the verification portal are
            hashed in memory and <strong className="text-on-surface">never stored</strong> — only the
            SHA-256 hash is compared against the ledger.
          </p>
        </section>

        <section>
          <h2 className="font-display text-xl font-bold text-on-surface mb-2">Two-tier data model</h2>
          <p>
            All data shown here is <strong className="text-on-surface">aggregated and de-identified</strong>.
            Supplier names, procuring-entity names, and field-monitor identities are never published on
            this public tier. Named findings are released only to authorised oversight bodies (OAG, ACC,
            ZPPA) under executed data-sharing agreements.
          </p>
        </section>

        <section>
          <h2 className="font-display text-xl font-bold text-on-surface mb-2">Personal data is off-chain</h2>
          <p>
            No personal data is ever written to any blockchain. The ledgers (Hyperledger Fabric and
            Polygon) hold only SHA-256 hashes and non-personal metadata. Because personal data is
            off-chain, your right to erasure under the DPA can be honoured without affecting the ledger.
          </p>
        </section>

        <section>
          <h2 className="font-display text-xl font-bold text-on-surface mb-2">Your rights</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>Right to access data concerning you</li>
            <li>Right to rectification of inaccurate data</li>
            <li>Right to erasure of personal data (off-chain)</li>
            <li>Right to lodge a complaint with the Data Protection Commissioner</li>
          </ul>
        </section>

        <section>
          <h2 className="font-display text-xl font-bold text-on-surface mb-2">Outputs are signals, not findings</h2>
          <p>
            Every anomaly flag and risk score on this platform is a
            <strong className="text-on-surface"> risk signal requiring expert review</strong> — never a
            determination of wrongdoing. The system augments, and does not replace, the OAG, ACC, ZPPA,
            or any judicial process.
          </p>
        </section>
      </div>

      <Link to={ROUTES.HOME} className="inline-flex items-center gap-1 text-primary hover:underline mt-8">
        <span className="material-symbols-outlined text-base" aria-hidden="true">arrow_back</span>Back to home
      </Link>
    </div>
  );
}
