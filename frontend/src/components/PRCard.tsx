import { PRAnalysis } from "@/app/page";

export default function PRCard({
  pr,
  selected,
  onClick,
}: {
  pr: PRAnalysis;
  selected: boolean;
  onClick: () => void;
}) {
  const criticalCount = pr.findings.filter((f) => f.severity === "critical").length;
  const warningCount = pr.findings.filter((f) => f.severity === "warning").length;
  const isClean = pr.findings.length === 0;
  const timeAgo = getTimeAgo(pr.analyzed_at);

  return (
    <div className={`pr-card ${selected ? "selected" : ""}`} onClick={onClick}>
      <div className="pr-card-top">
        <span className="pr-num">#{pr.pr_number}</span>
        <span className="pr-time">{timeAgo}</span>
      </div>
      <div className="pr-card-title">{pr.title}</div>
      <div className="pr-card-repo">{pr.repo}</div>
      <div className="pr-card-bottom">
        {isClean ? (
          <span className="badge badge-clean">✅ Clean</span>
        ) : (
          <>
            {criticalCount > 0 && (
              <span className="badge badge-critical">🔴 {criticalCount} Critical</span>
            )}
            {warningCount > 0 && (
              <span className="badge badge-warning">🟡 {warningCount} Warning</span>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function getTimeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}
