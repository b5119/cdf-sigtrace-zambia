import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { pulseApi } from "../lib/api";
import PhoneShell from "../components/PhoneShell";

// Design-sample assignments — shown when the API is unavailable (matches design M2).
const SAMPLE = {
  constituency_id: "MLG-001",
  constituency_name: "Milenge",
  projects: [
    { id: "proj-001", title: "Community Borehole", category: "Borehole", status: "Active", constituency_id: "MLG-001", constituency_name: "Milenge" },
    { id: "proj-002", title: "Clinic Annex", category: "Healthcare", status: "Active", constituency_id: "MLG-001", constituency_name: "Milenge" },
    { id: "proj-003", title: "Classroom Block", category: "Education", status: "Active", constituency_id: "MLG-001", constituency_name: "Milenge" },
    { id: "proj-004", title: "Feeder Road Culvert", category: "Infrastructure", status: "Active", constituency_id: "MLG-001", constituency_name: "Milenge" },
  ],
};

export default function Home() {
  const { data } = useQuery({
    queryKey: ["assignments"],
    queryFn: () => pulseApi.assignments().then(r => r.data),
    retry: false,
  });

  // Always render; a network error must NOT sign the field worker out.
  const view = data ?? SAMPLE;

  return (
    <PhoneShell title="Home">
      <div className="p-4">
        <p className="text-xs text-on-surface-variant mb-3">
          Constituency: <span className="font-semibold text-on-surface">{view.constituency_name}</span>
        </p>
        <div className="space-y-3">
          {view.projects.map(p => (
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
        </div>
        <Link to="/capture" className="mt-4 w-full bg-primary text-white text-sm font-semibold py-3 rounded-lg flex items-center justify-center gap-2">
          <span className="material-symbols-outlined">add_a_photo</span>New capture
        </Link>
      </div>
    </PhoneShell>
  );
}
