"""GitHub Action entrypoint — reads environment variables and triggers the PR comment flow."""

import os
import sys


def get_required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"[depgraph-action] ERROR: Required environment variable '{name}' is not set.", file=sys.stderr)
        sys.exit(1)
    return value


def main() -> None:
    print("[depgraph-action] Starting dependency graph diff...")

    token = get_required_env("GITHUB_TOKEN")
    repo = get_required_env("GITHUB_REPOSITORY")
    pr_number_str = get_required_env("PR_NUMBER")
    base_file = os.environ.get("BASE_DEP_FILE", "base_requirements.txt")
    head_file = os.environ.get("HEAD_DEP_FILE", "requirements.txt")

    try:
        pr_number = int(pr_number_str)
    except ValueError:
        print(f"[depgraph-action] ERROR: PR_NUMBER must be an integer, got '{pr_number_str}'.", file=sys.stderr)
        sys.exit(1)

    for path in (base_file, head_file):
        if not os.path.isfile(path):
            print(f"[depgraph-action] ERROR: Dependency file not found: '{path}'.", file=sys.stderr)
            sys.exit(1)

    from src.pr_commenter import run_pr_comment
    run_pr_comment(base_file, head_file, repo, pr_number, token)

    print("[depgraph-action] Done. PR comment upserted successfully.")


if __name__ == "__main__":
    main()
