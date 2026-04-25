## Context

OptimizeSpec is moving toward a TypeScript CLI and skill pack that generates optimization-system artifacts for target repositories. The current repo still contains full optimization-system examples under `examples/py-claude-managed-agent/optimizespec/changes/`, including scripts and eval cases for package guidance, managed-agent eval generation, and a manual self-improvement system. Those directories are useful proof points, but they are generated/application artifacts rather than core source.

The cleaner boundary is that committed reference agents are inputs used by tests and skills, while generated optimization systems are outputs produced by the CLI, skills, or test harnesses. Tests should prove that generation works by creating those outputs in temporary workspaces instead of relying on prebuilt systems checked into the repo.

## Goals / Non-Goals

**Goals:**

- Keep reference agent definitions available for regression tests and live smoke tests.
- Remove committed full optimization-system examples from the normal repo surface.
- Make tests generate optimization systems in temporary directories and verify their structure.
- Preserve enough focused fixture data to compare important generated contracts when deterministic snapshots are useful.
- Keep the npm package free of generated optimization systems and Python example artifacts.
- Update documentation so contributors understand where reference agents live and where generated outputs belong.

**Non-Goals:**

- Delete the Python Managed Agents reference implementation in this change.
- Redesign the candidate schema, evaluator, optimizer, or live Managed Agents runtime.
- Require live Anthropic credentials for normal fixture-boundary tests.
- Commit large run outputs, optimizer traces, or generated working directories as golden data.

## Decisions

### 1. Reference agents are committed inputs

Move reference agent definitions into a clear fixture root such as `tests/fixtures/reference-agents/<agent-id>/`. Each fixture should contain only the input material needed to ask the CLI or skills to build an optimization system, such as `agent.yaml`, `request.md`, and small hand-authored fixture metadata.

Rationale: This makes the fixtures stable and reviewable. A reference agent is source material; it is not an already-built optimization system.

### 2. Optimization systems are generated outputs

Full `optimizespec/changes/<change-id>/` directories, generated runners, run ledgers, optimizer traces, and optimization-system output folders should be produced inside temporary test workspaces or ignored local run directories.

Rationale: If generated systems are committed as examples, tests can accidentally validate stale artifacts instead of validating the generator, CLI, and skills.

### 3. Golden snapshots must be narrow

When deterministic comparison is valuable, store focused expected-output snapshots under a test fixture directory such as `tests/fixtures/expected/`. Snapshots should cover schemas, manifests, CLI JSON output, or small generated file excerpts. They should not be complete runnable optimization systems unless a test explicitly needs that shape.

Rationale: Narrow snapshots catch regressions without turning generated systems back into product artifacts.

### 4. Python reference code remains a harness, not product content

The Python Managed Agents code can remain under an example or test-support directory while it is useful for regression and live smoke tests. However, tests should stop importing optimization-system scripts from `examples/py-claude-managed-agent/optimizespec/changes/*` as canonical source. If a Python helper remains necessary, it should live in test support or reference harness code rather than inside a committed generated change.

Rationale: The TypeScript CLI is the product surface. The Python code demonstrates and tests a real agent path, but it should not define repo-level optimization systems by default.

### 5. Verification owns the boundary

Add tests or package checks that fail when generated optimization-system directories are accidentally committed in release-visible locations. Existing npm package verification should continue to exclude examples and generated artifacts.

Rationale: The boundary needs an automated guard, not just documentation.

## Risks / Trade-offs

- [Loss of useful examples] -> Keep one small documented reference-agent fixture and generate the example output during tests.
- [Tests become more complex] -> Add helper utilities that create temp workspaces and run the CLI/skill flow consistently.
- [Golden snapshots become stale] -> Keep snapshots narrow and regenerate only through explicit test updates.
- [Live smoke tests lose context] -> Keep the Claude Managed Agent reference fixture and pass it through the generated-system path during the live gate.

## Migration Plan

1. Create `tests/fixtures/reference-agents/` and move current agent fixtures there.
2. Replace tests that import committed optimization-system scripts with tests that generate systems in temporary workspaces.
3. Remove or relocate `examples/py-claude-managed-agent/optimizespec/changes/*`.
4. Keep any required deterministic expected data under `tests/fixtures/expected/`.
5. Update documentation and package checks to explain and enforce the reference-agent/generated-output split.
6. Run deterministic Node and Python tests, then run the opt-in live Managed Agents smoke test.

Rollback is straightforward: restore the previous example change directories from version control if a specific regression test cannot be replaced immediately, then keep those directories outside the release package while the generator path is repaired.
