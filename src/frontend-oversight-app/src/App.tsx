import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ROUTES } from "./lib/routes";
import ConsoleLayout from "./components/layout/ConsoleLayout";
import Login from "./pages/Login";
import MfaChallenge from "./pages/MfaChallenge";
import Dashboard from "./pages/Dashboard";
import ContractList from "./pages/ContractList";
import ContractDetail from "./pages/ContractDetail";
import GhostQueue from "./pages/GhostQueue";
import MismatchExplorer from "./pages/MismatchExplorer";
import SupplierNetwork from "./pages/SupplierNetwork";
import VerificationReview from "./pages/VerificationReview";
import Analytics from "./pages/Analytics";
import Reports from "./pages/Reports";
import Cases from "./pages/Cases";
import Notifications from "./pages/Notifications";
import AuditLog from "./pages/AuditLog";
import Admin from "./pages/Admin";
import VerifyDocument from "./pages/VerifyDocument";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path={ROUTES.LOGIN} element={<Login />} />
          <Route path={ROUTES.MFA} element={<MfaChallenge />} />
          <Route path={ROUTES.DASHBOARD} element={<ConsoleLayout><Dashboard /></ConsoleLayout>} />
          <Route path={ROUTES.CONTRACTS} element={<ConsoleLayout><ContractList /></ConsoleLayout>} />
          <Route path={ROUTES.CONTRACT} element={<ConsoleLayout><ContractDetail /></ConsoleLayout>} />
          <Route path={ROUTES.GHOST_QUEUE} element={<ConsoleLayout><GhostQueue /></ConsoleLayout>} />
          <Route path={ROUTES.MISMATCH} element={<ConsoleLayout><MismatchExplorer /></ConsoleLayout>} />
          <Route path={ROUTES.SUPPLIER_NETWORK} element={<ConsoleLayout><SupplierNetwork /></ConsoleLayout>} />
          <Route path={ROUTES.VERIFICATION_REVIEW} element={<ConsoleLayout><VerificationReview /></ConsoleLayout>} />
          <Route path={ROUTES.VERIFY_DOC} element={<ConsoleLayout><VerifyDocument /></ConsoleLayout>} />
          <Route path={ROUTES.ANALYTICS} element={<ConsoleLayout><Analytics /></ConsoleLayout>} />
          <Route path={ROUTES.REPORTS} element={<ConsoleLayout><Reports /></ConsoleLayout>} />
          <Route path={ROUTES.CASES} element={<ConsoleLayout><Cases /></ConsoleLayout>} />
          <Route path={ROUTES.NOTIFICATIONS} element={<ConsoleLayout><Notifications /></ConsoleLayout>} />
          <Route path={ROUTES.AUDIT} element={<ConsoleLayout><AuditLog /></ConsoleLayout>} />
          <Route path={ROUTES.ADMIN} element={<ConsoleLayout><Admin /></ConsoleLayout>} />
          <Route path="/" element={<Navigate to={ROUTES.DASHBOARD} replace />} />
          <Route path="*" element={<Navigate to={ROUTES.DASHBOARD} replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
