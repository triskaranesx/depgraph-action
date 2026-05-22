"""Tests for the graph_generator module."""

import pytest
from src.graph_generator import generate_mermaid_graph, generate_diff_graph, wrap_in_mermaid_block


class TestGenerateMermaidGraph:
    def test_basic_graph_contains_package(self):
        deps = {"requests": "2.28.0"}
        result = generate_mermaid_graph(deps)
        assert "requests@2.28.0" in result

    def test_graph_starts_with_flowchart(self):
        result = generate_mermaid_graph({"flask": "2.0.0"})
        assert result.startswith("graph LR")

    def test_package_without_version(self):
        deps = {"some-lib": None}
        result = generate_mermaid_graph(deps)
        assert "some_lib[\"some-lib\"]" in result

    def test_custom_title_in_subgraph(self):
        result = generate_mermaid_graph({"numpy": "1.24.0"}, title="My Deps")
        assert '"My Deps"' in result

    def test_empty_dependencies(self):
        result = generate_mermaid_graph({})
        assert "graph LR" in result


class TestGenerateDiffGraph:
    def test_added_package_has_added_class(self):
        base = {}
        head = {"requests": "2.28.0"}
        result = generate_diff_graph(base, head)
        assert ":::added" in result
        assert "requests" in result

    def test_removed_package_has_removed_class(self):
        base = {"flask": "1.0.0"}
        head = {}
        result = generate_diff_graph(base, head)
        assert ":::removed" in result
        assert "flask" in result

    def test_changed_package_shows_version_transition(self):
        base = {"numpy": "1.23.0"}
        head = {"numpy": "1.24.0"}
        result = generate_diff_graph(base, head)
        assert ":::changed" in result
        assert "1.23.0" in result
        assert "1.24.0" in result

    def test_unchanged_package_has_unchanged_class(self):
        base = {"boto3": "1.26.0"}
        head = {"boto3": "1.26.0"}
        result = generate_diff_graph(base, head)
        assert ":::unchanged" in result

    def test_diff_graph_includes_classdefs(self):
        result = generate_diff_graph({}, {})
        assert "classDef added" in result
        assert "classDef removed" in result
        assert "classDef changed" in result

    def test_mixed_diff(self):
        base = {"requests": "2.27.0", "flask": "1.0.0"}
        head = {"requests": "2.28.0", "numpy": "1.24.0"}
        result = generate_diff_graph(base, head)
        assert ":::added" in result
        assert ":::removed" in result
        assert ":::changed" in result


class TestWrapInMermaidBlock:
    def test_wraps_with_mermaid_fence(self):
        graph = "graph LR\n    A[\"pkg\"]"
        result = wrap_in_mermaid_block(graph)
        assert result.startswith("```mermaid\n")
        assert result.endswith("\n```")

    def test_content_preserved(self):
        graph = "graph LR"
        result = wrap_in_mermaid_block(graph)
        assert graph in result
