import { Link, useLocation } from "react-router-dom";
import { ROUTES } from "../../lib/routes";

const NAV_LINKS = [
  { label: "Dashboard",   to: ROUTES.DASHBOARD },
  { label: "Map",         to: ROUTES.MAP },
  { label: "Risk",        to: ROUTES.RISK },
  { label: "Open Data",   to: ROUTES.OPEN_DATA },
  { label: "Verify",      to: ROUTES.VERIFY },
  { label: "About",       to: ROUTES.ABOUT },
];

export default function Navbar() {
  const { pathname } = useLocation();
  return (
    <nav className="sticky top-0 z-40 bg-card border-b border-outline-variant backdrop-blur">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-14">
        <Link to={ROUTES.HOME} className="flex items-center gap-2 font-display font-bold text-primary text-lg">
          <span className="text-accent">◈</span> CDF Integrity
        </Link>
        <div className="hidden md:flex items-center gap-1">
          {NAV_LINKS.map(({ label, to }) => (
            <Link
              key={to}
              to={to}
              className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                pathname === to
                  ? "bg-primary/10 text-primary"
                  : "text-on-surface-variant hover:bg-surface-2 hover:text-on-surface"
              }`}
            >
              {label}
            </Link>
          ))}
        </div>
        <a
          href="#officials"
          className="hidden md:flex items-center gap-1 text-xs text-on-surface-variant border border-outline-variant rounded px-3 py-1.5 hover:bg-surface-2 transition-colors"
        >
          🔒 For Officials
        </a>
      </div>
    </nav>
  );
}
