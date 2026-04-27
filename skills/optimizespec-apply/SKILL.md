---
name: optimizespec-apply
description: Apply a completed OptimizeSpec self-improvement plan to an agent repository. Use when the user asks to implement eval cases, rollouts, scorers, ASI, direct eval, compare, or GEPA optimization from completed artifacts. Includes a concrete Python Claude Managed Agents reference, while the core contracts are runtime-neutral.
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
3. Read the proposal's `Optimization System Location` section and write implementation code only in the recorded executable-code folder. If the section is missing, the path is unresolved, or the import/runtime access plan is missing, stop and ask for the proposal/design to be updated before editing code.
4. Verify the recorded folder decision still matches the repo and that code in that folder can import or invoke the real agent modules using the repo's package setup, repo-root command, editable install, workspace command, or documented `PYTHONPATH`/module path. Reuse an existing folder only if the proposal says to; otherwise create the proposed folder.
5. Verify the artifacts and repo identify the target runtime or clearly record runtime unknowns. If no bundled runtime reference exists, continue from the core contracts and record the production adapter assumptions for the target runtime.
6. Read `../optimizespec-common/references/core/reference-contracts.md`, then load the apply-phase core contracts, starting with `../optimizespec-common/references/core/live-eval-runner-contract.md`. Load runtime-specific references only for the identified runtime. For live Python Claude Managed Agents work, inspect `../optimizespec-common/references/runtimes/claude-managed-agent/python-managed-agent-package/README.md` and `../optimizespec-common/references/runtimes/claude-managed-agent/python-managed-agent-package/src/optimizespec/runtime.py` before implementing the runner.
7. Implement tasks in order, marking each checkbox complete only after implementation and local verification.
8. Use bundled runtime references when they match the artifact runtime. For Claude Managed Agents, adapt `../optimizespec-common/references/runtimes/claude-managed-agent/python-managed-agent-package/` as the primary runnable reference for live Managed Agents execution.
9. After implementation and local validation, run the verify workflow by default unless the user has said not to run live or expensive commands. Do not run the full optimize loop during apply. If verification passes, ask whether the user wants to run the full optimize loop.

## Test Authenticity

Create only tests and verification steps that exercise real behavior through the target repo's production-equivalent runtime path. Do not add fake tests, mock-only tests, static prompt snapshots, fixture-only assertions, or placeholder checks to compensate for missing credentials, missing MCP/tool access, missing hosted runtime access, or unavailable external services.

If credentials, permissions, environment configuration, hosted runtime access, MCP servers, tools, skills, or production integrations are missing, stop and ask the user for what is needed. Record the blocker clearly if the user cannot provide it. Never mark a task complete or claim verification from tests that do not exercise the real integration required by the eval contract.

## Implementation Contract

The applied system must expose operations equivalent to:

- direct eval
- optimize
- compare
- show candidate

The rollout executor must run the real agent runtime for live eval cases and produce score plus ASI for every candidate/eval-case pair. The applied system must persist a durable evidence ledger with run manifest, candidate registry, runtime-neutral rollout records, per-case scores, judge records when present, ASI, comparison records, optimizer lineage, leaderboard, selected best candidate, and optional promotion or no-promotion evidence. Read:

- `../optimizespec-common/references/core/live-eval-runner-contract.md`
- `../optimizespec-common/references/core/eval-system-evidence.md`
- `../optimizespec-common/references/core/runner-contract.md`
- `../optimizespec-common/references/core/grader-contract.md`
- `../optimizespec-common/references/core/asi-contract.md`
- `../optimizespec-common/references/core/candidate-surface.md`
- `../optimizespec-common/references/core/optimizer-contract.md`
- `../optimizespec-common/references/core/verification-contract.md`
- `../optimizespec-common/references/core/repo-patterns.md`

For Claude Managed Agents, also read:

- `../optimizespec-common/references/runtimes/claude-managed-agent/managed-agents-runtime-contract.md`
- `../optimizespec-common/references/runtimes/claude-managed-agent/managed-agents-runner.md`
- `../optimizespec-common/references/runtimes/claude-managed-agent/scorers-and-asi.md`
- `../optimizespec-common/references/runtimes/claude-managed-agent/python-managed-agent-package/`

Use the target repo's existing factory or session runner when available.
The optimization system should import or adapt the target repo's real agent factory, tools, skills, MCP servers, environment configuration, and permissions through a narrow adapter so live evals use production-equivalent integrations.
The core optimization loop is live eval only: static prompt scoring, fixture execution, dry-run evaluation, preflight/readiness tiers, and promotion decisions are not alternate eval modes. Runtime setup failures must be separated from candidate-quality feedback, and best-candidate selection must come from live rollout scores.
