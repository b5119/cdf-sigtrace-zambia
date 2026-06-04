import { Link } from "react-router-dom";
import { ROUTES } from "../../lib/routes";

export default function Footer() {
  return (
    <footer className="bg-ink text-sidebar-text mt-16">
      <div className="max-w-7xl mx-auto px-4 py-10 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div>
          <div className="font-display font-bold text-lg mb-2">
            <span className="text-accent">◈</span> CDF Integrity
          </div>
          <p className="text-sidebar-muted text-sm leading-relaxed">
            Blockchain-anchored accountability for Zambia's Constituency Development Fund
            and government procurement.
          </p>
        </div>
        <div>
          <p className="font-semibold text-sm mb-3">Public Portal</p>
          <div className="flex flex-col gap-1.5 text-sm text-sidebar-muted">
            <Link to={ROUTES.DASHBOARD} className="hover:text-sidebar-text">National Dashboard</Link>
            <Link to={ROUTES.MAP}       className="hover:text-sidebar-text">Constituency Map</Link>
            <Link to={ROUTES.RISK}      className="hover:text-sidebar-text">Procurement Risk</Link>
            <Link to={ROUTES.VERIFY}    className="hover:text-sidebar-text">Verify a Contract</Link>
            <Link to={ROUTES.OPEN_DATA} className="hover:text-sidebar-text">Open Data</Link>
          </div>
        </div>
        <div>
          <p className="font-semibold text-sm mb-3">Institutional</p>
          <div className="flex flex-col gap-1.5 text-sm text-sidebar-muted">
            <Link to={ROUTES.ABOUT}       className="hover:text-sidebar-text">About & Methodology</Link>
            <Link to={ROUTES.AUDIT_TRAIL} className="hover:text-sidebar-text">Public Ledger</Link>
            <Link to={ROUTES.CONSENT}     className="hover:text-sidebar-text">Data Protection</Link>
            <a href="#"                   className="hover:text-sidebar-text">Officials Portal ↗</a>
          </div>
        </div>
      </div>
      <div className="border-t border-white/10 max-w-7xl mx-auto px-4 py-4 flex flex-col md:flex-row justify-between items-center text-xs text-sidebar-muted gap-2">
        <span>© {new Date().getFullYear()} Republic of Zambia — Office of the Auditor General. All outputs are risk signals requiring review.</span>
        <span className="mono">Hyperledger Fabric · Polygon PoS · IPFS</span>
      </div>
    </footer>
  );
}
