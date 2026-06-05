import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { pulseApi } from "../lib/api";

export default function Mfa() {
  const [code, setCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const token = sessionStorage.getItem("mfa_token");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    try {
      const res = await pulseApi.mfaVerify(token!, code);
      if (res.data.access_token) {
        localStorage.setItem("pulse_token", res.data.access_token);
        localStorage.setItem("pulse_refresh", res.data.refresh_token ?? "");
        sessionStorage.removeItem("mfa_token");
        navigate("/home");
      }
    } catch { setError("Invalid code."); }
  }

  return (
    <div className="min-h-screen bg-ink flex items-center justify-center p-6">
      <form onSubmit={submit} className="bg-card rounded-2xl p-6 w-full max-w-sm">
        <h1 className="font-display font-bold text-lg text-center mb-4">Enter 2FA code</h1>
        <input value={code} onChange={e => setCode(e.target.value.replace(/\D/g, "").slice(0,6))}
          inputMode="numeric" autoFocus placeholder="000000"
          className="w-full border border-outline-variant rounded-lg px-3 py-3 text-center mono text-2xl tracking-[0.4em] bg-surface outline-none" />
        {error && <p className="text-risk-high text-sm text-center mt-2">{error}</p>}
        <button type="submit" disabled={code.length !== 6}
          className="w-full bg-primary text-white font-semibold py-3 rounded-lg mt-4 disabled:opacity-50">Verify</button>
      </form>
    </div>
  );
}
