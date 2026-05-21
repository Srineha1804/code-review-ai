"use client";
import { useState, useEffect } from "react";
import PRCard from "@/components/PRCard";
import StatsBar from "@/components/StatsBar";
import EmptyState from "@/components/EmptyState";

export type Finding = {
  severity: "critical" | "warning" | "info";
  bug_type: string;
  file_path: string;
  line_number: number | null;
  explanation: string;
  suggestion: string;
};

export type PRAnalysis = {
  id: string;
  pr_number: number;
  title: string;
  author: string;
  repo: string;
  pr_url: string;
  findings: Finding[];
  summary: string;
  analyzed_at: string;
};

// Mock data — replace with real API calls in Week 7
const MOCK_DATA: PRAnalysis[] = [
  {
    id: "1",
    pr_number: 3,
    title: "Create buggy_code.py",
    author: "Srineha1804",
    repo: "Srineha1804/test-repo",
    pr_url: "https://github.com/Srineha1804/test-repo/pull/3",
    findings: [
      {
        severity: "critical",
        bug_type: "SQL Injection",
        file_path: "buggy_code.py",
        line_number: 2,
        explanation: "User input is directly interpolated into SQL query without sanitization. An attacker can inject malicious SQL to access or destroy data.",
        suggestion: "Use parameterized queries: cursor.execute('SELECT * FROM users WHERE name = ?', (username,))",
      },
      {
        severity: "critical",
        bug_type: "Hardcoded Credentials",
        file_path: "buggy_code.py",
        line_number: 6,
        explanation: "Password is hardcoded as a string literal. Anyone with code access can see the password.",
        suggestion: "Store passwords as environment variables and use a proper hashing library like bcrypt.",
      },
    ],
    summary: "Found 2 critical issues: SQL injection and hardcoded credentials",
    analyzed_at: new Date().toISOString(),
  },
  {
    id: "2",
    pr_number: 2,
    title: "Create test2.py",
    author: "Srineha1804",
    repo: "Srineha1804/test-repo",
    pr_url: "https://github.com/Srineha1804/test-repo/pull/2",
    findings: [],
    summary: "No critical bugs found in this PR",
    analyzed_at: new Date(Date.now() - 3600000).toISOString(),
  },
];

export default function Dashboard() {
  const [analyses, setAnalyses] = useState<PRAnalysis[]>([]);
  const [selected, setSelected] = useState<PRAnalysis | null>(null);
  const [filter, setFilter] = useState<"all" | "critical" | "clean">("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setAnalyses(MOCK_DATA);
      setLoading(false);
    }, 800);
  }, []);

  const filtered = analyses.filter((a) => {
    if (filter === "critical") return a.findings.some((f) => f.severity === "critical");
    if (filter === "clean") return a.findings.length === 0;
    return true;
  });

  const totalBugs = analyses.reduce((acc, a) => acc + a.findings.length, 0);
  const criticalBugs = analyses.reduce(
    (acc, a) => acc + a.findings.filter((f) => f.severity === "critical").length, 0
  );

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <span className="logo-icon">⬡</span>
            <span className="logo-text">CodeReview<span className="logo-accent">AI</span></span>
          </div>
          <div className="header-meta">
            <span className="live-dot" />
            <span className="live-text">Live</span>
          </div>
        </div>
      </header>

      <main className="main">
        <div className="page-title">
          <h1>Pull Request Analysis</h1>
          <p>AI-powered bug detection across your repositories</p>
        </div>

        <StatsBar
          total={analyses.length}
          bugs={totalBugs}
          critical={criticalBugs}
          clean={analyses.filter((a) => a.findings.length === 0).length}
        />

        <div className="toolbar">
          <div className="filters">
            {(["all", "critical", "clean"] as const).map((f) => (
              <button
                key={f}
                className={`filter-btn ${filter === f ? "active" : ""}`}
                onClick={() => setFilter(f)}
              >
                {f === "all" ? "All PRs" : f === "critical" ? "🔴 Critical" : "✅ Clean"}
              </button>
            ))}
          </div>
          <span className="result-count">{filtered.length} results</span>
        </div>

        <div className="layout">
          <div className="pr-list">
            {loading ? (
              Array(2).fill(0).map((_, i) => (
                <div key={i} className="skeleton" />
              ))
            ) : filtered.length === 0 ? (
              <EmptyState />
            ) : (
              filtered.map((pr) => (
                <PRCard
                  key={pr.id}
                  pr={pr}
                  selected={selected?.id === pr.id}
                  onClick={() => setSelected(pr)}
                />
              ))
            )}
          </div>

          <div className="detail-panel">
            {selected ? (
              <DetailView pr={selected} />
            ) : (
              <div className="detail-empty">
                <span>←</span>
                <p>Select a PR to see findings</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

function DetailView({ pr }: { pr: PRAnalysis }) {
  const severityColor = { critical: "#ef4444", warning: "#f59e0b", info: "#3b82f6" };

  return (
    <div className="detail-view">
      <div className="detail-header">
        <div className="detail-pr-num">PR #{pr.pr_number}</div>
        <h2 className="detail-title">{pr.title}</h2>
        <div className="detail-meta">
          <span>@{pr.author}</span>
          <span>·</span>
          <span>{pr.repo}</span>
          <span>·</span>
          <a href={pr.pr_url} target="_blank" rel="noreferrer">View on GitHub ↗</a>
        </div>
        <div className="detail-summary">{pr.summary}</div>
      </div>

      {pr.findings.length === 0 ? (
        <div className="no-findings">
          <div className="no-findings-icon">✅</div>
          <p>No bugs found — this PR looks clean!</p>
        </div>
      ) : (
        <div className="findings-list">
          {pr.findings.map((f, i) => (
            <div key={i} className="finding-card" style={{ borderLeftColor: severityColor[f.severity] }}>
              <div className="finding-top">
                <span className="finding-type">{f.bug_type}</span>
                <span className="finding-severity" style={{ color: severityColor[f.severity] }}>
                  {f.severity.toUpperCase()}
                </span>
              </div>
              <div className="finding-location">
                📄 {f.file_path} {f.line_number ? `· Line ${f.line_number}` : ""}
              </div>
              <p className="finding-explanation">{f.explanation}</p>
              <div className="finding-fix">
                <span className="fix-label">Fix:</span>
                <code>{f.suggestion}</code>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
