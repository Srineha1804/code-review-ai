# 🤖 Code Review AI

> AI-powered security vulnerability detection for GitHub Pull Requests — catches SQL injection, hardcoded credentials, and auth bypasses that GitHub Copilot misses.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![Gemini](https://img.shields.io/badge/AI-Gemini_2.5_Flash-orange)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub_Actions-blue)

---

## 🎯 The Problem

GitHub Copilot and existing AI review tools only catch **typos and style issues**. They completely miss dangerous security bugs like:

- 🔴 SQL Injection
- 🔴 Hardcoded passwords and API keys
- 🔴 Authentication bypasses
- 🔴 Missing input validation
- 🔴 Race conditions in financial logic

Senior engineer review time is the **biggest bottleneck** at every growing company. This tool automates the security layer.

---

## ✅ The Solution

Every time a developer opens a Pull Request, **Code Review AI**:

1. Automatically receives the PR event via GitHub webhook
2. Fetches the code diff using GitHub REST API
3. Sends it to Gemini 2.5 Flash AI for security analysis
4. Posts a structured bug report as a PR comment within 30 seconds
5. Displays all findings on a React dashboard with severity filtering

---

## 🏗️ Architecture

```
Developer opens PR
       ↓
GitHub webhook → FastAPI server
       ↓
Fetch PR diff (GitHub REST API)
       ↓
Gemini AI analysis → structured JSON findings
       ↓
Post comment on PR + update dashboard
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, uvicorn |
| AI Analysis | Gemini 2.5 Flash API |
| Frontend | React, Next.js 14, TypeScript |
| CI/CD | GitHub Actions |
| GitHub Integration | GitHub Apps, Webhooks, REST API |
| Dev Tools | ngrok, python-dotenv, httpx |

---

## 📁 Project Structure

```
code-review-ai/
├── .github/
│   ├── workflows/
│   │   └── code-review-ai.yml   # GitHub Actions CI pipeline
│   └── scripts/
│       └── analyze.py           # AI analysis script
├── backend/
│   ├── main.py                  # FastAPI webhook server
│   ├── analyzer.py              # Gemini AI integration
│   ├── github_client.py         # GitHub API client
│   ├── models.py                # Pydantic data models
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── page.tsx         # Main dashboard
│       │   └── globals.css
│       └── components/
│           ├── PRCard.tsx
│           ├── StatsBar.tsx
│           └── EmptyState.tsx
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+
- A GitHub account
- Gemini API key (free at [aistudio.google.com](https://aistudio.google.com))

### 1. Clone the repo
```bash
git clone https://github.com/Srineha1804/code-review-ai.git
cd code-review-ai
```

### 2. Set up the backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Fill in your values in .env
```

### 3. Configure `.env`
```env
GITHUB_APP_ID=your_app_id
GITHUB_TOKEN=ghp_your_token
GITHUB_WEBHOOK_SECRET=your_secret
GEMINI_API_KEY=your_gemini_key
```

### 4. Run the backend
```bash
uvicorn main:app --reload --port 8000
```

### 5. Set up the frontend
```bash
cd frontend
npm install
npm run dev
```

### 6. Expose with ngrok (for local webhook testing)
```bash
ngrok http 8000
```

Paste the ngrok URL into your GitHub App webhook settings.

---

## ⚡ GitHub Actions CI (Zero Setup)

Add your Gemini API key as a GitHub secret and the workflow runs automatically on every PR — no ngrok or local server needed:

1. Go to your repo → **Settings → Secrets → Actions**
2. Add `GEMINI_API_KEY` as a secret
3. Open any Pull Request — the AI review runs automatically!

---

## 🖥️ Dashboard Features

- **Stats bar** — total PRs analyzed, bugs found, critical count, clean PRs
- **PR list** — all analyzed pull requests with severity badges
- **Detail panel** — full bug report with file, line number, explanation, and fix
- **Severity filter** — filter by All / Critical / Clean
- **Real-time** — updates as new PRs are analyzed

---

## 🔍 Example Bug Detection

Given this code in a PR:

```python
def get_user(username):
    query = f"SELECT * FROM users WHERE name = '{username}'"
    admin_password = "admin123"
    return query
```

Code Review AI automatically posts:

```
🤖 Code Review AI — PR #4

⚠️ Found 2 critical issues in auth.py

🔴 Issue #1: SQL Injection
Severity: CRITICAL
File: auth.py | Line: 2
Problem: User input directly interpolated into SQL query
Fix: Use parameterized queries

🔴 Issue #2: Hardcoded Credentials  
Severity: CRITICAL
File: auth.py | Line: 3
Problem: Password hardcoded as string literal
Fix: Use environment variables + bcrypt hashing
```

---

## 👩‍💻 Author

**Srineha** — [@Srineha1804](https://github.com/Srineha1804)

Built as a portfolio project to demonstrate full-stack AI engineering skills:
RAG pipelines · GitHub Apps · CI/CD · React · FastAPI · Prompt Engineering