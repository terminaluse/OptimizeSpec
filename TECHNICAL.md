# Technical Notes

This repository contains the public TypeScript CLI and OptimizeSpec skill/template system.

## TypeScript CLI

The release CLI follows an OpenSpec-style TypeScript package layout:

```text
package.json
bin/optimizespec.js
src/cli/index.ts
dist/
skills/
```

The package entrypoint is `bin/optimizespec.js`, which imports the compiled JavaScript from `dist/`. The CLI is implemented with `commander` and targets Bun 1.3.0 or newer.

Build and test:

```bash
bun install
bun run build
bun run test
```

Package inspection:

```bash
bun run pack:check
```

The npm package allowlist intentionally includes `bin`, `dist`, `skills`, and documentation. It does not include source tests, root run artifacts, caches, generated optimization systems, or local OpenSpec/OptimizeSpec planning history.

## CLI Commands

The TypeScript CLI focuses on project setup, artifact creation, status, and validation:

```bash
optimizespec init [path]
optimizespec new change <name> [--description <text>]
optimizespec status --change <name> [--json]
optimizespec validate <name> [--json]
```

Implementation is handled by the installed apply skill:

```text
$optimizespec-apply <change-name>
```

That skill writes files to the optimization-system path recorded in the proposal's `Optimization System Location` section. If that section does not name a concrete path, the user and coding agent should update the proposal before implementation. A common default for new systems is:

```text
optimizespec/systems/<change-name>/
```

Generated code is deliberately local to the project being improved. The optimization system should import or adapt the project's real agent factory, tools, environment configuration, and command conventions instead of copying a parallel agent implementation. OptimizeSpec itself does not require projects to import a bundled Python runtime.

## Artifact Layout

The default artifact layout in a project being improved is:

```text
optimizespec/changes/<change-name>/
  proposal.md
  design.md
  specs/
  tasks.md
```

`proposal.md` must include an `Optimization System Location` section with a create-or-reuse decision, the repo-relative path where implementation code will live, why that path fits the repo, and which existing agent code/dependencies the system will reuse.

Specs use OpenSpec-style requirement blocks:

```markdown
### Requirement: Generated optimization system
The agent project SHALL contain generated eval and optimization entrypoints.

#### Scenario: Runner generated
- **WHEN** the change is applied
- **THEN** runner files are written in the selected project language
```

## Skills And References

The skill pack remains repo-local and packageable:

- `skills/optimizespec-new`
- `skills/optimizespec-continue`
- `skills/optimizespec-apply`
- `skills/optimizespec-verify`
- `skills/optimizespec-common`

Shared contracts originate under `skills/optimizespec-common/references/`, and phase skills vendor the references they need so each installed skill folder is self-contained. Runtime-neutral contracts live under `references/core/`; runtime-specific contracts live under `references/runtimes/<runtime-id>/`. V1 apply support currently targets Claude Managed Agents through `references/runtimes/claude-managed-agent/`, while the core proposal, evidence, grader, ASI, candidate, optimizer, runner, and verification contracts stay runtime-neutral.

The most important contract is the evidence ledger: applied systems should persist run manifest, candidate registry, per-case scores, judge records when present, ASI, rollout records, comparison records, optimizer lineage, and promotion decisions.

## Release Boundary

Before release, verify:

- `bun run test` passes.
- `bun run pack:check` does not include source tests, local planning artifacts, or generated optimization systems.
- Documentation presents the TypeScript CLI as the public command surface.
