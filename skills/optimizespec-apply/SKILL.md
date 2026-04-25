---
name: optimizespec-apply
description: Apply a completed OptimizeSpec self-improvement plan to a supported agent repository. Use when the user asks to implement eval cases, rollouts, scorers, ASI, direct eval, compare, or GEPA optimization from completed artifacts. V1 apply support targets Claude Managed Agents.
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
   - runtime indicators, including Claude Managed Agents creation/session code when present
   - command/CLI conventions
   - test conventions
3. Read the proposal's `Optimization System Location` section and write implementation code only in the recorded folder. If the section is missing or the path is unresolved, stop and ask for the proposal/design to be updated before editing code.
4. Verify the recorded folder decision still matches the repo. Reuse an existing folder only if the proposal says to; otherwise create the proposed folder. Do not choose a different location during apply without updating the artifact.
5. Verify the artifacts and repo identify a supported runtime. V1 supports Claude Managed Agents only. If runtime is unsupported or ambiguous, stop and record the blocker instead of creating a parallel runtime path.
6. Read `references/core/reference-contracts.md`, then load the apply-phase core contracts and the `references/runtimes/claude-managed-agent/` runtime contracts.
7. Implement tasks in order, marking each checkbox complete only after implementation and local verification.
8. Adapt `assets/python_runner/agent_self_improve.py` to the agent project when useful.

## Implementation Contract

The applied system must expose operations equivalent to:

- direct eval
- optimize
- compare
- show candidate

The rollout executor must produce score plus ASI for every candidate/eval-case pair. The applied system must persist a durable evidence ledger with run manifest, candidate registry, per-case scores, judge records when present, ASI, rollout records, comparison records, optimizer lineage, leaderboard, and promotion or no-promotion decision. Read:

- `references/core/eval-system-evidence.md`
- `references/core/runner-contract.md`
- `references/core/grader-contract.md`
- `references/core/asi-contract.md`
- `references/core/candidate-surface.md`
- `references/core/optimizer-contract.md`
- `references/runtimes/claude-managed-agent/managed-agents-runtime-contract.md`
- `references/core/verification-contract.md`
- `references/runtimes/claude-managed-agent/managed-agents-runner.md`
- `references/runtimes/claude-managed-agent/scorers-and-asi.md`
- `references/core/repo-patterns.md`

Never create a parallel runtime path if the repo already has a factory or session runner that can be reused.
The optimization system should import or adapt the target repo's real agent factory, tools, skills, MCP servers, environment configuration, and permissions through a narrow adapter rather than copying them into a forked agent implementation.
