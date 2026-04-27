---
name: optimizespec-verify
description: Verify an OptimizeSpec self-improvement implementation. Use when checking generated skills, artifact completeness, eval runner behavior, ASI quality, direct eval, compare, or GEPA optimize readiness.
---

# OptimizeSpec Verify

Verify an OptimizeSpec implementation without making unrelated changes.

## Checks

1. Confirm artifacts are complete: proposal, design, specs, tasks.
2. Confirm the proposal and design name the inferred target runtime, evidence, executable optimization-system folder, and run-output folder, and that the implementation exists in the executable folder or the blocker is explicitly recorded.
3. Validate skill frontmatter and reference paths, including runtime-specific paths named by the skill.
4. Run direct eval on a fixture or small eval suite.
5. Inspect the evidence ledger and confirm it includes run manifest, candidate registry, runtime-neutral rollout records, per-case scores, judge records when present, ASI records, comparison records, optimizer lineage, leaderboard, best-candidate evidence, and any optional promotion or no-promotion decision.
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
8. Confirm optimizer wiring with the smallest useful production-equivalent smoke that proves candidates are evaluated through live rollout scores. Do not use fake, mock-only, no-credential, or placeholder tests. If credentials, permissions, tools, MCP servers, hosted runtime access, or environment configuration are missing, stop and ask the user instead of weakening the test.
9. Confirm graders consume final output/report and trace evidence from the real runtime as the primary objective. Static prompt text can support diagnostics, but not live optimization scoring. For Claude Managed Agents, also check the runtime-specific ASI and scorer guidance.
10. Separate system-loop readiness from agent-quality improvement claims.

Use `../optimizespec-common/references/core/reference-contracts.md` to choose verification references.
Use `../optimizespec-common/references/core/live-eval-runner-contract.md` as the runtime-neutral live rollout evidence checklist.
Use `../optimizespec-common/references/core/eval-system-evidence.md` as the evidence-ledger checklist.
Use `../optimizespec-common/references/runtimes/claude-managed-agent/scorers-and-asi.md` as the ASI quality checklist for Claude Managed Agents implementations.
Use `../optimizespec-common/references/runtimes/claude-managed-agent/python-managed-agent-package/README.md` and `../optimizespec-common/references/runtimes/claude-managed-agent/python-managed-agent-package/src/optimizespec/runtime.py` as the live Python Managed Agents reference when checking SDK setup, stream-drain behavior, outcome capture, output retrieval, and cleanup.
Use `../optimizespec-common/references/core/verification-contract.md` for readiness reporting.
