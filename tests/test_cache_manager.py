"""Tests for src/cache_manager.py"""

import json
import os
import pytest

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import cache_manager as cm


REPO = "owner/repo"
REF_BASE = "main"
REF_HEAD = "feature-branch"
FILEPATH = "requirements.txt"
SAMPLE_DEPS = {"requests": "2.28.0", "flask": "2.3.1"}


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    """Redirect cache dir to a temp directory for each test."""
    monkeypatch.setattr(cm, "CACHE_DIR", str(tmp_path / ".depgraph_cache"))
    yield


class TestSaveAndLoadSnapshot:
    def test_roundtrip_returns_same_deps(self):
        cm.save_snapshot(REPO, REF_BASE, FILEPATH, SAMPLE_DEPS)
        result = cm.load_snapshot(REPO, REF_BASE, FILEPATH)
        assert result == SAMPLE_DEPS

    def test_different_refs_are_independent(self):
        cm.save_snapshot(REPO, REF_BASE, FILEPATH, {"a": "1.0"})
        cm.save_snapshot(REPO, REF_HEAD, FILEPATH, {"b": "2.0"})
        assert cm.load_snapshot(REPO, REF_BASE, FILEPATH) == {"a": "1.0"}
        assert cm.load_snapshot(REPO, REF_HEAD, FILEPATH) == {"b": "2.0"}

    def test_missing_entry_returns_none(self):
        result = cm.load_snapshot(REPO, "nonexistent", FILEPATH)
        assert result is None

    def test_overwrite_updates_value(self):
        cm.save_snapshot(REPO, REF_BASE, FILEPATH, {"x": "1.0"})
        cm.save_snapshot(REPO, REF_BASE, FILEPATH, {"x": "9.9"})
        assert cm.load_snapshot(REPO, REF_BASE, FILEPATH) == {"x": "9.9"}

    def test_cache_file_is_valid_json(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cm, "CACHE_DIR", str(tmp_path / ".depgraph_cache"))
        cm.save_snapshot(REPO, REF_BASE, FILEPATH, SAMPLE_DEPS)
        cache_dir = tmp_path / ".depgraph_cache"
        files = list(cache_dir.glob("*.json"))
        assert len(files) == 1
        with open(files[0]) as fh:
            data = json.load(fh)
        assert data["deps"] == SAMPLE_DEPS


class TestClearCache:
    def test_clear_removes_all_files(self):
        cm.save_snapshot(REPO, REF_BASE, FILEPATH, SAMPLE_DEPS)
        cm.save_snapshot(REPO, REF_HEAD, FILEPATH, SAMPLE_DEPS)
        removed = cm.clear_cache()
        assert removed == 2

    def test_clear_on_empty_dir_returns_zero(self):
        assert cm.clear_cache() == 0

    def test_clear_makes_load_return_none(self):
        cm.save_snapshot(REPO, REF_BASE, FILEPATH, SAMPLE_DEPS)
        cm.clear_cache()
        assert cm.load_snapshot(REPO, REF_BASE, FILEPATH) is None

    def test_clear_when_no_cache_dir_returns_zero(self):
        # cache dir was never created
        result = cm.clear_cache()
        assert result == 0
