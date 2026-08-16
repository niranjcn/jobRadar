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
        : "text-text";
  return (
    <div className="card p-4">
      <div className={`font-serif text-3xl font-semibold ${color}`}>{value}</div>
      <div className="mt-1 text-[13px] text-text-secondary">{label}</div>
    </div>
  );
}