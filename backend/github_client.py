import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_API = "https://api.github.com"


class GitHubClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_pr_diff(self, repo_full_name: str, pr_number: int) -> str | None:
        """Fetch the raw unified diff for a pull request."""
        url = f"{GITHUB_API}/repos/{repo_full_name}/pulls/{pr_number}"
        diff_headers = {**self.headers, "Accept": "application/vnd.github.diff"}

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=diff_headers)
            if response.status_code == 200:
                return response.text
            print(f"[GitHub] Failed to fetch diff: {response.status_code}")
            return None

    async def get_pr_files(self, repo_full_name: str, pr_number: int) -> list[dict]:
        """Fetch list of changed files in a PR."""
        url = f"{GITHUB_API}/repos/{repo_full_name}/pulls/{pr_number}/files"

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            return []

    async def post_pr_comment(
        self, repo_full_name: str, pr_number: int, body: str
    ) -> bool:
        """Post a comment on a pull request (used in Week 3 to post AI findings)."""
        url = f"{GITHUB_API}/repos/{repo_full_name}/issues/{pr_number}/comments"

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                url,
                headers=self.headers,
                json={"body": body},
            )
            if response.status_code == 201:
                print(f"[GitHub] Comment posted on PR #{pr_number}")
                return True
            print(f"[GitHub] Failed to post comment: {response.status_code}")
            return False

    async def create_check_run(
        self,
        repo_full_name: str,
        head_sha: str,
        name: str,
        status: str,
        conclusion: str | None = None,
        summary: str = "",
    ) -> bool:
        """
        Create a GitHub Check Run — shows pass/fail status directly on the PR.
        Use this in Week 7 when integrating with GitHub Actions.
        """
        url = f"{GITHUB_API}/repos/{repo_full_name}/check-runs"
        payload = {
            "name": name,
            "head_sha": head_sha,
            "status": status,
            "output": {
                "title": "Code Review AI",
                "summary": summary,
            },
        }
        if conclusion:
            payload["conclusion"] = conclusion

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=self.headers, json=payload)
            return response.status_code == 201
