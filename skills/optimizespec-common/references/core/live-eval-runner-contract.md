# Live Eval Runner Contract

This contract is the runtime-neutral source of truth for live agent optimization systems. Language packages under runtime references are implementations of this contract, not replacements for it.

## Eval Primitive

A rollout is one candidate evaluated on one eval case by executing the real agent runtime. For Claude Managed Agents, that means creating or selecting the Agent, Environment, and Session, sending the eval input through the Session, draining runtime events, collecting the final output or report, grading that live evidence, and writing a durable rollout record.

Live agent optimization requires real runtime rollouts. Static prompt, config, dry-run, fixture, and template-output checks belong outside eval modes. If real runtime access is unavailable, the runner must fail with a clear runtime blocker.

## Runner Inputs

Every runner invocation must accept or derive:

- Candidate id and candidate fields that compile into runtime behavior.
- Eval case id, live input, expected output behavior, expected trace behavior, and split.
- Run configuration, including run directory, output path, timeout, candidate budget, usage or cost limits, and live runtime mode.
- Credential and environment configuration, including required env vars, runtime beta/header settings, tool permissions, resource paths, and source fixture paths.
- Adapter configuration that tells the runner how to create or update the real agent, mount resources, send input, collect final output, and clean up runtime resources.

Path and import resolution must be explicit. Runners should work from the repo root, the optimization-system implementation folder, and CI by resolving candidate paths, eval-case paths, source fixtures, run outputs, credentials, and environment configuration from a known project root or explicit flags. The chosen optimization-system implementation location should normally be in the repo's eval, test, tooling, or agent package-adjacent surface. The location must include a concrete import/runtime access plan, such as running through the repo's package command, installing the project in editable mode, using the workspace's module resolution, or documenting the required module path.

## Rollout Record

The runner must emit a JSON-serializable rollout record with runtime-neutral top-level fields:

```json
{
  "candidate_id": "candidate-a",
  "eval_case_id": "case-1",
  "status": "completed|failed|timeout",
  "final_output": "...",
  "trace_summary": [],
  "tool_activity": [],
  "usage": {},
  "errors": [],
  "timeout": {
    "configured_seconds": 120,
    "timed_out": false,
    "interrupted": false
  },
  "cleanup": {
    "status": "completed|partial|skipped",
    "warnings": []
  },
  "timestamps": {
    "started_at": "...",
    "ended_at": "..."
  },
  "score_inputs": {
    "final_output_ref": "result.txt",
    "trace_ref": "rollout.json",
    "runtime_metadata_ref": "rollout.json#runtime_metadata"
  },
  "runtime_metadata": {}
}
```

Runtime-specific values belong under `runtime_metadata`. For Claude Managed Agents, that includes Agent id and version, Environment id, Session id and status, Managed Agents event types, beta/header assumptions, files and resources, generated file ids, resolved skills, callable agents, cleanup warnings, and SDK preview details.

Failed, interrupted, or timed-out rollouts must still be scoreable. Preserve partial final output, partial trace, error details, timeout/interrupt details, cleanup status, and a clear failure marker.

## Lifecycle Requirements

The runner must:

1. Load the candidate and eval case.
2. Compile mutable candidate fields into the real runtime surface.
3. Create or reuse runtime resources reproducibly.
4. Send the eval input through the real agent session.
5. Drain or poll runtime events until terminal evidence, timeout, failure, or a bounded settle period.
6. Capture the final output or report and trace evidence.
7. Grade the rollout record rather than prompt text.
8. Emit ASI grounded in observed output and trace failures.
9. Persist rollout, score, ASI, and summary records.
10. Clean up created resources or record cleanup warnings.

For event-stream runtimes, an idle event is not always sufficient. The runner should wait for required terminal evidence or a bounded settle period before finalizing evidence.

## Grading Inputs

Eval cases define both the live input sent to the agent and expected behavior. Output expectations are checked against the final output or report. Trace expectations are checked against event summaries, tool activity, runtime metadata, errors, usage, and cleanup details.

For BotVisibility-style cases, the grader should inspect the live report for required sections, effective denominator handling, CLI-only item handling, evidence-grounded limitations, unsupported claims, and trace-level fetch-budget behavior.

## ASI Requirements

ASI must include live `Input`, `Expected`, `Actual`, `Feedback`, `Error`, `Agent Trajectory`, `Runtime`, `scores`, and field-specific feedback for mutable fields. Runtime setup failures such as missing credentials, permissions, environment configuration, timeout, SDK preview mismatch, or cleanup failure must be separated from candidate-quality feedback.

## Optimizer Requirements

The optimizer must evaluate candidates through the live runner and live grader. It should mutate only fields that compile into future live behavior, use live ASI to propose targeted changes, and report the best candidate by live score with per-case scores, lineage, budgets, and evidence locations. Promotion or release decisions may exist outside the loop, but they are not required for the core live optimization loop.
