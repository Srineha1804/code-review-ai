import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

SYSTEM_PROMPT = """You are an expert code reviewer specializing in finding security vulnerabilities and bugs.

Analyze the given code diff and find REAL bugs only — not style issues or typos.

Look specifically for:
- SQL Injection
- Authentication bypass
- Race conditions  
- Off-by-one errors in financial/critical logic
- Insecure direct object references
- Missing input validation
- Hardcoded secrets or credentials
- Unhandled exceptions that could crash the app

Respond ONLY with a valid JSON object in this exact format (no markdown, no explanation):
{
  "findings": [
    {
      "severity": "critical",
      "bug_type": "SQL Injection",
      "file_path": "backend/user.py",
      "line_number": 42,
      "explanation": "User input is directly interpolated into SQL query without sanitization",
      "suggestion": "Use parameterized queries: cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
    }
  ],
  "summary": "Found 1 critical issue: SQL injection vulnerability in user.py"
}

If no real bugs found, return:
{
  "findings": [],
  "summary": "No critical bugs found in this PR"
}
"""


async def analyze_diff_with_gemini(diff: str, pr_number: int) -> dict:
    """Send PR diff to Gemini and get bug findings back."""

    print(f"[PR #{pr_number}] Sending diff to Gemini AI for analysis...")

    # Limit diff size to avoid token limits
    if len(diff) > 8000:
        diff = diff[:8000] + "\n... (diff truncated)"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"{SYSTEM_PROMPT}\n\nAnalyze this PR diff:\n\n{diff}"
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1500,
        }
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(GEMINI_URL, json=payload)

        if response.status_code != 200:
            print(f"[PR #{pr_number}] Gemini API error: {response.status_code}")
            return {"findings": [], "summary": "AI analysis failed"}

        data = response.json()

        # Extract text from Gemini response
        text = data["candidates"][0]["content"]["parts"][0]["text"]

        # Clean up response if it has markdown code blocks
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        result = json.loads(text)
        print(f"[PR #{pr_number}] Gemini found {len(result.get('findings', []))} issue(s)")
        return result


def format_comment(findings: dict, pr_number: int) -> str:
    """Format AI findings into a nice GitHub PR comment."""

    findings_list = findings.get("findings", [])
    summary = findings.get("summary", "Analysis complete")

    if not findings_list:
        return f"""## 🤖 Code Review AI — PR #{pr_number}

✅ **{summary}**

No critical bugs detected in this pull request.

---
*Powered by Code Review AI + Gemini*"""

    # Build findings table
    severity_emoji = {
        "critical": "🔴",
        "warning": "🟡",
        "info": "🔵"
    }

    comment = f"""## 🤖 Code Review AI — PR #{pr_number}

⚠️ **{summary}**

---

"""
    for i, finding in enumerate(findings_list, 1):
        emoji = severity_emoji.get(finding.get("severity", "info"), "🔵")
        comment += f"""### {emoji} Issue #{i}: {finding.get('bug_type', 'Bug')}

**Severity:** `{finding.get('severity', 'unknown').upper()}`
**File:** `{finding.get('file_path', 'unknown')}`
**Line:** {finding.get('line_number', 'N/A')}

**Problem:** {finding.get('explanation', '')}

**Fix:** {finding.get('suggestion', '')}

---

"""

    comment += "*Powered by Code Review AI + Gemini*"
    return comment