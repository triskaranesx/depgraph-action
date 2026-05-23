"""Tests for snapshot_diff_reporter."""

import pytest
from unittest.mock import patch, MagicMock
from src.snapshot_diff_reporter import build_diff_report, build_diff_report_from_cache

BASE_DEPS = {"requests": "2.28.0", "flask": "2.2.0"}
HEAD_DEPS = {"requests": "2.31.0", "flask": "2.2.0", "click": "8.1.0"}
REPO = "owner/repo"
BASE_REF = "main"
HEAD_REF = "feature-branch"


@pytest.fixture(autouse=True)
def mock_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("DEPGRAPH_CACHE_DIR", str(tmp_path))


class TestBuildDiffReport:
    def test_returns_dict_with_expected_keys(self):
        report = build_diff_report(REPO, BASE_REF, HEAD_REF, BASE_DEPS, HEAD_DEPS)
        assert "added" in report
        assert "removed" in report
        assert "changed" in report
        assert "mermaid_block" in report

    def test_added_package_detected(self):
        report = build_diff_report(REPO, BASE_REF, HEAD_REF, BASE_DEPS, HEAD_DEPS)
        assert "click" in report["added"]

    def test_changed_package_detected(self):
        report = build_diff_report(REPO, BASE_REF, HEAD_REF, BASE_DEPS, HEAD_DEPS)
        changed_pkgs = [entry[0] for entry in report["changed"]]
        assert "requests" in changed_pkgs

    def test_no_removed_packages(self):
        report = build_diff_report(REPO, BASE_REF, HEAD_REF, BASE_DEPS, HEAD_DEPS)
        assert report["removed"] == []

    def test_mermaid_block_is_fenced(self):
        report = build_diff_report(REPO, BASE_REF, HEAD_REF, BASE_DEPS, HEAD_DEPS)
        assert report["mermaid_block"].startswith("```mermaid")
        assert report["mermaid_block"].strip().endswith("```")

    def test_custom_title_in_mermaid(self):
        report = build_diff_report(
            REPO, BASE_REF, HEAD_REF, BASE_DEPS, HEAD_DEPS, title="My Custom Title"
        )
        assert "My Custom Title" in report["mermaid_block"]


class TestBuildDiffReportFromCache:
    def test_returns_none_when_no_cached_base(self):
        result = build_diff_report_from_cache(REPO, "nonexistent-ref", HEAD_REF, HEAD_DEPS)
        assert result is None

    def test_returns_report_when_base_cached(self):
        # First, persist base snapshot via full build
        build_diff_report(REPO, BASE_REF, HEAD_REF, BASE_DEPS, HEAD_DEPS)
        # Now load from cache
        result = build_diff_report_from_cache(REPO, BASE_REF, HEAD_REF, HEAD_DEPS)
        assert result is not None
        assert "mermaid_block" in result

    def test_cached_report_added_matches(self):
        build_diff_report(REPO, BASE_REF, HEAD_REF, BASE_DEPS, HEAD_DEPS)
        result = build_diff_report_from_cache(REPO, BASE_REF, HEAD_REF, HEAD_DEPS)
        assert "click" in result["added"]
