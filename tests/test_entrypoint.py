"""Tests for the entrypoint module."""

import pytest
import sys
from unittest.mock import patch, MagicMock


class TestGetRequiredEnv:
    def test_returns_value_when_set(self, monkeypatch):
        monkeypatch.setenv("MY_VAR", "hello")
        from src.entrypoint import get_required_env
        assert get_required_env("MY_VAR") == "hello"

    def test_exits_when_missing(self, monkeypatch):
        monkeypatch.delenv("MISSING_VAR", raising=False)
        from src.entrypoint import get_required_env
        with pytest.raises(SystemExit):
            get_required_env("MISSING_VAR")

    def test_exits_when_empty(self, monkeypatch):
        monkeypatch.setenv("EMPTY_VAR", "   ")
        from src.entrypoint import get_required_env
        with pytest.raises(SystemExit):
            get_required_env("EMPTY_VAR")


class TestMain:
    def _set_env(self, monkeypatch, overrides=None):
        defaults = {
            "GITHUB_TOKEN": "tok",
            "GITHUB_REPOSITORY": "owner/repo",
            "PR_NUMBER": "7",
            "BASE_DEP_FILE": "base.txt",
            "HEAD_DEP_FILE": "head.txt",
        }
        if overrides:
            defaults.update(overrides)
        for k, v in defaults.items():
            monkeypatch.setenv(k, v)

    @patch("src.pr_commenter.run_pr_comment")
    def test_main_calls_run_pr_comment(self, mock_run, monkeypatch, tmp_path):
        base = tmp_path / "base.txt"
        head = tmp_path / "head.txt"
        base.write_text("requests==2.27.0\n")
        head.write_text("requests==2.28.0\n")
        self._set_env(monkeypatch, {"BASE_DEP_FILE": str(base), "HEAD_DEP_FILE": str(head)})
        from src.entrypoint import main
        main()
        mock_run.assert_called_once_with(str(base), str(head), "owner/repo", 7, "tok")

    def test_main_exits_on_invalid_pr_number(self, monkeypatch, tmp_path):
        base = tmp_path / "base.txt"
        head = tmp_path / "head.txt"
        base.write_text("")
        head.write_text("")
        self._set_env(monkeypatch, {"PR_NUMBER": "not-a-number", "BASE_DEP_FILE": str(base), "HEAD_DEP_FILE": str(head)})
        from src.entrypoint import main
        with pytest.raises(SystemExit):
            main()

    def test_main_exits_when_file_missing(self, monkeypatch):
        self._set_env(monkeypatch, {"BASE_DEP_FILE": "/nonexistent/base.txt", "HEAD_DEP_FILE": "/nonexistent/head.txt"})
        from src.entrypoint import main
        with pytest.raises(SystemExit):
            main()
