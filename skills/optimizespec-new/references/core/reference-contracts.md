# Reference Contract Index

Use this index to load the smallest contract set needed for the current phase. These contracts are bundled inside each installed OptimizeSpec skill folder so the skill can run independently.

Core contracts are runtime-neutral. Runtime contracts live under references/runtimes/<runtime-id>/ and should be loaded only after repository inspection or existing artifacts identify the target runtime. If runtime evidence is ambiguous, record the unknown or ask one focused clarification question instead of guessing an implementation path.

## Phase Loading

- Proposal or new-change work: load `references/core/criteria-first-evals.md`, `references/core/candidate-surface.md`, `references/core/grader-contract.md`, and `references/core/eval-system-evidence.md`.
- Design work: load `references/core/runner-contract.md`, `references/core/eval-system-evidence.md`, `references/core/grader-contract.md`, `references/core/asi-contract.md`, `references/core/candidate-surface.md`, `references/core/optimizer-contract.md`, `references/core/verification-contract.md`, and runtime contracts only for the inferred runtime.
- Apply work: load `references/core/runner-contract.md`, `references/core/eval-system-evidence.md`, `references/core/grader-contract.md`, `references/core/asi-contract.md`, `references/core/candidate-surface.md`, `references/core/optimizer-contract.md`, `references/core/verification-contract.md`, and the supported runtime contracts for the artifact runtime.
- Verify work: load `references/core/eval-system-evidence.md`, `references/core/grader-contract.md`, `references/core/asi-contract.md`, `references/core/optimizer-contract.md`, `references/core/verification-contract.md`, and runtime-specific evidence expectations when applicable.

## Core Contracts

- `references/core/eval-system-evidence.md`: durable run ledger, candidate registry, scores, judge records, ASI, rollout artifacts, comparisons, optimizer lineage, leaderboard, and promotion decisions.
- `references/core/runner-contract.md`: direct eval, compare, optimize, show-candidate, command inputs and outputs, rollout lifecycle, and failure behavior.
- `references/core/grader-contract.md`: numeric scoring, qualitative judgment, grader type, calibration, reliability risks, and human review triggers.
- `references/core/asi-contract.md`: actionable side information shape, storage, field-specific feedback, and GEPA reflection handoff.
- `references/core/candidate-surface.md`: mutable candidate files or fields, candidate ids, diffs, rollback, and promotion boundaries.
- `references/core/optimizer-contract.md`: objective metric, diagnostics, guardrails, candidate selection, lineage, leaderboard, promotion, and rejection evidence.
- `references/core/verification-contract.md`: deterministic smoke checks, live checks, evidence inspection, and release readiness.
- `references/core/gepa-reflection.md`: GEPA reflection setup, ASI handoff, mutable candidate fields, and optimizer configuration.
- `references/core/repo-patterns.md`: local adaptation patterns for reusing the target project code and dependency boundary.

## Runtime Contracts

Claude Managed Agents are the only v1 apply target:

- `references/runtimes/claude-managed-agent/managed-agents-runtime-contract.md`: SDK/header setup, invocation assumptions, rollout records, and preview caveats.
- `references/runtimes/claude-managed-agent/managed-agents-runner.md`: Claude Managed Agents rollout lifecycle and runtime validation.
- `references/runtimes/claude-managed-agent/scorers-and-asi.md`: scorer templates and ASI expectations for Claude Managed Agents rollouts.

## Review Questions

- Can a reviewer find which candidate version was evaluated for each case?
- Can a reviewer inspect per-case score, judge output when present, ASI, rollout evidence, and errors?
- Can a reviewer explain why the optimizer selected, rejected, or promoted a candidate?
- Does verification distinguish system-loop success from agent-quality improvement?
