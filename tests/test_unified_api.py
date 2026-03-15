"""
Unified API tests for KanJian.

Tests ToolResult, API functions, tools schema, dispatch, CLI flags, and package exports.
Following the unified test specification from Python multi-project development standards.
"""

import pytest
import json
import sys
import subprocess
from pathlib import Path


class TestToolResult:
    """Tests for ToolResult data class behavior."""

    def test_success_result(self):
        """Test ToolResult with success=True."""
        from kanjian.api import ToolResult

        r = ToolResult(success=True, data={"key": "value"}, metadata={"v": "1"})
        assert r.success is True
        assert r.data == {"key": "value"}
        assert r.error is None
        assert r.metadata == {"v": "1"}

    def test_failure_result(self):
        """Test ToolResult with success=False."""
        from kanjian.api import ToolResult

        r = ToolResult(success=False, error="something broke")
        assert r.success is False
        assert r.error == "something broke"
        assert r.data is None

    def test_to_dict(self):
        """Test ToolResult.to_dict() serialization."""
        from kanjian.api import ToolResult

        r = ToolResult(success=True, data=[1, 2], metadata={"x": 1})
        d = r.to_dict()
        assert set(d.keys()) == {"success", "data", "error", "metadata"}
        assert d["success"] is True
        assert d["data"] == [1, 2]

    def test_default_metadata_isolation(self):
        """Test that metadata defaults are not shared between instances."""
        from kanjian.api import ToolResult

        r1 = ToolResult(success=True)
        r2 = ToolResult(success=True)
        r1.metadata["a"] = 1
        assert "a" not in r2.metadata


class TestKanJianAPI:
    """Tests for kanjian.api module functions."""

    def test_simulate_magma_success(self):
        """Test kanjian_simulate with magma concept."""
        from kanjian.api import kanjian_simulate

        result = kanjian_simulate(concept="magma", steps=10)
        assert result.success is True
        assert result.data["concept"] == "magma"
        assert "version" in result.metadata

    def test_simulate_pythagorean_success(self):
        """Test kanjian_simulate with pythagorean concept."""
        from kanjian.api import kanjian_simulate

        result = kanjian_simulate(concept="pythagorean", params={"a": 3, "b": 4})
        assert result.success is True
        assert result.data["concept"] == "pythagorean"
        assert result.data["parameters"]["c"] == 5.0

    def test_simulate_unknown_concept(self):
        """Test kanjian_simulate with unknown concept."""
        from kanjian.api import kanjian_simulate

        result = kanjian_simulate(concept="unknown_concept")
        assert result.success is False
        assert "Unknown concept" in result.error

    def test_visualize_success(self):
        """Test kanjian_visualize generates image."""
        from kanjian.api import kanjian_visualize

        result = kanjian_visualize(concept="circle", params={"radius": 5})
        assert result.success is True
        assert "image_base64" in result.data or "concept_data" in result.data

    def test_visualize_with_output_path(self, tmp_path):
        """Test kanjian_visualize saves to file."""
        from kanjian.api import kanjian_visualize

        output_file = tmp_path / "test_viz.png"
        result = kanjian_visualize(
            concept="linear", params={"slope": 1, "intercept": 0}, output_path=str(output_file)
        )
        assert result.success is True
        assert result.data["file"] == str(output_file)
        assert output_file.exists()


class TestToolsSchema:
    """Tests for kanjian.tools TOOLS schema."""

    def test_tools_is_list(self):
        """Test TOOLS is a list with at least one tool."""
        from kanjian.tools import TOOLS

        assert isinstance(TOOLS, list)
        assert len(TOOLS) >= 2

    def test_tool_names(self):
        """Test tool names start with kanjian_ prefix."""
        from kanjian.tools import TOOLS

        for tool in TOOLS:
            name = tool["function"]["name"]
            assert name.startswith("kanjian_"), f"Tool name {name} should start with kanjian_"

    def test_tool_structure(self):
        """Test each tool has required structure."""
        from kanjian.tools import TOOLS

        for tool in TOOLS:
            assert tool["type"] == "function"
            func = tool["function"]
            assert "name" in func
            assert "description" in func
            assert "parameters" in func
            assert func["parameters"]["type"] == "object"
            assert "properties" in func["parameters"]
            assert "required" in func["parameters"]

    def test_required_fields_in_properties(self):
        """Test required fields exist in properties."""
        from kanjian.tools import TOOLS

        for tool in TOOLS:
            func = tool["function"]
            props = func["parameters"]["properties"]
            for req in func["parameters"]["required"]:
                assert req in props, f"Required '{req}' not in properties"


