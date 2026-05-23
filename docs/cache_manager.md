# Cache Manager

The `cache_manager` module provides a lightweight, file-based caching layer for
dependency snapshots fetched from GitHub.  Caching avoids redundant API calls
when the same `(repo, ref, filepath)` triple is needed more than once during a
workflow run.

## Storage layout

All cache files are written to `.depgraph_cache/` in the current working
directory.  Each entry is a JSON file whose name is a 16-character SHA-256
prefix derived from the cache key:

```
.depgraph_cache/
  3a9f1c72b84e0d51.json
  c7e2a041f9b63d88.json
  ...
```

Each file contains:

```json
{
  "repo": "owner/repo",
  "ref": "main",
  "filepath": "requirements.txt",
  "deps": {
    "requests": "2.28.0",
    "flask": "2.3.1"
  }
}
```

## Public API

### `save_snapshot(repo, ref, filepath, deps)`

Persist a dependency dict to the cache.  Creates `.depgraph_cache/` if it does
not exist.  Overwrites any existing entry for the same key.

### `load_snapshot(repo, ref, filepath) -> dict | None`

Return the cached dependency dict, or `None` if no entry exists.

### `clear_cache() -> int`

Delete all `.json` files inside `.depgraph_cache/`.  Returns the number of
files removed.  Safe to call even when the directory does not exist.

## Usage example

```python
from cache_manager import save_snapshot, load_snapshot

deps = load_snapshot(repo, base_ref, filepath)
if deps is None:
    deps = fetch_and_parse(repo, base_ref, filepath)  # expensive API call
    save_snapshot(repo, base_ref, filepath, deps)
```

## Notes

- The cache is intentionally **ephemeral** — it persists only for the lifetime
  of a single GitHub Actions runner job.
- Add `.depgraph_cache/` to `.gitignore` to avoid accidentally committing
  cached data.
