## Context

The current skill pack works, but its naming sends mixed signals. `optimizespec-common` contains broadly reusable contracts such as evidence, grader behavior, ASI, candidate surfaces, optimizer acceptance, criteria-first evals, verification, and repo patterns. It also contains Claude Managed Agent-specific references such as `managed-agents-runner.md` and `managed-agents-runtime-contract.md`, and phase skills directly state that v1 supports only Claude Managed Agents.

That is acceptable as an implementation limitation, but it should be represented as a runtime adapter boundary. The common skill can stay as the package that ships shared references and assets. Inside it, references should be grouped by applicability so future runtimes can be added without renaming the product or duplicating the whole skill pack.

## Goals / Non-Goals

**Goals:**

- Keep `optimizespec-common` as the shared skill folder.
- Separate generic OptimizeSpec contracts from Claude Managed Agent-specific runtime contracts.
- Make reference paths communicate scope.
- Keep installed skills self-contained after the move.
- Preserve the current v1 implementation rule: apply supports Claude Managed Agents only.
- Make future runtime adapters possible without another large restructuring.

**Non-Goals:**

- Add support for another runtime in this change.
- Create separate installable skills for every runtime.
- Change the public CLI command surface.
- Redesign evidence, grader, ASI, optimizer, or candidate contracts.
- Remove the Python Claude Managed Agent reference harness.

## Decisions

### 1. Keep common, add scoped reference directories

Use this directory shape inside every installed skill folder that vendors references:

```text
references/
  core/
    workflow.md
    criteria-first-evals.md
    eval-system-evidence.md
    grader-contract.md
    asi-contract.md
    candidate-surface.md
    optimizer-contract.md
    verification-contract.md
    repo-patterns.md
    reference-contracts.md
  runtimes/
    claude-managed-agent/
      managed-agents-runtime-contract.md
      managed-agents-runner.md
      scorers-and-asi.md
```

Rationale: This keeps one common skill while making the runtime boundary obvious. It also avoids introducing `optimizespec-claude-managed-agent` as a separate skill before there is more than one runtime adapter.

Alternative considered: create a separate `optimizespec-claude-managed-agent` skill. That may make sense later, but it is more packaging and install complexity than needed now.

### 2. Make the reference index runtime-aware

`reference-contracts.md` should become the small index that tells phase skills what to load:

- Always load `core/` contracts relevant to the phase.
- Load `runtimes/claude-managed-agent/` only when repo inspection identifies the target runtime as Claude Managed Agents.
- If repo inspection cannot determine the target runtime, proposal/design may ask a focused question or record unknowns, but apply must block until a supported runtime adapter is selected.
- If the target runtime is not Claude Managed Agents, v1 apply records an unsupported-runtime blocker unless a new runtime subtree exists.

Rationale: The product remains general, while implementation support remains honest.

### 3. Update phase skills and templates without changing workflow

The phase order stays the same:

1. `optimizespec-new`
2. `optimizespec-continue`
3. `optimizespec-apply`
4. `optimizespec-verify`

The difference is only reference selection:

- New/proposal work uses core contracts, inspects the repo, and records the inferred target runtime.
- Continue/design work uses core contracts and, for Claude Managed Agents, runtime contracts.
- Apply work requires a supported runtime subtree and writes implementation code according to that runtime.
- Verify work uses core evidence/verification contracts plus runtime-specific evidence expectations.

Templates should not hardcode `Runtime: Claude Managed Agents` in generic proposal sections. They should include an inferred `Runtime:` field that the coding agent fills from repo inspection, asking the user only when the runtime cannot be determined from code, dependency files, config, or docs. Claude Managed Agents remains the only v1-supported apply runtime.

### 4. Keep vendored phase references self-contained

The repo currently vendors references into each phase skill so installed skills work when only that skill folder is available at runtime. The restructuring must preserve that property. If `optimizespec-apply` references `references/core/runner-contract.md` and `references/runtimes/claude-managed-agent/managed-agents-runner.md`, both paths must exist inside `skills/optimizespec-apply/`.

Rationale: Installed skill folders cannot rely on sibling skills or repo-root files.

## Risks / Trade-offs

- **Risk: path churn across many skill folders.** Mitigation: update all vendored copies together and keep package tests for self-contained skill references.
- **Risk: users think non-Claude runtimes are fully supported.** Mitigation: documentation and apply instructions should say v1 apply support is Claude Managed Agent-only until another runtime subtree exists.
- **Risk: too much nesting.** Mitigation: only add two levels: `core/` and `runtimes/<runtime>/`.
- **Risk: stale references in docs/tests.** Mitigation: search for old root reference paths and run `npm test`, `npm run pack:check`, and deterministic Python tests if Python-facing reference paths change.

## Migration Plan

1. Create the new `core/` and `runtimes/claude-managed-agent/` directories in `optimizespec-common` and every phase skill that vendors references.
2. Move generic contracts into `core/`.
3. Move Managed Agent-specific contracts into `runtimes/claude-managed-agent/`.
4. Update `SKILL.md`, templates, and reference indexes to the new paths.
5. Update tests that check self-contained skill references.
6. Run packaging and test verification.
