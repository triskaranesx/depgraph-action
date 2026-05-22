"""Orchestrates the full PR comment flow: parse, diff, generate graph, and comment."""

import os
from .dependency_parser import parse_dependency_file, diff_dependencies
from .graph_generator import generate_diff_graph, wrap_in_mermaid_block
from .github_commenter import upsert_comment

COMMENT_MARKER = "<!-- depgraph-action -->"


def build_comment_body(added: dict, removed: dict, changed: dict) -> str:
    """Build the full markdown comment body with graph and summary table."""
    graph = generate_diff_graph(added, removed, changed)
    mermaid_block = wrap_in_mermaid_block(graph)

    lines = [
        COMMENT_MARKER,
        "## 📦 Dependency Graph Diff",
        "",
        mermaid_block,
        "",
        "### Summary",
        "",
        "| Change | Package | Version |",
        "|--------|---------|---------|`,
    ]

    for pkg, ver in sorted(added.items()):
        lines.append(f"| ➕ Added | `{pkg}` | `{ver or 'unspecified'}` |")
    for pkg, ver in sorted(removed.items()):
        lines.append(f"| ➖ Removed | `{pkg}` | `{ver or 'unspecified'}` |")
    for pkg, (old_ver, new_ver) in sorted(changed.items()):
        lines.append(f"| 🔄 Changed | `{pkg}` | `{old_ver}` → `{new_ver}` |")

    if not added and not removed and not changed:
        lines.append("| — | No dependency changes detected | — |")

    return "\n".join(lines)


def run_pr_comment(base_file: str, head_file: str, repo: str, pr_number: int, token: str) -> None:
    """Main entry point: diff two dependency files and upsert a PR comment."""
    base_deps = parse_dependency_file(base_file)
    head_deps = parse_dependency_file(head_file)

    added, removed, changed = diff_dependencies(base_deps, head_deps)
    body = build_comment_body(added, removed, changed)
    upsert_comment(repo, pr_number, token, body, COMMENT_MARKER)
