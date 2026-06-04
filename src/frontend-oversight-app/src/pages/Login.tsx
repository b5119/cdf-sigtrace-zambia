import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authApi } from "../lib/api";
import { useAuth } from "../store/auth";
import { ROUTES } from "../lib/routes";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { setTokens, setMfaChallenge } = useAuth();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true); setError(null);
    try {
      const res = await authApi.login(email, password);
      const data = res.data;
      if (data.mfa_challenge_token) {
        setMfaChallenge(data.mfa_challenge_token);
        navigate(ROUTES.MFA);
      } else if (data.access_token && data.refresh_token) {
        setTokens(data.access_token, data.refresh_token);
        navigate(ROUTES.DASHBOARD);
      }
    } catch {
      setError("Invalid credentials. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-ink flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <span className="text-accent text-4xl font-bold">◈</span>
          <h1 className="text-white font-display text-2xl font-bold mt-3">SigTrace Oversight</h1>
          <p className="text-sidebar-muted text-sm mt-1">Restricted access · OAG / ACC / ZPPA officers</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-card rounded-2xl p-8 space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-1.5">Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required
              className="w-full border border-outline-variant rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 bg-surface"
              placeholder="officer@oag.gov.zm" />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-1.5">Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required
              className="w-full border border-outline-variant rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 bg-surface"
              placeholder="••••••••••" />
          </div>
          {error && <p className="text-risk-high text-sm">{error}</p>}
          <button type="submit" disabled={loading}
            className="w-full bg-primary hover:bg-primary-h disabled:opacity-50 text-white font-semibold py-3 rounded-lg flex items-center justify-center gap-2">
            {loading ? "Signing in…" : <>Continue <span className="material-symbols-outlined text-base">arrow_forward</span></>}
          </button>
          <p className="text-xs text-on-surface-variant text-center pt-2">
            Protected by mandatory TOTP multi-factor authentication.
          </p>
        </form>

        <p className="text-center text-sidebar-muted text-xs mt-6">
          ← <a href="http://localhost:5173" className="hover:text-white">Back to public portal</a>
        </p>
      </div>
    </div>
  );
}
