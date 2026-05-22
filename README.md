# depgraph-action

> GitHub Action that generates and comments a visual dependency graph diff on pull requests.

## Installation

```yaml
- uses: your-org/depgraph-action@v1
```

No additional installation required — runs directly in your GitHub Actions workflow.

## Usage

Add the following step to your pull request workflow:

```yaml
name: Dependency Graph Diff

on:
  pull_request:
    branches: [main]

jobs:
  depgraph:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - uses: your-org/depgraph-action@v1
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          requirements-file: requirements.txt
```

The action will automatically generate a visual diff of your dependency graph and post it as a comment on the pull request, highlighting added, removed, and changed packages.

### Inputs

| Input | Description | Default |
|---|---|---|
| `token` | GitHub token for posting comments | `${{ secrets.GITHUB_TOKEN }}` |
| `requirements-file` | Path to the requirements file | `requirements.txt` |
| `format` | Output format (`png`, `svg`) | `svg` |

### Example Output

The action posts a comment containing a rendered dependency graph diff, with color-coded nodes indicating:
- 🟢 **Green** — newly added dependencies
- 🔴 **Red** — removed dependencies
- 🟡 **Yellow** — version-changed dependencies

## License

MIT © your-org