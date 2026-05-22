"""Parse dependency files and extract package dependencies."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Set


DependencyMap = Dict[str, Set[str]]


def parse_requirements_txt(content: str) -> DependencyMap:
    """Parse a requirements.txt file and return a dict of package -> versions."""
    deps: DependencyMap = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        match = re.match(r"^([A-Za-z0-9_\-\.]+)([=<>!~].+)?$", line)
        if match:
            name = match.group(1).lower()
            version = match.group(2) or ""
            deps[name] = {version.strip()} if version else set()
    return deps


def parse_package_json(content: str) -> DependencyMap:
    """Parse a package.json file and return combined dependencies."""
    data = json.loads(content)
    deps: DependencyMap = {}
    for section in ("dependencies", "devDependencies", "peerDependencies"):
        for name, version in data.get(section, {}).items():
            deps[name] = {version}
    return deps


def parse_dependency_file(file_path: str, content: str) -> DependencyMap:
    """Dispatch to the correct parser based on file name."""
    name = Path(file_path).name.lower()
    if name == "requirements.txt":
        return parse_requirements_txt(content)
    if name == "package.json":
        return parse_package_json(content)
    raise ValueError(f"Unsupported dependency file: {file_path}")


def diff_dependencies(
    before: DependencyMap, after: DependencyMap
) -> dict[str, list[str]]:
    """Compute added, removed, and changed dependencies between two snapshots."""
    before_keys = set(before)
    after_keys = set(after)

    added = sorted(after_keys - before_keys)
    removed = sorted(before_keys - after_keys)
    changed = [
        pkg
        for pkg in before_keys & after_keys
        if before[pkg] != after[pkg]
    ]

    return {"added": added, "removed": removed, "changed": sorted(changed)}
