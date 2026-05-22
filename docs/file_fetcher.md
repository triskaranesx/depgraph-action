# File Fetcher Module

The `src/file_fetcher.py` module is responsible for retrieving dependency files
from a GitHub repository at specific git refs (branches or commit SHAs) using
the GitHub Contents API.

## Public API

### `fetch_file_at_ref(repo, path, ref, token) -> str | None`

Fetches the raw text content of a single file from a GitHub repository.

- **repo**: Full repository name, e.g. `"owner/repo"`
- **path**: File path relative to repo root, e.g. `"requirements.txt"`
- **ref**: Git ref (branch name, tag, or commit SHA)
- **token**: GitHub personal access token or Actions token
- **Returns**: Decoded file content as a string, or `None` if the file is not found (HTTP 404).

### `detect_dependency_file(repo, ref, token) -> tuple[str, str] | tuple[None, None]`

Probes the repository for the first supported dependency file.
Currently supported (in priority order):

1. `requirements.txt`
2. `package.json`

- **Returns**: `(filename, content)` tuple, or `(None, None)` if no supported file exists.

### `fetch_base_and_head(repo, base_ref, head_ref, token) -> dict`

Convenience function used by the entrypoint to retrieve dependency file contents
for both sides of a pull request.

- **Returns** a dict with:
  - `filename` — detected dependency file name (or `None`)
  - `base_content` — file content at `base_ref` (empty string if absent)
  - `head_content` — file content at `head_ref`

## Supported Files

The list of supported dependency files is defined in `SUPPORTED_FILES` and can
be extended to support additional ecosystems (e.g. `Pipfile`, `pyproject.toml`).

## Error Handling

- A `404` response is treated as "file not present" and returns `None`.
- Any other HTTP error is re-raised so the caller can handle or surface it.
