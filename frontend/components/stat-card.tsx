export function StatCard({
  value,
  label,
  accent,
}: {
  value: string | number;
  label: string;
  accent?: "primary" | "accent" | "success";
}) {
  const color =
    accent === "accent"
      ? "text-accent"
      : accent === "success"
        ? "text-success"
        : accent === "primary"
          ? "text-primary"
          : "text-text";
  const glow = accent === "primary" ? "text-glow" : "";
  return (
    <div className="card p-4">
      <div
        className={`font-display text-2xl font-bold tabular-nums whitespace-nowrap sm:text-3xl ${color} ${glow}`}
      >
        {value}
      </div>
      <div className="mt-1 font-mono text-[11px] uppercase tracking-[0.16em] text-text-secondary">
        {label}
      </div>
    </div>
  );
}