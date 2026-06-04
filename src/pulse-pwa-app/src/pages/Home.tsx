import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { pulseApi } from "../lib/api";
import PhoneShell from "../components/PhoneShell";

export default function Home() {
  const navigate = useNavigate();
  const { data, isError } = useQuery({
    queryKey: ["assignments"],
    queryFn: () => pulseApi.assignments().then(r => r.data),
    retry: false,
  });

  if (isError) { navigate("/login"); return null; }

  return (
    <PhoneShell title="Home">
      <div className="p-4">
        <p className="text-xs text-on-surface-variant mb-3">
          Constituency: <span className="font-semibold text-on-surface">{data?.constituency_name ?? "…"}</span>
        </p>
        <div className="space-y-3">
          {(data?.projects ?? []).map(p => (
            <Link key={p.id} to={`/capture?project=${p.id}`}
              className="block bg-card border border-outline-variant rounded-xl p-3 hover:border-primary/40 transition-colors">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold">{p.title}</p>
                  <p className="text-xs text-on-surface-variant">{p.category} · {p.status}</p>
                </div>
                <span className="material-symbols-outlined text-outline">chevron_right</span>
              </div>
            </Link>
          ))}
          {!data && [1,2,3].map(i => <div key={i} className="h-16 bg-surface-2 rounded-xl animate-pulse" />)}
        </div>
        <Link to="/capture" className="mt-4 w-full bg-primary text-white text-sm font-semibold py-3 rounded-lg flex items-center justify-center gap-2">
          <span className="material-symbols-outlined">add_a_photo</span>New capture
        </Link>
      </div>
    </PhoneShell>
  );
}
