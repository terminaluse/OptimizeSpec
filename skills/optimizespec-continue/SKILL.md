---
name: optimizespec-continue
description: Continue an OptimizeSpec self-improvement change by creating the next artifact. Use when proposal, design, specs, or tasks need to be created for a Claude Managed Agents OptimizeSpec workflow.
---

# OptimizeSpec Continue

Create exactly one next artifact for an existing change under `optimizespec/changes/<change-name>/`.

## Artifact Order

1. `proposal.md`
2. `design.md`
3. `specs/*.md`
4. `tasks.md`

## Rules

- Read completed dependency artifacts before writing the next artifact.
- Read `references/reference-contracts.md` before choosing phase-specific context.
- For design work, load runner, evidence, grader, ASI, candidate surface, optimizer, Managed Agents runtime, and verification contracts.
- Do not skip artifacts.
- Do not implement code.
- Preserve explicit unknowns instead of guessing.
- If the agent project is not a Claude Managed Agents project, record the v1 runtime blocker.

## Templates

- Proposal: `assets/templates/proposal.md`
- Design: `assets/templates/design.md`
- Spec: `assets/templates/spec.md`
- Tasks: `assets/templates/tasks.md`

The design artifact must include runner invocation, rollout lifecycle, trace capture, evidence ledger path and required files, scoring and judge records, ASI mapping, candidate fields, GEPA optimizer configuration, optimizer lineage, promotion decision, and verification plan. Read `references/managed-agents-runner.md`, `references/gepa-reflection.md`, and the relevant reference contracts before writing design.
