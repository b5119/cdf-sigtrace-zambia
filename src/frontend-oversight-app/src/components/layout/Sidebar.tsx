import { Link, useLocation } from "react-router-dom";
import { ROUTES } from "../../lib/routes";
import { useAuth } from "../../store/auth";
import { authApi } from "../../lib/api";

const NAV = [
  { to: ROUTES.DASHBOARD,        icon: "monitoring",      label: "Risk Dashboard" },
  { to: ROUTES.CONTRACTS,        icon: "table_rows",      label: "Contract Risk List" },
  { to: ROUTES.SUPPLIER_NETWORK, icon: "hub",             label: "Supplier Network" },
  { to: ROUTES.VERIFICATION_REVIEW, icon: "how_to_reg",   label: "Verification Review" },
  { to: ROUTES.ANALYTICS,        icon: "insights",        label: "Analytics" },
  { to: ROUTES.REPORTS,          icon: "summarize",       label: "Reports" },
  { to: ROUTES.NOTIFICATIONS,    icon: "notifications",   label: "Notifications" },
  { to: ROUTES.AUDIT,            icon: "fact_check",      label: "Audit Log" },
  { to: ROUTES.ADMIN,            icon: "settings",        label: "Admin" },
];

export default function Sidebar() {
  const { pathname } = useLocation();
  const { user, logout, refreshToken } = useAuth();

  async function handleLogout() {
    if (refreshToken) {
      try { await authApi.logout(refreshToken); } catch { /* ignore */ }
    }
    logout();
  }

  return (
    <aside className="w-[260px] shrink-0 bg-sidebar min-h-screen p-4 flex flex-col gap-1">
      <div className="flex items-center gap-2 px-2 py-3 mb-2">
        <span className="text-accent text-xl font-bold">◈</span>
        <div>
          <p className="text-white font-display font-semibold text-sm">SigTrace Oversight</p>
          <p className="text-sidebar-muted text-xs">{user?.role?.name ?? "Officer"}</p>
        </div>
      </div>

      {NAV.map(({ to, icon, label }) => {
        const active = pathname === to || (to !== ROUTES.DASHBOARD && pathname.startsWith(to));
        return (
          <Link key={to} to={to}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
              active ? "bg-sidebar-2 text-white font-semibold" : "text-sidebar-muted hover:text-white hover:bg-sidebar-2/60"
            }`}>
            <span className="material-symbols-outlined text-base">{icon}</span>
            <span>{label}</span>
          </Link>
        );
      })}

      <div className="mt-auto pt-4 border-t border-white/10">
        <div className="px-3 py-2 mb-2">
          <p className="text-white text-sm font-medium">{user?.name ?? "Officer"}</p>
          <p className="text-sidebar-muted text-xs">{user?.email}</p>
        </div>
        <button onClick={handleLogout}
          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-sidebar-muted hover:text-white hover:bg-sidebar-2/60 rounded-lg">
          <span className="material-symbols-outlined text-base">logout</span>Sign out
        </button>
      </div>
    </aside>
  );
}
