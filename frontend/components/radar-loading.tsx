export function RadarLoading({ label = "Scanning the job market…" }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-16 text-text-secondary">
      <div className="relative flex h-20 w-20 items-center justify-center">
        <span className="absolute inset-0 rounded-full border border-[var(--glass-border)]" />
        <span className="radar-sweep absolute inset-0 rounded-full border-b-2 border-l-2 border-primary/70" />
        <span className="absolute top-1/2 left-1/2 h-1.5 w-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary shadow-neo-glow" />
        <span className="pulse-dot absolute right-2 top-4 h-1.5 w-1.5 rounded-full bg-accent" />
      </div>
      <p className="text-sm">{label}</p>
    </div>
  );
}