"""Tests for orchestrator.py

These tests document issue #44: the plan-execute loop in `Orchestrator.run()`
wraps each tool call in a broad `except Exception` and silently continues,
so a failing tool never surfaces as a run-level failure and produces a
`tool_results` entry with a different shape than a successful one.
"""

import pytest

from agent.orchestrator import Orchestrator
from agent.tools.base import BaseTool, ToolResult
from agent.tools.tech_detector import TechDetector


class AlwaysFailsTool(BaseTool):
    """Simulates a tool whose upstream dependency (e.g. GitHub API) fails."""

    name = "readme_scorer"
    description = "Intentionally broken tool for reproducing issue #44"

    def execute(self, input_data: dict) -> ToolResult:
        raise RuntimeError("simulated upstream API failure (e.g. GitHub 500)")


@pytest.mark.unit
class TestOrchestratorSwallowsToolExceptions:
    """Reproduces issue #44."""

    def test_run_does_not_raise_when_a_tool_fails(self) -> None:
        """`run()` completes normally even though a tool raised every retry."""
        orchestrator = Orchestrator(
            tools={
                "tech_detector": TechDetector(),
                "readme_scorer": AlwaysFailsTool(),
            }
        )

        # Should not raise -- this is the bug. A failing tool should not be
        # silently absorbed into a "successful" run.
        output = orchestrator.run(
            profile_id="profile-123",
            profile_data={
                "files": ["main.py", "package.json"],
                "readme_content": "# My Project",
            },
        )

        assert output["profile_id"] == "profile-123"

    def test_failed_tool_result_has_no_run_level_signal(self) -> None:
        """There is no top-level flag indicating a partial failure occurred.

        A caller building a review from `tool_results` has no way to detect
        that `readme_scorer` failed without inspecting every entry's shape.
        """
        orchestrator = Orchestrator(
            tools={
                "tech_detector": TechDetector(),
                "readme_scorer": AlwaysFailsTool(),
            }
        )

        output = orchestrator.run(
            profile_id="profile-123",
            profile_data={
                "files": ["main.py"],
                "readme_content": "# My Project",
            },
        )

        # Bug: nothing at the top level says "a tool failed".
        assert set(output.keys()) == {"profile_id", "tool_results", "cached_results"}

        # Bug: the failed tool's entry has an entirely different shape
        # (error/success keys) than a successful tool's entry (tool-specific
        # data keys), with nothing to distinguish them without probing.
        failed_result = output["tool_results"]["readme_scorer"]
        succeeded_result = output["tool_results"]["tech_detector"]

        assert failed_result == {
            "error": "simulated upstream API failure (e.g. GitHub 500)",
            "success": False,
        }
        assert "error" not in succeeded_result

    def test_plan_queues_unregistered_market_analyzer_tool(self) -> None:
        """`_build_plan` always appends `market_analyzer` whenever any other
        tool ran, even if it isn't registered in `self.tools` -- this hits
        the exact same silent-failure path via `ValueError("Unknown tool")`.
        """
        orchestrator = Orchestrator(tools={"tech_detector": TechDetector()})

        output = orchestrator.run(
            profile_id="profile-456",
            profile_data={"files": ["main.py"]},
        )

        assert output["tool_results"]["market_analyzer"] == {
            "error": "Unknown tool: market_analyzer",
            "success": False,
        }