class TestToolsDispatch:
    """Tests for kanjian.tools dispatch function."""

    def test_dispatch_unknown_tool(self):
        """Test dispatch raises ValueError for unknown tool."""
        from kanjian.tools import dispatch

        with pytest.raises(ValueError, match="Unknown tool"):
            dispatch("nonexistent_tool", {})

    def test_dispatch_json_string_args(self):
        """Test dispatch with JSON string arguments."""
        from kanjian.tools import dispatch

        args = json.dumps({"concept": "magma", "steps": 5})
        result = dispatch("kanjian_simulate", args)
        assert isinstance(result, dict)
        assert "success" in result

    def test_dispatch_dict_args(self):
        """Test dispatch with dict arguments."""
        from kanjian.tools import dispatch

        args = {"concept": "pythagorean", "params": {"a": 3, "b": 4}}
        result = dispatch("kanjian_simulate", args)
        assert isinstance(result, dict)
        assert result["success"] is True

    def test_dispatch_error_case(self):
        """Test dispatch handles error cases."""
        from kanjian.tools import dispatch

        args = {"concept": "unknown_concept"}
        result = dispatch("kanjian_simulate", args)
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result


class TestCLIFlags:
    """Tests for CLI unified flags."""

    def _run_cli(self, *args):
        """Helper to run CLI with arguments."""
        return subprocess.run(
            [sys.executable, "-m", "kanjian"] + list(args),
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(Path(__file__).parent.parent / "src"),
        )

    def test_version_flag(self):
        """Test -V/--version flag."""
        r = self._run_cli("-V")
        assert r.returncode == 0
        assert "kanjian" in r.stdout.lower()

    def test_help_has_unified_flags(self):
        """Test --help shows unified flags."""
        r = self._run_cli("--help")
        assert r.returncode == 0
        assert "--json" in r.stdout
        assert "--quiet" in r.stdout or "-q" in r.stdout
        assert "--verbose" in r.stdout or "-v" in r.stdout
        assert "--version" in r.stdout or "-V" in r.stdout

    def test_simulate_help(self):
        """Test simulate subcommand help."""
        r = self._run_cli("simulate", "--help")
        assert r.returncode == 0
        assert "--concept" in r.stdout
        assert "--steps" in r.stdout

    def test_visualize_help(self):
        """Test visualize subcommand help."""
        r = self._run_cli("visualize", "--help")
        assert r.returncode == 0
        assert "--concept" in r.stdout
        assert "--param" in r.stdout


class TestPackageExports:
    """Tests for kanjian package exports."""

    def test_version(self):
        """Test __version__ is exported."""
        import kanjian

        assert hasattr(kanjian, "__version__")
        assert isinstance(kanjian.__version__, str)

    def test_toolresult(self):
        """Test ToolResult is exported."""
        from kanjian import ToolResult

        assert callable(ToolResult)

    def test_api_functions_exported(self):
        """Test API functions are exported."""
        from kanjian import kanjian_simulate, kanjian_visualize

        assert callable(kanjian_simulate)
        assert callable(kanjian_visualize)

    def test_all_exports(self):
        """Test __all__ contains expected exports."""
        import kanjian

        assert "ToolResult" in kanjian.__all__
        assert "kanjian_simulate" in kanjian.__all__
        assert "kanjian_visualize" in kanjian.__all__
        assert "__version__" in kanjian.__all__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
