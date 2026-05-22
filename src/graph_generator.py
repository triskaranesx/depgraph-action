"""Generates visual dependency graph representations using Mermaid syntax."""

from typing import Dict, Set, Optional
from src.dependency_parser import diff_dependencies


def generate_mermaid_graph(dependencies: Dict[str, Optional[str]], title: str = "Dependencies") -> str:
    """Generate a Mermaid flowchart from a flat dependency dict."""
    lines = ["graph LR", f'    subgraph "{title}"']
    for package, version in sorted(dependencies.items()):
        label = f"{package}@{version}" if version else package
        node_id = package.replace("-", "_").replace(".", "_")
        lines.append(f'        {node_id}["{label}"]')
    lines.append("    end")
    return "\n".join(lines)


def generate_diff_graph(base_deps: Dict[str, Optional[str]], head_deps: Dict[str, Optional[str]]) -> str:
    """Generate a Mermaid graph highlighting added, removed, and changed dependencies."""
    diff = diff_dependencies(base_deps, head_deps)

    added: Set[str] = set(diff.get("added", {}).keys())
    removed: Set[str] = set(diff.get("removed", {}).keys())
    changed: Set[str] = set(diff.get("changed", {}).keys())

    all_packages = set(base_deps.keys()) | set(head_deps.keys())

    lines = [
        "graph LR",
        "    classDef added fill:#d4edda,stroke:#28a745,color:#155724",
        "    classDef removed fill:#f8d7da,stroke:#dc3545,color:#721c24",
        "    classDef changed fill:#fff3cd,stroke:#ffc107,color:#856404",
        "    classDef unchanged fill:#f8f9fa,stroke:#6c757d,color:#343a40",
    ]

    for package in sorted(all_packages):
        node_id = package.replace("-", "_").replace(".", "_")

        if package in added:
            version = head_deps.get(package)
            label = f"{package}@{version}" if version else package
            lines.append(f'    {node_id}["{label}"]:::added')
        elif package in removed:
            version = base_deps.get(package)
            label = f"{package}@{version}" if version else package
            lines.append(f'    {node_id}["{label}"]:::removed')
        elif package in changed:
            old_ver = base_deps.get(package, "?")
            new_ver = head_deps.get(package, "?")
            label = f"{package}\n{old_ver} → {new_ver}"
            lines.append(f'    {node_id}["{label}"]:::changed')
        else:
            version = head_deps.get(package)
            label = f"{package}@{version}" if version else package
            lines.append(f'    {node_id}["{label}"]:::unchanged')

    return "\n".join(lines)


def wrap_in_mermaid_block(graph: str) -> str:
    """Wrap a Mermaid graph string in a markdown code block."""
    return f"```mermaid\n{graph}\n```"
