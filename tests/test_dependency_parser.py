"""Unit tests for dependency_parser module."""

import pytest

from src.dependency_parser import (
    diff_dependencies,
    parse_dependency_file,
    parse_package_json,
    parse_requirements_txt,
)


REQUIREMENTS_SAMPLE = """
# This is a comment
requests==2.28.0
flask>=2.0
numpy
-r other.txt
"""

PACKAGE_JSON_SAMPLE = """{
  "dependencies": {"react": "^18.0.0", "axios": "^1.0.0"},
  "devDependencies": {"jest": "^29.0.0"}
}"""


class TestParseRequirementsTxt:
    def test_parses_pinned_version(self):
        deps = parse_requirements_txt("requests==2.28.0")
        assert "requests" in deps
        assert "==2.28.0" in deps["requests"]

    def test_skips_comments_and_flags(self):
        deps = parse_requirements_txt(REQUIREMENTS_SAMPLE)
        assert len(deps) == 3
        assert "requests" in deps
        assert "flask" in deps
        assert "numpy" in deps

    def test_package_without_version(self):
        deps = parse_requirements_txt("numpy")
        assert deps["numpy"] == set()

    def test_empty_file(self):
        assert parse_requirements_txt("") == {}


class TestParsePackageJson:
    def test_parses_all_sections(self):
        deps = parse_package_json(PACKAGE_JSON_SAMPLE)
        assert "react" in deps
        assert "axios" in deps
        assert "jest" in deps

    def test_missing_sections(self):
        deps = parse_package_json('{"name": "my-app"}')
        assert deps == {}


class TestParseDependencyFile:
    def test_dispatches_requirements(self):
        deps = parse_dependency_file("requirements.txt", "flask==2.0")
        assert "flask" in deps

    def test_dispatches_package_json(self):
        deps = parse_dependency_file("package.json", '{"dependencies": {"vue": "3"}}')
        assert "vue" in deps

    def test_unsupported_file_raises(self):
        with pytest.raises(ValueError, match="Unsupported"):
            parse_dependency_file("Gemfile", "gem 'rails'")


class TestDiffDependencies:
    def test_added(self):
        result = diff_dependencies({}, {"requests": {"==2.28.0"}})
        assert "requests" in result["added"]

    def test_removed(self):
        result = diff_dependencies({"flask": {"==2.0"}}, {})
        assert "flask" in result["removed"]

    def test_changed(self):
        result = diff_dependencies(
            {"numpy": {"==1.23"}}, {"numpy": {"==1.24"}}
        )
        assert "numpy" in result["changed"]

    def test_unchanged_not_reported(self):
        result = diff_dependencies({"scipy": {"==1.9"}}, {"scipy": {"==1.9"}})
        assert result == {"added": [], "removed": [], "changed": []}
