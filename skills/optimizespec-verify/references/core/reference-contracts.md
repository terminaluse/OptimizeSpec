# Reference Contract Index

Use this index to load the smallest contract set needed for the current phase. These contracts are bundled inside each installed OptimizeSpec skill folder so the skill can run independently.

Core contracts are runtime-neutral. Runtime contracts live under references/runtimes/<runtime-id>/ and should be loaded only after repository inspection or existing artifacts identify the target runtime. If no runtime-specific reference exists, use the core contracts to design a repo-local adapter. Record the runtime assumptions, missing reference coverage, and contribution opportunity.

## Phase Loading

- Proposal or new-change work: load `references/core/criteria-first-evals.md`, `references/core/candidate-surface.md`, `references/core/grader-contract.md`, `references/core/eval-system-evidence.md`, and `references/core/live-eval-runner-contract.md` before drafting the eval primitive. Load runtime contracts only when repository evidence identifies the target runtime.
- Design work: load `references/core/live-eval-runner-contract.md`, `references/core/runner-contract.md`, `references/core/eval-system-evidence.md`, `references/core/grader-contract.md`, `references/core/asi-contract.md`, `references/core/candidate-surface.md`, `references/core/optimizer-contract.md`, `references/core/verification-contract.md`, and runtime contracts only for the inferred runtime.
- Apply work: load `references/core/live-eval-runner-contract.md`, `references/core/runner-contract.md`, `references/core/eval-system-evidence.md`, `references/core/grader-contract.md`, `references/core/asi-contract.md`, `references/core/candidate-surface.md`, `references/core/optimizer-contract.md`, `references/core/verification-contract.md`, and any runtime contracts or reference implementations that match the artifact runtime.
- Verify work: load `references/core/live-eval-runner-contract.md`, `references/core/eval-system-evidence.md`, `references/core/grader-contract.md`, `references/core/asi-contract.md`, `references/core/optimizer-contract.md`, `references/core/verification-contract.md`, and runtime-specific evidence expectations when applicable.

## Core Contracts

- `references/core/eval-system-evidence.md`: durable run ledger, candidate registry, scores, judge records, ASI, rollout artifacts, comparisons, optimizer lineage, leaderboard, and promotion decisions.
- `references/core/live-eval-runner-contract.md`: runtime-neutral live rollout contract, runner inputs, rollout record shape, lifecycle, path/config conventions, grading inputs, ASI, and optimizer requirements.
- `references/core/runner-contract.md`: direct eval, compare, optimize, show-candidate, command inputs and outputs, rollout lifecycle, and failure behavior.
- `references/core/grader-contract.md`: numeric scoring, qualitative judgment, grader type, calibration, reliability risks, and human review triggers.
- `references/core/asi-contract.md`: actionable side information shape, storage, field-specific feedback, and GEPA reflection handoff.
- `references/core/candidate-surface.md`: mutable candidate files or fields, candidate ids, diffs, rollback, and promotion boundaries.
- `references/core/optimizer-contract.md`: objective metric, diagnostics, guardrails, candidate selection, lineage, leaderboard, promotion, and rejection evidence.
- `references/core/verification-contract.md`: live checks, evidence inspection, runtime blockers, and release readiness.
- `references/core/gepa-reflection.md`: GEPA reflection setup, ASI handoff, mutable candidate fields, and optimizer configuration.
- `references/core/repo-patterns.md`: local adaptation patterns for reusing the target project code and dependency boundary.

## Runtime References

The included concrete runtime reference is Claude Managed Agents:

- `references/runtimes/claude-managed-agent/managed-agents-runtime-contract.md`: SDK/header setup, invocation assumptions, rollout records, and preview caveats.
- `references/runtimes/claude-managed-agent/managed-agents-runner.md`: Claude Managed Agents rollout lifecycle and runtime validation.
- `references/runtimes/claude-managed-agent/scorers-and-asi.md`: scorer templates and ASI expectations for Claude Managed Agents rollouts.
- `references/runtimes/claude-managed-agent/python-managed-agent-package/`: full runnable Python reference package with preview SDK requirements, live Managed Agents session runtime, evaluator, GEPA optimizer, CLI smoke command, and evidence-ledger writer. Treat it as one implementation of `references/core/live-eval-runner-contract.md`.

For other hosted agent runtimes or implementation languages, use the core contracts as the source of truth and create/adapt a runtime-specific adapter that calls the production agent's real tools, skills, MCP servers, environment configuration, and permissions. Contributions that add runtime references alongside `references/runtimes/claude-managed-agent/` are welcome.

## Review Questions

- Can a reviewer find which candidate version was evaluated for each case?
- Can a reviewer inspect per-case score, judge output when present, ASI, rollout evidence, and errors?
- Can a reviewer explain why the optimizer selected or rejected a candidate from live scores?
- Does verification distinguish system-loop success from agent-quality improvement?
