import BottomNav from "./BottomNav";
import { useOnline } from "../store/useOnline";

export default function PhoneShell({ title, children, hideNav }: { title: string; children: React.ReactNode; hideNav?: boolean }) {
  const online = useOnline();
  return (
    <div className="min-h-screen bg-surface-2 flex items-center justify-center sm:py-8">
      <div className="w-full sm:w-[390px] h-screen sm:h-[800px] bg-card sm:rounded-[2rem] sm:border-4 sm:border-ink overflow-hidden flex flex-col shadow-xl">
        {/* Header */}
        <div className="bg-primary text-white px-4 py-3 flex items-center gap-2 shrink-0">
          <span className="material-symbols-outlined">eco</span>
          <span className="font-display font-semibold">CDF Pulse</span>
          <span className="ml-auto flex items-center gap-2 text-xs">
            <span className={`flex items-center gap-1 ${online ? "text-white" : "text-amber-200"}`}>
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>{online ? "wifi" : "wifi_off"}</span>
              {online ? "Online" : "Offline"}
            </span>
            <span className="opacity-70">·</span>
            <span>{title}</span>
          </span>
        </div>
        {/* Content */}
        <div className="flex-1 overflow-y-auto">{children}</div>
        {/* Bottom nav */}
        {!hideNav && <BottomNav />}
      </div>
    </div>
  );
}
