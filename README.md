# Code Review AI — Week 1 Setup

## Step 1: Create your GitHub App

1. Go to **GitHub → Settings → Developer settings → GitHub Apps → New GitHub App**
2. Fill in:
   - **App name**: `code-review-ai-yourname` (must be globally unique)
   - **Homepage URL**: `http://localhost:8000` (for now)
   - **Webhook URL**: `https://YOUR_NGROK_URL/webhooks/github` (see Step 3)
   - **Webhook secret**: type any strong random string — copy it for `.env`

3. Under **Repository permissions**, set:
   | Permission | Access |
   |---|---|
   | Pull requests | Read & Write |
   | Contents | Read |
   | Checks | Read & Write |

4. Under **Subscribe to events**, check:
   - ✅ Pull request

5. Click **Create GitHub App**
6. On the next page, note your **App ID**
7. Scroll down → **Generate a private key** → save the `.pem` file in `/backend/`

---

## Step 2: Install your GitHub App on a test repo

1. In your GitHub App settings → **Install App** → choose a repo
2. This allows your app to receive webhook events from that repo

---

## Step 3: Expose your local server with ngrok

```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000
```

Copy the `https://xxxx.ngrok-free.app` URL and paste it into your GitHub App's
**Webhook URL** field: `https://xxxx.ngrok-free.app/webhooks/github`

---

## Step 4: Run the backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Fill in your values in .env

uvicorn main:app --reload --port 8000
```

---

## Step 5: Test it

1. Open any repo where you installed the app
2. Create a new pull request (or push a commit to an existing one)
3. Check your terminal — you should see:

```
[Webhook] Received event: pull_request
[PR #42] Processing: My feature branch
[PR #42] Diff fetched (3420 chars) — ready for AI analysis
```

---

## Step 6: Quick token shortcut for Week 1

Instead of full GitHub App auth, use a **Personal Access Token** for now:

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Generate a token with scopes: `repo`
3. Paste it in `.env` as `GITHUB_TOKEN`

This is fine for Week 1. In Week 3 you'll switch to proper App authentication.

---

## Project structure so far

```
code-review-ai/
└── backend/
    ├── main.py           # FastAPI app + webhook endpoint
    ├── github_client.py  # GitHub API: fetch diffs, post comments
    ├── models.py         # Pydantic data models
    ├── requirements.txt
    └── .env.example
```

## Next up: Week 3

Once webhooks are flowing, we'll send the diff to the Claude API and parse
real bug findings — race conditions, SQL injection, auth bypasses.
