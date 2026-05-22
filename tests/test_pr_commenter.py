"""Tests for pr_commenter orchestration module."""

import pytest
from unittest.mock import patch, MagicMock
from src.pr_commenter import build_comment_body, run_pr_comment, COMMENT_MARKER


class TestBuildCommentBody:
    def test_contains_marker(self):
        body = build_comment_body({}, {}, {})
        assert COMMENT_MARKER in body

    def test_contains_mermaid_block(self):
        body = build_comment_body({"requests": "2.28.0"}, {}, {})
        assert "```mermaid" in body

    def test_added_package_in_summary(self):
        body = build_comment_body({"flask": "2.0.0"}, {}, {})
        assert "flask" in body
        assert "Added" in body

    def test_removed_package_in_summary(self):
        body = build_comment_body({}, {"django": "3.2.0"}, {})
        assert "django" in body
        assert "Removed" in body

    def test_changed_package_shows_versions(self):
        body = build_comment_body({}, {}, {"numpy": ("1.21.0", "1.24.0")})
        assert "numpy" in body
        assert "1.21.0" in body
        assert "1.24.0" in body

    def test_no_changes_message(self):
        body = build_comment_body({}, {}, {})
        assert "No dependency changes detected" in body

    def test_heading_present(self):
        body = build_comment_body({}, {}, {})
        assert "Dependency Graph Diff" in body


class TestRunPrComment:
    @patch("src.pr_commenter.upsert_comment")
    @patch("src.pr_commenter.parse_dependency_file")
    def test_calls_upsert_comment(self, mock_parse, mock_upsert):
        mock_parse.side_effect = [
            {"requests": "2.27.0"},
            {"requests": "2.28.0"},
        ]
        run_pr_comment("base.txt", "head.txt", "owner/repo", 42, "token123")
        mock_upsert.assert_called_once()
        args = mock_upsert.call_args[0]
        assert args[0] == "owner/repo"
        assert args[1] == 42
        assert args[2] == "token123"

    @patch("src.pr_commenter.upsert_comment")
    @patch("src.pr_commenter.parse_dependency_file")
    def test_body_passed_to_upsert(self, mock_parse, mock_upsert):
        mock_parse.side_effect = [{"flask": "1.0"}, {"flask": "2.0"}]
        run_pr_comment("base.txt", "head.txt", "owner/repo", 1, "tok")
        body_arg = mock_upsert.call_args[0][3]
        assert COMMENT_MARKER in body_arg
