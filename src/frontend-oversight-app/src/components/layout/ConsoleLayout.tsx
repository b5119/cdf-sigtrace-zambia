import { Navigate, useLocation } from "react-router-dom";
import Sidebar from "./Sidebar";
import { useAuth } from "../../store/auth";
import { ROUTES } from "../../lib/routes";
import { roleFromToken, canAccess, roleHome } from "../../lib/roles";

export default function ConsoleLayout({ children }: { children: React.ReactNode }) {
  const { accessToken } = useAuth();
  const { pathname } = useLocation();
  if (!accessToken) return <Navigate to={ROUTES.LOGIN} replace />;

  // Role guard — send users who hit a route outside their role to their own home.
  const role = roleFromToken(accessToken);
  if (!canAccess(role, pathname)) return <Navigate to={roleHome(role)} replace />;

  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 p-10 bg-surface min-h-screen">{children}</main>
    </div>
  );
}
