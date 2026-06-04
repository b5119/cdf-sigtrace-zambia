import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Login from "./pages/Login";
import Mfa from "./pages/Mfa";
import Home from "./pages/Home";
import Capture from "./pages/Capture";
import Submissions from "./pages/Submissions";
import SubmissionDetail from "./pages/SubmissionDetail";
import Profile from "./pages/Profile";

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } } });

function RequireAuth({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem("pulse_token");
  return token ? <>{children}</> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/mfa" element={<Mfa />} />
          <Route path="/home" element={<RequireAuth><Home /></RequireAuth>} />
          <Route path="/capture" element={<RequireAuth><Capture /></RequireAuth>} />
          <Route path="/submissions" element={<RequireAuth><Submissions /></RequireAuth>} />
          <Route path="/submissions/:id" element={<RequireAuth><SubmissionDetail /></RequireAuth>} />
          <Route path="/profile" element={<RequireAuth><Profile /></RequireAuth>} />
          <Route path="*" element={<Navigate to="/home" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
