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
