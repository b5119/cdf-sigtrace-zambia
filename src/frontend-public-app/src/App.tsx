import { BrowserRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ROUTES } from "./lib/routes";
import PublicHeader from "./components/layout/PublicHeader";
import Landing          from "./pages/Landing";
import Dashboard        from "./pages/Dashboard";
import MapPage          from "./pages/MapPage";
import ConstituencyDetail from "./pages/ConstituencyDetail";
import ProjectDetail     from "./pages/ProjectDetail";
import ProcurementRisk  from "./pages/ProcurementRisk";
import OpenData         from "./pages/OpenData";
import About            from "./pages/About";
import AuditTrail       from "./pages/AuditTrail";
import VerifyPortal     from "./pages/VerifyPortal";
import Consent          from "./pages/Consent";
import OfflineBanner    from "./components/ui/OfflineBanner";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
});

function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col bg-surface">
      <OfflineBanner />
      <PublicHeader />
      <main className="flex-1">{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path={ROUTES.HOME}        element={<Landing />} />
          <Route path={ROUTES.DASHBOARD}   element={<PublicLayout><Dashboard /></PublicLayout>} />
          <Route path={ROUTES.MAP}         element={<PublicLayout><MapPage /></PublicLayout>} />
          <Route path={ROUTES.CONSTITUENCY} element={<PublicLayout><ConstituencyDetail /></PublicLayout>} />
          <Route path={ROUTES.PROJECT}     element={<PublicLayout><ProjectDetail /></PublicLayout>} />
          <Route path={ROUTES.RISK}        element={<PublicLayout><ProcurementRisk /></PublicLayout>} />
          <Route path={ROUTES.OPEN_DATA}   element={<PublicLayout><OpenData /></PublicLayout>} />
          <Route path={ROUTES.ABOUT}       element={<PublicLayout><About /></PublicLayout>} />
          <Route path={ROUTES.AUDIT_TRAIL} element={<PublicLayout><AuditTrail /></PublicLayout>} />
          <Route path={ROUTES.VERIFY}      element={<PublicLayout><VerifyPortal /></PublicLayout>} />
          <Route path={ROUTES.CONSENT}     element={<PublicLayout><Consent /></PublicLayout>} />
          <Route path="*" element={
            <PublicLayout>
              <div className="flex flex-col items-center justify-center py-32 text-center">
                <span className="material-symbols-outlined text-6xl text-outline mb-4">search_off</span>
                <h1 className="font-display text-3xl font-bold mb-2">Page not found</h1>
                <a href="/" className="text-primary hover:underline mt-2">Back to home</a>
              </div>
            </PublicLayout>
          } />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
