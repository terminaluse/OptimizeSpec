---
name: optimizespec-common
description: Shared OptimizeSpec self-improvement references and templates. Use only as a supporting skill when another OptimizeSpec skill needs workflow, ASI, Claude Managed Agents, scorer, or runner reference material.
---

# OptimizeSpec Common

Do not use this as the primary user-facing workflow. Use it as a shared reference bundle for:

- `optimizespec-new`
- `optimizespec-continue`
- `optimizespec-apply`
- `optimizespec-verify`

## Reference Loading

Load `references/reference-contracts.md` first when a phase skill needs shared OptimizeSpec system expectations. It explains which smaller contracts to load for proposal, design, apply, and verify work.

Keep loading progressive: use only the references needed for the current phase, and cite the contract names in generated artifacts instead of copying long contract prose into user-facing documents.

## References

- `references/workflow.md`: OpenSpec-inspired artifact flow and directory convention.
- `references/reference-contracts.md`: index of shared reference contracts and phase-specific loading rules.
- `references/criteria-first-evals.md`: lightweight criteria-first eval design, grader trust, and optimizer acceptance.
- `references/eval-system-evidence.md`: durable evidence ledger for run manifests, candidate registry, per-case scores, judge output, ASI, rollouts, optimizer lineage, and promotion decisions.
- `references/runner-contract.md`: direct eval, compare, optimize, show-candidate, verify commands, rollout lifecycle, command IO, and failure behavior.
- `references/grader-contract.md`: numeric scores, qualitative judgment, grader type, calibration, reliability risks, and human review triggers.
- `references/asi-contract.md`: Actionable Side Information shape, persistence, field-specific feedback, and GEPA reflection handoff.
- `references/candidate-surface.md`: mutable fields or files, candidate ids, diffs, rollback, immutable eval inputs, and promotion boundaries.
- `references/optimizer-contract.md`: objective metric, diagnostics, guardrails, candidate selection, lineage, leaderboard, promotion, and rejection evidence.
- `references/managed-agents-runtime-contract.md`: Claude Managed Agents SDK/header setup, invocation assumptions, rollout records, and preview caveats.
- `references/verification-contract.md`: deterministic and live readiness checks that inspect emitted evidence.
- `references/gepa-reflection.md`: GEPA reflective evolution, ASI, candidate fields, and optimizer configuration.
- `references/managed-agents-runner.md`: Claude Managed Agents rollout lifecycle.
- `references/scorers-and-asi.md`: scorer templates and ASI shape.
- `references/repo-patterns.md`: local `optimizespec` prototype patterns to adapt.

## Assets

- `assets/templates/`: proposal, design, spec, task, eval case, and candidate templates.
- `assets/python_runner/agent_self_improve.py`: portable runner/optimizer implementation template for agent projects.

Load only the specific reference or asset needed for the current task.
