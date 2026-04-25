---
name: optimizespec-apply
description: Apply a completed OptimizeSpec self-improvement plan to a Claude Managed Agents repository. Use when the user asks to implement eval cases, rollouts, scorers, ASI, direct eval, compare, or GEPA optimization from completed artifacts.
---

# OptimizeSpec Apply

Implement a completed OptimizeSpec change.

## Preconditions

Require all files under `optimizespec/changes/<change-name>/`:

- `proposal.md`
- `design.md`
- at least one `specs/*.md`
- `tasks.md`

If any are missing, stop and report the blocker.

## Workflow

1. Read all artifacts and summarize the planned changes to the agent project.
2. Inspect the agent project before editing:
   - language and dependency files
   - existing Claude Managed Agents creation/session code
   - command/CLI conventions
   - test conventions
3. Verify the agent project uses Claude Managed Agents. If not, stop; v1 does not support other runtimes.
4. Read `references/reference-contracts.md`, then load the apply-phase contracts for runner, evidence, grader, ASI, optimizer, runtime, and verification.
5. Implement tasks in order, marking each checkbox complete only after implementation and local verification.
6. Adapt `assets/python_runner/agent_self_improve.py` to the agent project when useful.

## Implementation Contract

The applied system must expose operations equivalent to:

- direct eval
- optimize
- compare
- show candidate

The rollout executor must produce score plus ASI for every candidate/eval-case pair. The applied system must persist a durable evidence ledger with run manifest, candidate registry, per-case scores, judge records when present, ASI, rollout records, comparison records, optimizer lineage, leaderboard, and promotion or no-promotion decision. Read:

- `references/eval-system-evidence.md`
- `references/runner-contract.md`
- `references/grader-contract.md`
- `references/asi-contract.md`
- `references/candidate-surface.md`
- `references/optimizer-contract.md`
- `references/managed-agents-runtime-contract.md`
- `references/verification-contract.md`
- `references/managed-agents-runner.md`
- `references/scorers-and-asi.md`
- `references/repo-patterns.md`

Never create a parallel Managed Agents path if the repo already has a factory or session runner that can be reused.
