export default function StatsBar({
  total, bugs, critical, clean,
}: {
  total: number; bugs: number; critical: number; clean: number;
}) {
  return (
    <div className="stats-bar">
      {[
        { label: "PRs Analyzed", value: total, color: "#a78bfa" },
        { label: "Bugs Found", value: bugs, color: "#f87171" },
        { label: "Critical", value: critical, color: "#ef4444" },
        { label: "Clean PRs", value: clean, color: "#34d399" },
      ].map((s) => (
        <div key={s.label} className="stat-card">
          <div className="stat-value" style={{ color: s.color }}>{s.value}</div>
          <div className="stat-label">{s.label}</div>
        </div>
      ))}
    </div>
  );
}
