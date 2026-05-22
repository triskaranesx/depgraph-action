import os
import requests

GITHUB_API_URL = "https://api.github.com"
COMMENT_MARKER = "<!-- depgraph-action -->"


def get_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def find_existing_comment(repo: str, pr_number: int, token: str) -> int | None:
    """Find an existing depgraph-action comment on the PR. Returns comment ID or None."""
    url = f"{GITHUB_API_URL}/repos/{repo}/issues/{pr_number}/comments"
    headers = get_headers(token)
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    for comment in response.json():
        if COMMENT_MARKER in comment.get("body", ""):
            return comment["id"]
    return None


def post_comment(repo: str, pr_number: int, body: str, token: str) -> dict:
    """Post a new comment on a pull request."""
    url = f"{GITHUB_API_URL}/repos/{repo}/issues/{pr_number}/comments"
    headers = get_headers(token)
    payload = {"body": f"{COMMENT_MARKER}\n{body}"}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def update_comment(repo: str, comment_id: int, body: str, token: str) -> dict:
    """Update an existing comment by ID."""
    url = f"{GITHUB_API_URL}/repos/{repo}/issues/comments/{comment_id}"
    headers = get_headers(token)
    payload = {"body": f"{COMMENT_MARKER}\n{body}"}
    response = requests.patch(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def upsert_comment(repo: str, pr_number: int, body: str, token: str) -> dict:
    """Post or update the depgraph-action comment on a pull request."""
    existing_id = find_existing_comment(repo, pr_number, token)
    if existing_id:
        return update_comment(repo, existing_id, body, token)
    return post_comment(repo, pr_number, body, token)
