---
name: gepa-evals-common
description: Shared GEPA eval self-improvement references and templates. Use only as a supporting skill when another GEPA eval skill needs workflow, ASI, Claude Managed Agents, scorer, or runner reference material.
---

# GEPA Evals Common

Do not use this as the primary user-facing workflow. Use it as a shared reference bundle for:

- `gepa-evals-new`
- `gepa-evals-continue`
- `gepa-evals-apply`
- `gepa-evals-verify`

## References

- `references/workflow.md`: OpenSpec-inspired artifact flow and directory convention.
- `references/criteria-first-evals.md`: lightweight criteria-first eval design, grader trust, and optimizer acceptance.
- `references/gepa-reflection.md`: GEPA reflective evolution, ASI, candidate fields, and optimizer configuration.
- `references/managed-agents-runner.md`: Claude Managed Agents rollout lifecycle.
- `references/scorers-and-asi.md`: scorer templates and ASI shape.
- `references/repo-patterns.md`: local `agent_gepa` prototype patterns to adapt.

## Assets

- `assets/templates/`: proposal, design, spec, task, eval case, and candidate templates.
- `assets/python_runner/agent_self_improve.py`: portable runner/optimizer implementation template for target repos.

Load only the specific reference or asset needed for the current task.
