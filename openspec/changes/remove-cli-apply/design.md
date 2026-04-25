## Context

The current TypeScript CLI includes an `apply` command that calls a local `scaffold()` helper. That helper validates the change, resolves the proposal's `Optimization System Location` path, and writes a tiny TypeScript or Python runner scaffold. The output is useful as a smoke test, but not as a real OptimizeSpec apply implementation.

The skill contract has a much higher bar. `$optimizespec-apply` must inspect the target repo, verify the runtime, reuse the existing agent factory/tools/skills/MCP/env/permissions, implement direct eval/compare/optimize/show-candidate, persist a durable evidence ledger, capture ASI, and mark tasks complete only after verification. Dogfooding confirmed that the skill-guided path can do this, while the CLI command alone cannot.

## Goals / Non-Goals

**Goals:**

- Remove the misleading CLI `apply` command before release.
- Make the release CLI honest: setup, artifact creation, status, and validation.
- Keep `$optimizespec-apply` as the implementation path.
- Update docs and tests to make the boundary obvious.
- Avoid shipping placeholder scaffolding as if it were a real optimization system.

**Non-Goals:**

- Remove the `optimizespec-apply` skill.
- Remove the proposal's `Optimization System Location` section.
- Add a new `scaffold` command in this change.
- Implement full CLI-driven repo inspection and runtime-specific application.
- Change the Python Claude Managed Agent reference harness.

## Decisions

### 1. Delete the CLI command instead of renaming it immediately

Remove the `.command('apply')` registration from `src/cli/index.ts`.

Rationale: A renamed `scaffold` command could be useful later, but adding it now would create another release promise and documentation surface. The immediate release need is clarity.

### 2. Remove unused scaffold-only helpers when practical

Remove helper functions that only exist to power CLI apply, including generic renderer helpers and output-dir parsing, unless a helper is still used by another command or test.

Rationale: Keeping dead scaffold code increases the chance it reappears in docs or gets mistaken for supported implementation behavior.

### 3. Update tests from "apply generates placeholders" to "apply is absent"

CLI tests should assert:

- help includes `init`, `new`, `continue`, `status`, and `validate`
- help does not list `apply`
- invoking `optimizespec apply` exits non-zero
- JSON behavior remains covered for supported commands

Remove tests that assert generated placeholder runner files.

### 4. Keep implementation docs skill-first

README should continue to show:

```text
$optimizespec-apply improve-agent-output
```

TECHNICAL should describe the TypeScript CLI as artifact tooling. It should not list `optimizespec apply` as a CLI command. The docs may mention that the proposal records where implementation code will live, but implementation is done by the skill.

## Risks / Trade-offs

- **Risk: Users expect an all-CLI workflow.** Mitigation: README and TECHNICAL should explicitly say coding-agent skills perform implementation.
- **Risk: Removing apply feels like reduced capability.** Mitigation: the removed command was not capable enough for the product promise; the skill remains the real apply path.
- **Risk: Tests lose coverage for generated runner files.** Mitigation: replace that coverage with skill/package self-containment tests and validation of the dogfood-generated system where appropriate.
- **Risk: Future scaffold work lacks a home.** Mitigation: a later change can add `optimizespec scaffold` with narrow wording and tests if starter scaffolds are still valuable.

## Migration Plan

1. Remove the CLI `apply` command registration.
2. Delete or quarantine apply-only scaffold helpers.
3. Update CLI tests to assert the supported release command surface and absence of `apply`.
4. Update README quick start and TECHNICAL CLI command list.
5. Search for `optimizespec apply` references and either remove them or mark them as obsolete planning history where appropriate.
6. Run `npm test`, `npm run pack:check`, and OpenSpec validation for this change.
