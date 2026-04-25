# Reference Contract Index

Use this index to load the smallest contract set needed for the current phase. The contracts are shared sources of truth for OptimizeSpec systems; phase skills should cite them rather than duplicating their full contents.

## Phase Loading

- Proposal or new-change work: load `criteria-first-evals.md`, `candidate-surface.md`, `grader-contract.md`, and `eval-system-evidence.md`.
- Design work: load `runner-contract.md`, `eval-system-evidence.md`, `grader-contract.md`, `asi-contract.md`, `candidate-surface.md`, `optimizer-contract.md`, `managed-agents-runtime-contract.md`, and `verification-contract.md`.
- Apply work: load `runner-contract.md`, `eval-system-evidence.md`, `grader-contract.md`, `asi-contract.md`, `optimizer-contract.md`, `managed-agents-runtime-contract.md`, and `verification-contract.md`.
- Verify work: load `eval-system-evidence.md`, `grader-contract.md`, `asi-contract.md`, `optimizer-contract.md`, and `verification-contract.md`.

## Contracts

- `eval-system-evidence.md`: durable run ledger, candidate registry, scores, judge records, ASI, rollout artifacts, comparisons, optimizer lineage, leaderboard, and promotion decisions.
- `runner-contract.md`: direct eval, compare, optimize, show-candidate, command inputs and outputs, rollout lifecycle, and failure behavior.
- `grader-contract.md`: numeric scoring, qualitative judgment, grader type, calibration, reliability risks, and human review triggers.
- `asi-contract.md`: actionable side information shape, storage, field-specific feedback, and GEPA reflection handoff.
- `candidate-surface.md`: mutable candidate files or fields, candidate ids, diffs, rollback, and promotion boundaries.
- `optimizer-contract.md`: objective metric, diagnostics, guardrails, candidate selection, lineage, leaderboard, promotion, and rejection evidence.
- `managed-agents-runtime-contract.md`: Claude Managed Agents SDK/header setup, invocation assumptions, rollout records, and preview caveats.
- `verification-contract.md`: deterministic smoke checks, live checks, evidence inspection, and release readiness.

## Review Questions

- Can a reviewer find which candidate version was evaluated for each case?
- Can a reviewer inspect per-case score, judge output when present, ASI, rollout evidence, and errors?
- Can a reviewer explain why the optimizer selected, rejected, or promoted a candidate?
- Does verification distinguish system-loop success from agent-quality improvement?
