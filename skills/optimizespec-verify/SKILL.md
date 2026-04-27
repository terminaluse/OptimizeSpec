---
name: optimizespec-verify
description: Verify an OptimizeSpec self-improvement implementation. Use when checking generated skills, artifact completeness, eval runner behavior, ASI quality, direct eval, compare, or GEPA optimize readiness.
---

# OptimizeSpec Verify

Verify an OptimizeSpec implementation without making unrelated changes.

## Checks

1. Confirm artifacts are complete: proposal, design, specs, tasks.
2. Confirm the proposal and design name the inferred target runtime, evidence, and optimization-system folder, and that the implementation exists there or the blocker is explicitly recorded.
3. Validate skill frontmatter and reference paths, including runtime-specific paths named by the skill.
4. Run direct eval on a fixture or small eval suite.
5. Inspect the evidence ledger and confirm it includes run manifest, candidate registry, per-case scores, judge records when present, ASI records, rollout records, comparison records, optimizer lineage, leaderboard, and promotion or no-promotion decision.
6. Inspect a failed rollout and confirm ASI includes:
   - `Input`
   - `Expected`
   - `Actual`
   - `Feedback`
   - `Error`
   - `Agent Trajectory`
   - `scores`
   - field-specific ASI keys
7. Run compare and confirm per-case and aggregate deltas.
8. Confirm optimize can be invoked or explain missing live credentials/features/runtime support.
9. Separate system-loop readiness from agent-quality improvement claims.

Use `references/core/reference-contracts.md` to choose verification references.
Use `references/core/eval-system-evidence.md` as the evidence-ledger checklist.
Use `references/runtimes/claude-managed-agent/scorers-and-asi.md` as the ASI quality checklist for Claude Managed Agents implementations.
Use `references/runtimes/claude-managed-agent/python-managed-agent-package/README.md` and `references/runtimes/claude-managed-agent/python-managed-agent-package/src/optimizespec/runtime.py` as the live Python Managed Agents reference when checking SDK setup, stream-drain behavior, outcome capture, output retrieval, and cleanup.
Use `references/core/verification-contract.md` for readiness reporting.
