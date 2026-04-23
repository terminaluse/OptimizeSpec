---
name: gepa-evals-continue
description: Continue a GEPA eval self-improvement change by creating the next artifact. Use when proposal, design, specs, or tasks need to be created for a Claude Managed Agents GEPA eval workflow.
---

# GEPA Evals Continue

Create exactly one next artifact for an existing change under `gepa-evals/changes/<change-name>/`.

## Artifact Order

1. `proposal.md`
2. `design.md`
3. `specs/*.md`
4. `tasks.md`

## Rules

- Read completed dependency artifacts before writing the next artifact.
- Do not skip artifacts.
- Do not implement code.
- Preserve explicit unknowns instead of guessing.
- If the target repo is not a Claude Managed Agents project, record the v1 runtime blocker.

## Templates

- Proposal: `../gepa-evals-common/assets/templates/proposal.md`
- Design: `../gepa-evals-common/assets/templates/design.md`
- Spec: `../gepa-evals-common/assets/templates/spec.md`
- Tasks: `../gepa-evals-common/assets/templates/tasks.md`

The design artifact must include runner invocation, rollout lifecycle, trace capture, ASI mapping, candidate fields, and GEPA optimizer configuration. Read `../gepa-evals-common/references/managed-agents-runner.md` and `../gepa-evals-common/references/gepa-reflection.md` before writing design.
