import { Link, useLocation } from "react-router-dom";

const TABS = [
  { to: "/home", icon: "home", label: "Home" },
  { to: "/capture", icon: "add_a_photo", label: "Capture" },
  { to: "/submissions", icon: "sync", label: "Mine" },
  { to: "/confirm", icon: "fact_check", label: "Confirm" },
  { to: "/profile", icon: "person", label: "Profile" },
];

export default function BottomNav() {
  const { pathname } = useLocation();
  return (
    <div className="border-t border-outline-variant flex bg-card shrink-0">
      {TABS.map(t => {
        const active = pathname === t.to;
        return (
          <Link key={t.to} to={t.to}
            className={`flex-1 flex flex-col items-center gap-0.5 py-2 text-[10px] ${active ? "text-primary font-semibold" : "text-on-surface-variant"}`}>
            <span className="material-symbols-outlined" style={{ fontSize: 22 }}>{t.icon}</span>
            <span>{t.label}</span>
          </Link>
        );
      })}
    </div>
  );
}
