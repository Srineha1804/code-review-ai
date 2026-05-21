"""
Code Review AI — GitHub Actions Script
Reads the PR diff, sends to Gemini, posts findings as a PR comment.
"""
import os
import json
import httpx

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
PR_NUMBER = os.environ["PR_NUMBER"]
REPO = os.environ["REPO"]

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

SYSTEM_PROMPT = """You are an expert code reviewer specializing in security vulnerabilities.
Analyze the PR diff and find REAL bugs only — not style issues.
Look for: SQL Injection, Auth bypass, Race conditions, Hardcoded secrets, Missing validation.

Respond ONLY with valid JSON (no markdown):
{
  "findings": [
    {
      "severity": "critical",
      "bug_type": "SQL Injection",
      "file_path": "file.py",
      "line_number": 42,
      "explanation": "...",
      "suggestion": "..."
    }
  ],
  "summary": "Found X issues"
}
If no bugs: {"findings": [], "summary": "No critical bugs found"}"""


def read_diff() -> str:
    try:
        with open("pr_diff.txt", "r") as f:
            diff = f.read()
        return diff[:8000] if len(diff) > 8000 else diff
    except FileNotFoundError:
        print("No diff file found")
        return ""


def analyze_with_gemini(diff: str) -> dict:
    payload = {
        "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\nAnalyze:\n\n{diff}"}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1500},
    }
    response = httpx.post(GEMINI_URL, json=payload, timeout=30)
    if response.status_code != 200:
        print(f"Gemini error: {response.status_code}")
        return {"findings": [], "summary": "Analysis failed"}

    text = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def format_comment(findings: dict) -> str:
    items = findings.get("findings", [])
    summary = findings.get("summary", "")
    emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}

    if not items:
        return f"## 🤖 Code Review AI\n\n✅ **{summary}**\n\nNo critical bugs found!\n\n---\n*Powered by Code Review AI + Gemini*"

    comment = f"## 🤖 Code Review AI\n\n⚠️ **{summary}**\n\n---\n\n"
    for i, f in enumerate(items, 1):
        e = emoji.get(f.get("severity", "info"), "🔵")
        comment += f"### {e} Issue #{i}: {f.get('bug_type', 'Bug')}\n\n"
        comment += f"**Severity:** `{f.get('severity','').upper()}`  \n"
        comment += f"**File:** `{f.get('file_path', '')}`  \n"
        comment += f"**Line:** {f.get('line_number', 'N/A')}\n\n"
        comment += f"**Problem:** {f.get('explanation', '')}\n\n"
        comment += f"**Fix:** `{f.get('suggestion', '')}`\n\n---\n\n"
    comment += "*Powered by Code Review AI + Gemini*"
    return comment


def post_comment(body: str):
    url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    response = httpx.post(url, headers=headers, json={"body": body})
    if response.status_code == 201:
        print(f"✅ Comment posted on PR #{PR_NUMBER}")
    else:
        print(f"Failed to post comment: {response.status_code}")


if __name__ == "__main__":
    print("🤖 Code Review AI starting...")
    diff = read_diff()
    if not diff:
        print("Empty diff — skipping analysis")
        exit(0)

    print(f"📄 Diff size: {len(diff)} chars")
    findings = analyze_with_gemini(diff)
    print(f"🔍 Found {len(findings.get('findings', []))} issue(s)")
    comment = format_comment(findings)
    post_comment(comment)
    print("✅ Done!")
