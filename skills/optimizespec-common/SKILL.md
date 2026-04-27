---
name: optimizespec-common
description: Shared OptimizeSpec self-improvement references and templates. Use only as a supporting skill when another OptimizeSpec skill needs workflow, ASI, scorer, runner, or runtime-specific reference material.
---

# OptimizeSpec Common

This skill is a shared reference bundle for:

- `optimizespec-new`
- `optimizespec-continue`
- `optimizespec-apply`
- `optimizespec-verify`

## Reference Loading

Load `references/core/reference-contracts.md` first when a phase skill needs shared OptimizeSpec system expectations. It explains which smaller core contracts to load for proposal, design, apply, and verify work, and when to load runtime-specific contracts such as `references/runtimes/claude-managed-agent/`.

Keep loading progressive: use only the references needed for the current phase, infer the target runtime from repo inspection when possible, and cite contract names in generated artifacts while summarizing only the details the user needs.

## References

- `references/core/workflow.md`: OpenSpec-inspired artifact flow and directory convention.
- `references/core/reference-contracts.md`: index of shared reference contracts and phase-specific loading rules.
- `references/core/criteria-first-evals.md`: lightweight criteria-first eval design, grader trust, and optimizer acceptance.
- `references/core/eval-system-evidence.md`: durable evidence ledger for run manifests, candidate registry, per-case scores, judge output, ASI, rollouts, optimizer lineage, and promotion decisions.
- `references/core/live-eval-runner-contract.md`: runtime-neutral live rollout contract for runner inputs, rollout records, lifecycle, path/config resolution, live grading, ASI, and optimizer scoring.
- `references/core/runner-contract.md`: direct eval, compare, optimize, show-candidate, verify commands, rollout lifecycle, command IO, and failure behavior.
- `references/core/grader-contract.md`: numeric scores, qualitative judgment, grader type, calibration, reliability risks, and human review triggers.
- `references/core/asi-contract.md`: Actionable Side Information shape, persistence, field-specific feedback, and GEPA reflection handoff.
- `references/core/candidate-surface.md`: mutable fields or files, candidate ids, diffs, rollback, immutable eval inputs, and promotion boundaries.
- `references/core/optimizer-contract.md`: objective metric, diagnostics, guardrails, candidate selection, lineage, leaderboard, promotion, and rejection evidence.
- `references/runtimes/claude-managed-agent/managed-agents-runtime-contract.md`: Claude Managed Agents SDK/header setup, invocation assumptions, rollout records, and preview caveats.
- `references/core/verification-contract.md`: deterministic and live readiness checks that inspect emitted evidence.
- `references/core/gepa-reflection.md`: GEPA reflective evolution, ASI, candidate fields, and optimizer configuration.
- `references/runtimes/claude-managed-agent/managed-agents-runner.md`: Claude Managed Agents rollout lifecycle.
- `references/runtimes/claude-managed-agent/scorers-and-asi.md`: scorer templates and ASI shape.
- `references/runtimes/claude-managed-agent/python-managed-agent-package/`: full runnable Python Managed Agents reference package with preview SDK requirements, live session runtime, evaluator, GEPA optimizer, CLI smoke command, and evidence-ledger writer.
- `references/core/repo-patterns.md`: repo adaptation patterns for production-equivalent optimization systems.

## Assets

- `assets/templates/`: proposal, design, spec, task, eval case, and candidate templates.

Load only the specific reference or asset needed for the current task.
