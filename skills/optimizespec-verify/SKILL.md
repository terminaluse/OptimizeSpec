---
name: optimizespec-verify
description: Verify an OptimizeSpec self-improvement implementation. Use when checking generated skills, artifact completeness, eval runner behavior, ASI quality, direct eval, compare, or GEPA optimize readiness.
---

# OptimizeSpec Verify

Verify an OptimizeSpec implementation without making unrelated changes.

## Checks

1. Confirm artifacts are complete: proposal, design, specs, tasks.
2. Validate skill frontmatter and reference paths.
3. Run direct eval on a fixture or small eval suite.
4. Inspect the evidence ledger and confirm it includes run manifest, candidate registry, per-case scores, judge records when present, ASI records, rollout records, comparison records, optimizer lineage, leaderboard, and promotion or no-promotion decision.
5. Inspect a failed rollout and confirm ASI includes:
   - `Input`
   - `Expected`
   - `Actual`
   - `Feedback`
   - `Error`
   - `Agent Trajectory`
   - `scores`
   - field-specific ASI keys
6. Run compare and confirm per-case and aggregate deltas.
7. Confirm optimize can be invoked or explain missing live credentials/features.
8. Separate system-loop readiness from agent-quality improvement claims.

Use `../optimizespec-common/references/reference-contracts.md` to choose verification references.
Use `../optimizespec-common/references/eval-system-evidence.md` as the evidence-ledger checklist.
Use `../optimizespec-common/references/scorers-and-asi.md` as the ASI quality checklist.
Use `../optimizespec-common/references/verification-contract.md` for readiness reporting.
