export function RadarLoading({ label = "Scanning the job market…" }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-16" style={{ color: "#CFCBD6" }}>
      <div className="relative flex h-20 w-20 items-center justify-center">
        <span className="absolute inset-0 rounded-full" style={{ border: "1px solid rgba(255,255,255,0.09)" }} />
        <span className="absolute inset-0 rounded-full" style={{ borderBottom: "2px solid rgba(185,141,218,0.7)", borderLeft: "2px solid rgba(185,141,218,0.7)", animation: "spin 1.2s linear infinite" }} />
        <span className="absolute top-1/2 left-1/2 h-1.5 w-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full" style={{ background: "#B98DDA", boxShadow: "0 0 20px rgba(185,141,218,0.5)" }} />
        <span className="absolute right-2 top-4 h-1.5 w-1.5 rounded-full" style={{ background: "#A78BFA", animation: "pulse-dot 1.6s ease-in-out infinite" }} />
      </div>
      <p className="text-sm" style={{ color: "#A39EAB" }}>{label}</p>
    </div>
  );
}