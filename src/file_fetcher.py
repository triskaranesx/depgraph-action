"""Fetch dependency files from GitHub at specific git refs."""

import base64
from typing import Optional

import urllib.request
import urllib.error
import json

GITHUB_API = "https://api.github.com"
KNOWN_DEPENDENCY_FILES = ["requirements.txt", "package.json", "Pipfile", "pyproject.toml"]


def get_headers(token: str) -> dict:
    """Return HTTP headers required for GitHub API requests."""
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def fetch_file_at_ref(repo: str, filepath: str, ref: str, token: str) -> Optional[str]:
    """Fetch the raw text content of a file at a specific git ref.

    Returns:
        Decoded file content as a string, or None if the file does not exist.

    Raises:
        RuntimeError: For unexpected HTTP errors (not 404).
    """
    url = f"{GITHUB_API}/repos/{repo}/contents/{filepath}?ref={ref}"
    req = urllib.request.Request(url, headers=get_headers(token))
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return base64.b64decode(data["content"]).decode("utf-8")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise RuntimeError(f"GitHub API error {exc.code} fetching {filepath}@{ref}") from exc


def detect_dependency_file(repo: str, ref: str, token: str) -> Optional[str]:
    """Return the first known dependency filename found in the repo at ref.

    Returns:
        Filename string (e.g. 'requirements.txt'), or None if none detected.
    """
    for candidate in KNOWN_DEPENDENCY_FILES:
        content = fetch_file_at_ref(repo, candidate, ref, token)
        if content is not None:
            return candidate
    return None


def fetch_base_and_head(
    repo: str, base_ref: str, head_ref: str, token: str
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Fetch dependency file contents for both base and head refs.

    Returns:
        A tuple of (filepath, base_content, head_content).  filepath is the
        detected dependency filename; either content may be None if the file
        does not exist at that ref.
    """
    filepath = detect_dependency_file(repo, head_ref, token) or detect_dependency_file(
        repo, base_ref, token
    )
    if filepath is None:
        return None, None, None
    base_content = fetch_file_at_ref(repo, filepath, base_ref, token)
    head_content = fetch_file_at_ref(repo, filepath, head_ref, token)
    return filepath, base_content, head_content
