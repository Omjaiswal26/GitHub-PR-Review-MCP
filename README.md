# GitHub-PR-Review-MCP

## Overview

This project is a FastMCP based GitHub PR Review Server.

## Features

- List PRs in a repository
- Get diff for a specific PR
- Suggest comments for a PR
- Review a PR
- 

## Setup

1. Clone the repository

```bash
git clone https://github.com/cymake/GitHub-PR-Review-MCP.git
```

2. Install the dependencies using uv

```bash
pip install uv
uv pip install -r requirements.txt
```

3. Create a `.env` file and set the `GITHUB_TOKEN` environment variable

```bash
GITHUB_TOKEN=your_github_token
```

## Usage

1. Run the server

```bash
python server.py
```

2. Run the client

```bash
python client.py
```


## Connecting to Claude Desktop

1. Run Claude Desktop
2. Run the server
3. Edit 'claude_desktop_config.json'
4. Add the following
```json
{
  "mcpServers": {
    "pr-review-server": {
      "command": "uv",
      "args": ["run","--with", "fastmcp", "--with", "dotenv", "--with", "requests", "python", "path/to/server.py"],
      "env": {
        "GITHUB_TOKEN": "your_github_token"
      }
    }
  }
}
```

5. Restart Claude Desktop

6. Ask about various PRs and Enjoy!!!