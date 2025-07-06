import os
import requests
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("GitHub PR Review Server")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN is not set")

API_URL = "https://api.github.com/"

@mcp.tool()
def create_pr(repo: str, title: str, body: str, base: str, head: str):
    resp = requests.post(f"{API_URL}/repos/{repo}/pulls",
                        headers={"Authorization": f"token {GITHUB_TOKEN}"},
                        json={"title": title, "body": body, "base": base, "head": head})
    resp.raise_for_status()
    return resp.json()

# 🛠 Tool: List open PRs in a repo (owner/repo format)
@mcp.tool()
def list_prs(repo: str):
    resp = requests.get(f"{API_URL}/repos/{repo}/pulls",
                        headers={"Authorization": f"token {GITHUB_TOKEN}"})
    resp.raise_for_status()
    return [{"number": pr["number"], "title": pr["title"]} for pr in resp.json()]

# 🛠 Tool: Get diff for a specific PR
@mcp.tool()
def get_diff(repo: str, pr_number: int):
    # Step 1: Fetch PR metadata to get the .diff URL
    pr_url = f"{API_URL}/repos/{repo}/pulls/{pr_number}"
    pr_resp = requests.get(pr_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    pr_resp.raise_for_status()
    pr_data = pr_resp.json()

    # Step 2: Use the diff_url from the PR metadata
    diff_url = pr_data.get("diff_url")
    if not diff_url:
        return {"error": "diff_url not found in PR response"}

    # Step 3: Fetch the raw diff content
    diff_resp = requests.get(diff_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    diff_resp.raise_for_status()

    return diff_resp.text

# 🧠 Tool: Suggest comments via LLM prompt
@mcp.prompt("suggest_comments")
def suggest_comments(diff: str) -> str:
    return f"""You are a code reviewer. Please inspect this diff:
{diff}

Provide comments for style, bug risk, clarity.
Return output as JSON list: [{"file": "...", "line": int, "comment": "..."}].
"""

@mcp.prompt("review_pr_prompt")
def review_pr_prompt(diff: str) -> str:
    return f"""You are a code reviewer. Please inspect this diff:
{diff}

Provide a review of the PR. Tell about the lines changed, the changes made, and the overall review.
"""
@mcp.tool()
def review_pr(diff: str):
    return mcp.run_prompt("review_pr_prompt", diff=diff)


@mcp.tool()
def suggest_comments(diff: str):
    return mcp.run_prompt("suggest_comments", diff=diff)

@mcp.tool()
def push_comments(repo:str, pr_number: int, comments: list[dict]):
    resp = requests.post(f"{API_URL}/repos/{repo}/pulls/{pr_number}/comments",
                        headers={"Authorization": f"token {GITHUB_TOKEN}"},
                        json=comments)
    resp.raise_for_status()
    return resp.json()

@mcp.tool()
def merge_pr(repo:str, pr_number: int):
    resp = requests.post(f"{API_URL}/repos/{repo}/pulls/{pr_number}/merge",
                        headers={"Authorization": f"token {GITHUB_TOKEN}"})
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    mcp.run()