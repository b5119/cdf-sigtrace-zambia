import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { pulseApi } from "../lib/api";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true); setError(null);
    try {
      const res = await pulseApi.login(email, password);
      if (res.data.access_token) {
        localStorage.setItem("pulse_token", res.data.access_token);
        localStorage.setItem("pulse_refresh", res.data.refresh_token ?? "");
        navigate("/home");
      } else if (res.data.mfa_challenge_token) {
        sessionStorage.setItem("mfa_token", res.data.mfa_challenge_token);
        navigate("/mfa");
      }
    } catch {
      setError("Sign-in failed. Check your credentials.");
    } finally { setLoading(false); }
  }

  return (
    <div className="min-h-screen bg-ink flex items-center justify-center p-6">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8 text-white">
          <span className="material-symbols-outlined text-5xl text-accent">eco</span>
          <h1 className="font-display text-2xl font-bold mt-2">CDF Pulse</h1>
          <p className="text-sidebar-muted text-sm mt-1 text-white/60">Community monitor field app</p>
        </div>
        <form onSubmit={submit} className="bg-card rounded-2xl p-6 space-y-4">
          <input type="email" required value={email} onChange={e => setEmail(e.target.value)}
            placeholder="monitor@cdf.zm"
            className="w-full border border-outline-variant rounded-lg px-3 py-2.5 text-sm bg-surface focus:ring-2 focus:ring-primary/30 outline-none" />
          <input type="password" required value={password} onChange={e => setPassword(e.target.value)}
            placeholder="Password"
            className="w-full border border-outline-variant rounded-lg px-3 py-2.5 text-sm bg-surface focus:ring-2 focus:ring-primary/30 outline-none" />
          {error && <p className="text-risk-high text-sm">{error}</p>}
          <button type="submit" disabled={loading}
            className="w-full bg-primary text-white font-semibold py-3 rounded-lg disabled:opacity-50">
            {loading ? "Signing in…" : "Sign in"}
          </button>
          <p className="text-xs text-on-surface-variant text-center">Device-bound credential · works offline after first login</p>
        </form>
      </div>
    </div>
  );
}
