---
name: optimizespec-continue
description: Continue an OptimizeSpec self-improvement change by creating the next artifact. Use when proposal, design, specs, or tasks need to be created for an OptimizeSpec workflow.
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
- Read `references/core/reference-contracts.md` before choosing phase-specific context.
- For design work, load live eval runner, core runner, evidence, grader, ASI, candidate surface, optimizer, and verification contracts.
- Inspect the repo and prior artifacts to infer or confirm the target runtime. Load `references/runtimes/claude-managed-agent/` contracts only when the repo or artifacts identify Claude Managed Agents.
- Preserve the proposal's `Optimization System Location` decision in design, specs, and tasks. If repo inspection shows the path should change, record the proposed correction before moving implementation work.
- Do not skip artifacts.
- Do not implement code.
- Preserve explicit unknowns for design follow-up.
- For Claude Managed Agents, design around live Session rollouts, eval cases, report/trace grading, ASI from live failures, and live-score optimization. Static prompt, fixture, dry-run, and template-output checks belong outside the eval path.
- If no bundled runtime reference exists for the target runtime, continue from the core contracts, record the adapter assumptions, and identify missing runtime-specific reference coverage.

## Templates

- Proposal: `assets/templates/proposal.md`
- Design: `assets/templates/design.md`
- Spec: `assets/templates/spec.md`
- Tasks: `assets/templates/tasks.md`

The design artifact must include inferred runtime and evidence, optimization-system location, import/runtime access plan, existing agent code and dependency reuse, runner invocation, rollout lifecycle, trace capture, evidence ledger path and required files, scoring and judge records, ASI mapping, candidate fields, GEPA optimizer configuration, optimizer lineage, best-candidate selection, and verification plan. Always read the relevant core reference contracts before writing design. For Claude Managed Agents designs, also read `references/runtimes/claude-managed-agent/managed-agents-runner.md`, `references/runtimes/claude-managed-agent/managed-agents-runtime-contract.md`, `references/runtimes/claude-managed-agent/scorers-and-asi.md`, and `references/runtimes/claude-managed-agent/python-managed-agent-package/README.md`. Inspect `references/runtimes/claude-managed-agent/python-managed-agent-package/src/optimizespec/runtime.py` when the design needs concrete live Python runner behavior.
