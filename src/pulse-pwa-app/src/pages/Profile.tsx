import { useNavigate } from "react-router-dom";
import PhoneShell from "../components/PhoneShell";
import { useOnline } from "../store/useOnline";

export default function Profile() {
  const navigate = useNavigate();
  const online = useOnline();
  function signOut() {
    localStorage.removeItem("pulse_token");
    localStorage.removeItem("pulse_refresh");
    navigate("/login");
  }
  return (
    <PhoneShell title="Profile">
      <div className="p-4">
        <div className="flex flex-col items-center py-6">
          <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center">
            <span className="material-symbols-outlined text-4xl text-primary">person</span>
          </div>
          <p className="font-display font-semibold mt-3">Community Monitor</p>
          <p className="text-xs text-on-surface-variant">Milenge Constituency</p>
        </div>
        <div className="bg-card border border-outline-variant rounded-xl divide-y divide-outline-variant">
          {[
            ["Connection", online ? "Online" : "Offline"],
            ["Device", "Registered & bound"],
            ["Storage", "Local queue active"],
            ["Sync", "Automatic on reconnect"],
          ].map(([k, v]) => (
            <div key={k} className="flex justify-between px-4 py-3 text-sm">
              <span className="text-on-surface-variant">{k}</span><span className="font-medium">{v}</span>
            </div>
          ))}
        </div>
        <button onClick={signOut} className="w-full mt-4 border border-risk-high/30 text-risk-high text-sm font-semibold py-3 rounded-lg flex items-center justify-center gap-2">
          <span className="material-symbols-outlined" style={{ fontSize: 18 }}>logout</span>Sign out
        </button>
      </div>
    </PhoneShell>
  );
}
