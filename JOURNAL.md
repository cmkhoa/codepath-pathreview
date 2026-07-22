# Journal

## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/44

**Issue title:** Orchestrator catches all exceptions from tool calls and continues without logging the failure

**Tier:** [ ] Tier 1  [x] Tier 2  [ ] Tier 3

**Problem summary:**
The plan-execute loop in `agent/orchestrator.py` wraps every tool call in a broad `except Exception` block that swallows the error and moves on to the next step instead of surfacing it. When a tool invocation fails partway through a run, the orchestrator has no way to distinguish that failure from a normal empty result, so it produces a review with missing sections and gives the user no indication that anything went wrong. A successful fix would add proper error handling (likely tying into `agent/error_handling.py`) that logs the failure with enough context to debug it and either surfaces a partial-failure state to the user or fails the run loudly, rather than silently continuing.

**Branch name:** fix/44-orchestrator-silent-exception-handling

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger

## Week 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/cmkhoa/codepath-pathreview/commit/099ffd91df345191b84c021c19e4b2502cd62156

**Reproduction summary:**
Wrote `tests/unit/test_orchestrator.py`, instantiating `Orchestrator` with a real tool plus a tool that always raises. Confirmed `run()` returns normally with no exception and no top-level failure signal, and that the failed tool's `tool_results` entry (`{"error": ..., "success": False}`) has a completely different shape than a successful tool's entry, with nothing distinguishing the two without inspecting keys. Also found `_build_plan()` unconditionally queues `market_analyzer` even when it isn't registered in `self.tools`, hitting the same silent-swallow path via an `Unknown tool` error.

**PLAN.md link:** https://github.com/cmkhoa/codepath-pathreview/blob/fix/44-orchestrator-silent-exception-handling/PLAN.md

**Walkthrough video (recommended):** [not recorded]

**Blockers or open questions:**
Unsure whether the fix should make `run()` fail loud (raise) on total failure vs. always fail soft with a status field — leaning toward fail-soft, but want a mentor's take before committing to the API shape. Also need to decide whether failed tool results should still be persisted to `session_store`/`context_manager` as-is.
