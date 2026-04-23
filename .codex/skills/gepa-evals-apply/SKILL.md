---
name: gepa-evals-apply
description: Apply a completed GEPA eval self-improvement plan to a Claude Managed Agents repository. Use when the user asks to implement eval cases, rollouts, scorers, ASI, direct eval, compare, or GEPA optimization from completed artifacts.
---

# GEPA Evals Apply

Implement a completed GEPA eval change.

## Preconditions

Require all files under `gepa-evals/changes/<change-name>/`:

- `proposal.md`
- `design.md`
- at least one `specs/*.md`
- `tasks.md`

If any are missing, stop and report the blocker.

## Workflow

1. Read all artifacts and summarize the planned target-repo changes.
2. Inspect the target repo before editing:
   - language and dependency files
   - existing Claude Managed Agents creation/session code
   - command/CLI conventions
   - test conventions
3. Verify the target repo uses Claude Managed Agents. If not, stop; v1 does not support other runtimes.
4. Implement tasks in order, marking each checkbox complete only after implementation and local verification.
5. Adapt `../gepa-evals-common/assets/python_runner/agent_self_improve.py` to the target repo when useful.

## Implementation Contract

The applied system must expose operations equivalent to:

- direct eval
- optimize
- compare
- show candidate

The rollout executor must produce score plus ASI for every candidate/eval-case pair. Read:

- `../gepa-evals-common/references/managed-agents-runner.md`
- `../gepa-evals-common/references/scorers-and-asi.md`
- `../gepa-evals-common/references/repo-patterns.md`

Never create a parallel Managed Agents path if the repo already has a factory or session runner that can be reused.
