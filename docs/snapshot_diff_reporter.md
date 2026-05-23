# snapshot_diff_reporter

## Overview

`src/snapshot_diff_reporter.py` bridges the cache layer, diff logic, and graph
generation into a single, convenient API used by the action entrypoint.

## Functions

### `build_diff_report(repo, base_ref, head_ref, base_deps, head_deps, title)`

Persists both dependency snapshots to the cache, computes the diff, and returns
a structured report dictionary.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `repo` | `str` | Repository slug, e.g. `"owner/repo"` |
| `base_ref` | `str` | Git ref for the base (target) branch |
| `head_ref` | `str` | Git ref for the head (PR) branch |
| `base_deps` | `dict` | Parsed dependencies from the base ref |
| `head_deps` | `dict` | Parsed dependencies from the head ref |
| `title` | `str` | Optional graph title (default: `"Dependency Diff"`) |

**Returns** `dict` with keys:

- `added` — list of newly added package names
- `removed` — list of removed package names
- `changed` — list of `(package, old_version, new_version)` tuples
- `mermaid_block` — fenced Mermaid markdown string

---

### `build_diff_report_from_cache(repo, base_ref, head_ref, head_deps, title)`

Attempts to load the base snapshot from the local cache. If the snapshot does
not exist, returns `None` so the caller can fall back to fetching from GitHub.

**Returns** same structure as `build_diff_report`, or `None`.

## Usage Example

```python
from src.snapshot_diff_reporter import build_diff_report

report = build_diff_report(
    repo="acme/my-service",
    base_ref="main",
    head_ref="feat/upgrade-deps",
    base_deps={"requests": "2.28.0"},
    head_deps={"requests": "2.31.0", "httpx": "0.24.0"},
)

print(report["added"])    # ['httpx']
print(report["changed"])  # [('requests', '2.28.0', '2.31.0')]
print(report["mermaid_block"])
```

## Dependencies

- `src.cache_manager` — `save_snapshot`, `load_snapshot`
- `src.dependency_parser` — `diff_dependencies`
- `src.graph_generator` — `generate_diff_graph`, `wrap_in_mermaid_block`
