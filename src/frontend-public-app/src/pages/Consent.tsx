// X6 — Consent / Data-Protection Notice. Faithful port of design/screens/X6_consent.html.
import { Link } from "react-router-dom";
import { ROUTES } from "../lib/routes";

export default function Consent() {
  return (
    <div className="min-h-full flex items-center justify-center bg-surface-2 py-16 px-4">
      <div className="w-[360px] bg-card rounded-2xl p-7 border border-outline-variant">
        <h2 className="disp font-bold mb-3">Data protection</h2>
        <p className="text-sm text-on-surface-variant mb-4">
          We collect only what a report needs. Personal data stays off-chain and can be erased;
          only cryptographic hashes are anchored to the ledger.
        </p>
        <Link to={ROUTES.HOME} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 bg-primary text-white">
          I understand
        </Link>
      </div>
    </div>
  );
}
