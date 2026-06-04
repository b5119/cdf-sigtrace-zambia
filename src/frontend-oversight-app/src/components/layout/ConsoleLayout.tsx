import { Navigate } from "react-router-dom";
import Sidebar from "./Sidebar";
import { useAuth } from "../../store/auth";
import { ROUTES } from "../../lib/routes";

export default function ConsoleLayout({ children }: { children: React.ReactNode }) {
  const { accessToken } = useAuth();
  if (!accessToken) return <Navigate to={ROUTES.LOGIN} replace />;
  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 p-10 bg-surface min-h-screen">{children}</main>
    </div>
  );
}
