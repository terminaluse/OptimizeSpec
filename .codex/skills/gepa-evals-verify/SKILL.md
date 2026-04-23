---
name: gepa-evals-verify
description: Verify a GEPA eval self-improvement implementation. Use when checking generated skills, artifact completeness, eval runner behavior, ASI quality, direct eval, compare, or GEPA optimize readiness.
---

# GEPA Evals Verify

Verify a GEPA eval implementation without making unrelated changes.

## Checks

1. Confirm artifacts are complete: proposal, design, specs, tasks.
2. Validate skill frontmatter and reference paths.
3. Run direct eval on a fixture or small eval suite.
4. Inspect a failed rollout and confirm ASI includes:
   - `Input`
   - `Expected`
   - `Actual`
   - `Feedback`
   - `Error`
   - `Agent Trajectory`
   - `scores`
   - field-specific ASI keys
5. Run compare and confirm per-case and aggregate deltas.
6. Confirm optimize can be invoked or explain missing live credentials/features.

Use `../gepa-evals-common/references/scorers-and-asi.md` as the ASI quality checklist.
