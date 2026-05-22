import os
import base64
import urllib.request
import urllib.error
import json

SUPPORTED_FILES = ["requirements.txt", "package.json"]


def get_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "depgraph-action",
    }


def fetch_file_at_ref(repo: str, path: str, ref: str, token: str) -> str | None:
    """
    Fetch the raw content of a file from a GitHub repo at a given ref (branch/SHA).
    Returns the decoded string content, or None if the file does not exist.
    """
    url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={ref}"
    req = urllib.request.Request(url, headers=get_headers(token))
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            if data.get("encoding") == "base64":
                return base64.b64decode(data["content"]).decode("utf-8")
            return data.get("content", "")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def detect_dependency_file(repo: str, ref: str, token: str) -> tuple[str, str] | tuple[None, None]:
    """
    Detect the first supported dependency file in the repo at the given ref.
    Returns a (filename, content) tuple, or (None, None) if none found.
    """
    for filename in SUPPORTED_FILES:
        content = fetch_file_at_ref(repo, filename, ref, token)
        if content is not None:
            return filename, content
    return None, None


def fetch_base_and_head(repo: str, base_ref: str, head_ref: str, token: str) -> dict:
    """
    Fetch dependency file contents for both base and head refs.
    Returns a dict with keys: filename, base_content, head_content.
    """
    filename, head_content = detect_dependency_file(repo, head_ref, token)
    if filename is None:
        return {"filename": None, "base_content": "", "head_content": ""}

    base_content = fetch_file_at_ref(repo, filename, base_ref, token) or ""
    return {
        "filename": filename,
        "base_content": base_content,
        "head_content": head_content,
    }
