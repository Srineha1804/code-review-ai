from pydantic import BaseModel


class PREvent(BaseModel):
    action: str           # opened | synchronize | reopened
    number: int           # PR number e.g. 42
    title: str
    author: str
    repo_full_name: str   # e.g. "yourname/your-repo"
    head_sha: str         # latest commit SHA on the PR branch
    base_branch: str      # e.g. "main"
    head_branch: str      # e.g. "feature/new-login"
    pr_url: str


class BugFinding(BaseModel):
    severity: str         # critical | warning | info
    bug_type: str         # e.g. "SQL Injection", "Race Condition"
    file_path: str
    line_number: int | None
    explanation: str
    suggestion: str


class AnalysisResult(BaseModel):
    pr_number: int
    repo: str
    findings: list[BugFinding]
    summary: str
    analyzed_at: str
