"""Combines cache snapshots with diff logic to produce a structured report."""

from typing import Optional
from src.cache_manager import load_snapshot, save_snapshot
from src.dependency_parser import diff_dependencies
from src.graph_generator import generate_diff_graph, wrap_in_mermaid_block


def build_diff_report(
    repo: str,
    base_ref: str,
    head_ref: str,
    base_deps: dict,
    head_deps: dict,
    title: str = "Dependency Diff",
) -> dict:
    """Persist snapshots and return a structured diff report.

    Returns a dict with keys:
        - added: list of added package names
        - removed: list of removed package names
        - changed: list of (package, old_version, new_version) tuples
        - mermaid_block: fenced mermaid string ready for GitHub comment
    """
    save_snapshot(repo, base_ref, base_deps)
    save_snapshot(repo, head_ref, head_deps)

    diff = diff_dependencies(base_deps, head_deps)

    graph_md = wrap_in_mermaid_block(
        generate_diff_graph(base_deps, head_deps, title=title)
    )

    return {
        "added": diff.get("added", []),
        "removed": diff.get("removed", []),
        "changed": diff.get("changed", []),
        "mermaid_block": graph_md,
    }


def build_diff_report_from_cache(
    repo: str,
    base_ref: str,
    head_ref: str,
    head_deps: dict,
    title: str = "Dependency Diff",
) -> Optional[dict]:
    """Load base snapshot from cache; fall back to None if unavailable."""
    base_deps = load_snapshot(repo, base_ref)
    if base_deps is None:
        return None
    return build_diff_report(repo, base_ref, head_ref, base_deps, head_deps, title=title)
