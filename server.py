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
    resp = requests.get(f"{API_URL}/repos/{repo}/pulls/{pr_number}",
                        headers={"Authorization": f"token {GITHUB_TOKEN}"},
                        params={"media_type": "diff"})
    resp.raise_for_status()
    return resp.text  # Raw diff

# 🧠 Tool: Suggest comments via LLM prompt
@mcp.prompt("pr_review")
def suggest_comments(diff: str) -> str:
    return f"""You are a code reviewer. Please inspect this diff:
{diff}

Provide comments for style, bug risk, clarity.
Return output as JSON list: [{"file": "...", "line": int, "comment": "..."}].
"""

@mcp.tool()
def review_diff(diff: str):
    return mcp.run_prompt("pr_review", diff=diff)

if __name__ == "__main__":
    mcp.run()