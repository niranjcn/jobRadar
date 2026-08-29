export function RadarMark() {
  return (
    <span className="relative inline-flex h-6 w-6 items-center justify-center rounded-full border-2 border-border bg-surface shadow-offset-sm">
      <span className="absolute inset-[3px] rounded-full border border-primary/30" />
      <span className="h-1.5 w-1.5 rounded-full bg-primary" />
    </span>
  );
}
