"""Cache manager for storing and retrieving dependency snapshots."""

import json
import os
import hashlib
from typing import Optional

CACHE_DIR = ".depgraph_cache"


def _ensure_cache_dir() -> None:
    """Create cache directory if it doesn't exist."""
    os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_key(repo: str, ref: str, filepath: str) -> str:
    """Generate a stable cache key from repo, ref, and filepath."""
    raw = f"{repo}:{ref}:{filepath}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _cache_path(key: str) -> str:
    """Return the full path to a cache file."""
    return os.path.join(CACHE_DIR, f"{key}.json")


def save_snapshot(repo: str, ref: str, filepath: str, deps: dict) -> None:
    """Persist a dependency snapshot to the local cache.

    Args:
        repo: Repository full name (e.g. 'owner/repo').
        ref: Git ref (branch, tag, or commit SHA).
        filepath: Path to the dependency file inside the repo.
        deps: Parsed dependency dict to cache.
    """
    _ensure_cache_dir()
    key = _cache_key(repo, ref, filepath)
    with open(_cache_path(key), "w") as fh:
        json.dump({"repo": repo, "ref": ref, "filepath": filepath, "deps": deps}, fh)


def load_snapshot(repo: str, ref: str, filepath: str) -> Optional[dict]:
    """Load a previously cached dependency snapshot.

    Returns:
        The cached deps dict, or None if no cache entry exists.
    """
    key = _cache_key(repo, ref, filepath)
    path = _cache_path(key)
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        data = json.load(fh)
    return data.get("deps")


def clear_cache() -> int:
    """Remove all cache files.

    Returns:
        Number of files deleted.
    """
    if not os.path.isdir(CACHE_DIR):
        return 0
    count = 0
    for fname in os.listdir(CACHE_DIR):
        if fname.endswith(".json"):
            os.remove(os.path.join(CACHE_DIR, fname))
            count += 1
    return count
