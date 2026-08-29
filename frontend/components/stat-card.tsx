export function StatCard({
  value,
  label,
  accent,
  delay,
}: {
  value: string | number;
  label: string;
  accent?: "primary" | "accent" | "success";
  delay?: number;
}) {
  const color =
    accent === "accent"
      ? "text-text"
      : accent === "success"
        ? "text-success"
        : accent === "primary"
          ? "text-primary"
          : "text-text";
  return (
    <div
      className="card p-4 animate-rise"
      style={delay !== undefined ? { animationDelay: `${delay}ms` } : undefined}
    >
      <div className={`font-fraunces text-[26px] font-extrabold leading-none tracking-[-0.02em] ${color}`}>
        {value}
      </div>
      <div className="mt-2 border-t-2 border-border pt-2 font-mono text-[10px] uppercase tracking-[0.12em] text-text-muted">
        {label}
      </div>
    </div>
  );
}