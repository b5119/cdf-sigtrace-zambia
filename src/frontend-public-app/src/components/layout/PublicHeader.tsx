// Shared public header — faithful to design/screens generated header (Explore/Data/About dropdowns).
import { Link } from "react-router-dom";
import { ROUTES } from "../../lib/routes";

const OFFICIALS = "http://localhost:5174";

function Dropdown({ label, items }: { label: string; items: { to: string; text: string }[] }) {
  return (
    <div className="relative group">
      <button className="flex items-center gap-1 text-sm text-on-surface-variant hover:text-ink">
        {label}<span className="material-symbols-outlined" style={{ fontSize: 16 }}>expand_more</span>
      </button>
      <div className="absolute left-0 top-full pt-2 hidden group-hover:block z-50">
        <div className="w-56 bg-card border border-outline-variant rounded-xl shadow-lg p-2">
          {items.map(i => (
            <Link key={i.text} to={i.to} className="block px-3 py-2 rounded-lg text-sm text-on-surface hover:bg-surface-2">{i.text}</Link>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function PublicHeader() {
  return (
    <header className="sticky top-0 z-50 flex justify-between items-center px-6 md:px-12 h-16 bg-card border-b border-outline-variant">
      <Link to={ROUTES.HOME} className="flex items-center gap-2.5">
        <img src="/coat_of_arms.png" alt="Republic of Zambia" className="h-8 w-8 object-contain" />
        <span className="disp font-bold tracking-tight">REP. OF ZAMBIA <span className="text-outline font-normal">|</span> LEDGER</span>
      </Link>
      <nav className="hidden md:flex items-center gap-7">
        <Dropdown label="Explore" items={[
          { to: ROUTES.DASHBOARD, text: "National dashboard" },
          { to: ROUTES.MAP, text: "National map" },
          { to: ROUTES.CONSTITUENCIES, text: "Constituencies" },
          { to: ROUTES.PROJECTS, text: "Projects" },
          { to: ROUTES.RISK, text: "Procurement risk" },
        ]} />
        <Dropdown label="Data" items={[
          { to: ROUTES.OPEN_DATA, text: "Open data & datasets" },
          { to: ROUTES.API, text: "Public API" },
          { to: ROUTES.AUDIT_TRAIL, text: "Public ledger (audit trail)" },
        ]} />
        <Dropdown label="About" items={[
          { to: ROUTES.ABOUT, text: "How it works" },
          { to: ROUTES.METHODOLOGY, text: "Methodology" },
          { to: ROUTES.FAQ, text: "FAQ" },
          { to: ROUTES.CONSENT, text: "Data protection" },
        ]} />
      </nav>
      <div className="flex items-center gap-5">
        <a href={OFFICIALS} className="hidden md:flex items-center gap-1.5 text-sm text-on-surface-variant hover:text-ink">
          <span className="material-symbols-outlined" style={{ fontSize: 18 }}>lock</span>For officials
          <span className="material-symbols-outlined" style={{ fontSize: 16 }}>chevron_right</span>
        </a>
        <Link to={ROUTES.VERIFY} className="bg-primary text-white text-sm font-semibold px-4 py-2 rounded-lg flex items-center gap-2">
          <span className="material-symbols-outlined" style={{ fontSize: 18 }}>shield</span>Verify a contract
        </Link>
      </div>
    </header>
  );
}
