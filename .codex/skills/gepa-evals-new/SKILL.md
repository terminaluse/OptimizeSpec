---
name: gepa-evals-new
description: Start a repo-local GEPA eval self-improvement change for Claude Managed Agents. Use when the user wants to create evals, optimize an agent with GEPA, define an agent self-improvement loop, or begin an ASI-first evaluation workflow.
---

# GEPA Evals New

Create the first artifact for a GEPA eval self-improvement change. The default workflow directory is:

```text
gepa-evals/changes/<change-name>/
```

## Workflow

1. Derive or confirm a kebab-case change name.
2. Create `gepa-evals/changes/<change-name>/proposal.md`.
3. Use `../gepa-evals-common/assets/templates/proposal.md` as the structure.
4. Capture known details without inventing missing information.
5. If target agent, scorer, or examples are incomplete, record explicit unknowns and candidate discovery questions.
6. Stop after creating `proposal.md`.

## Required Proposal Content

- Target agent and runtime context.
- Behavior to improve.
- Candidate fields GEPA may mutate, if known.
- Input examples and expected outputs or output shapes.
- Numeric scoring intent, preferably `0.0` to `1.0`.
- Qualitative rubric.
- ASI fields needed for reflection.
- Unknowns to resolve in design.

For workflow motivation, read `../gepa-evals-common/references/workflow.md`.
For ASI-first framing, read `../gepa-evals-common/references/gepa-reflection.md`.
