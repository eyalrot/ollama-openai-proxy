#!/bin/bash
# GitHub MCP Server wrapper that automatically uses gh CLI token

# Get the GitHub token from gh CLI
GITHUB_TOKEN=$(gh auth token)

# Run the Docker container with the token
exec docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN="$GITHUB_TOKEN" ghcr.io/github/github-mcp-server "$@"