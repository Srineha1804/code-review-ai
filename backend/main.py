import hmac
import hashlib
import json
import os
import httpx

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from github_client import GitHubClient
from models import PREvent

load_dotenv()

app = FastAPI(title="Code Review AI - Webhook Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify that the webhook payload came from GitHub."""
    if not WEBHOOK_SECRET:
        return True  # Skip verification in dev if no secret set
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


async def process_pull_request(event: PREvent):
    """
    Background task: fetch PR diff and trigger AI analysis.
    Replace the TODO with your Claude API call in Week 3-4.
    """
    print(f"[PR #{event.number}] Processing: {event.title}")
    print(f"[PR #{event.number}] Repo: {event.repo_full_name}")
    print(f"[PR #{event.number}] Author: {event.author}")

    client = GitHubClient()
    diff = await client.get_pr_diff(event.repo_full_name, event.number)

    if diff:
        print(f"[PR #{event.number}] Diff fetched ({len(diff)} chars) — ready for AI analysis")
        # TODO Week 3: Send `diff` to Claude API for bug detection
        # findings = await analyze_with_claude(diff)
        # await client.post_pr_comment(event.repo_full_name, event.number, findings)
    else:
        print(f"[PR #{event.number}] Could not fetch diff")


@app.post("/webhooks/github")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """Main webhook endpoint that receives all GitHub App events."""

    # 1. Verify the request is from GitHub
    signature = request.headers.get("X-Hub-Signature-256", "")
    payload_bytes = await request.body()

    if not verify_signature(payload_bytes, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 2. Parse event type and payload
    event_type = request.headers.get("X-GitHub-Event", "")
    payload = json.loads(payload_bytes)

    print(f"[Webhook] Received event: {event_type}")

    # 3. Handle pull_request events
    if event_type == "pull_request":
        action = payload.get("action", "")

        # Only analyze when a PR is opened or new commits are pushed
        if action in ("opened", "synchronize", "reopened"):
            pr = payload["pull_request"]
            event = PREvent(
                action=action,
                number=pr["number"],
                title=pr["title"],
                author=pr["user"]["login"],
                repo_full_name=payload["repository"]["full_name"],
                head_sha=pr["head"]["sha"],
                base_branch=pr["base"]["ref"],
                head_branch=pr["head"]["ref"],
                pr_url=pr["html_url"],
            )

            # Process in background so we return 200 to GitHub immediately
            background_tasks.add_task(process_pull_request, event)
            return {"status": "queued", "pr": event.number, "action": action}

        return {"status": "ignored", "action": action}

    # 4. Handle ping event (sent when you first configure the webhook)
    if event_type == "ping":
        return {"status": "pong", "message": "Webhook configured successfully!"}

    return {"status": "ignored", "event": event_type}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "code-review-ai"}


@app.get("/")
async def root():
    return {
        "message": "Code Review AI Webhook Server",
        "endpoints": {
            "webhook": "POST /webhooks/github",
            "health": "GET /health",
        },
    }
