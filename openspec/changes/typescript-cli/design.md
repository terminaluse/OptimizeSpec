## Context

The current repo exposes `optimizespec` through Python packaging and keeps the CLI in `src/optimizespec/cli.py`. That happened because the first prototype needed a working Claude Managed Agents plus GEPA loop. It proved the technical concept, but it blurred the product boundary. OptimizeSpec should not be released as a Python optimization package; it should be a spec-driven tool that helps users create optimization systems in their own repositories.

OpenSpec's current public package is a TypeScript/Node CLI: its package metadata declares a `bin` entry, an ESM package, Node 20.19+ engine, compiled `dist` output, a small `bin/openspec.js` shim, a TypeScript build, Vitest tests, and commander-based command registration. Its CLI docs also separate human-oriented terminal commands from agent-compatible commands that support JSON output.

OptimizeSpec should use the same release posture. The product command should be a TypeScript CLI. The Python code should become an example, fixture, or reference implementation used to validate that generated optimization systems can work, not the core installed runtime.

## Goals / Non-Goals

**Goals:**

- Make TypeScript the public CLI implementation and release entrypoint.
- Keep command UX close to OpenSpec: predictable command groups, clear help, deterministic exit codes, and JSON output for agent/script paths.
- Make OptimizeSpec generate or guide optimization-system implementation from specs.
- Move the existing Python Managed Agents and GEPA prototype out of the shipped package surface and into examples, fixtures, or reference material.
- Ensure generated runners live in the target repository and can match the target repository's language.
- Make release packaging npm-first for the CLI.
- Add TypeScript tests and packaging checks before release.

**Non-Goals:**

- Port every Python prototype module to TypeScript in the first change.
- Redesign the Managed Agents candidate model or GEPA optimizer behavior.
- Ship a Python package as the normal user-facing product.
- Add a terminal dashboard.
- Introduce telemetry in this change.
- Publish a package as part of the spec creation step.

## Decisions

### 1. Build a Node ESM CLI package modeled after OpenSpec

Add TypeScript CLI infrastructure:

- `package.json` with `type: "module"`, `bin: { "optimizespec": "./bin/optimizespec.js" }`, Node engine requirement, `files` allowlist, and scripts for `build`, `dev:cli`, and `test`.
- `tsconfig.json` using modern Node module resolution, strict mode, declarations, and `dist` output.
- `bin/optimizespec.js` as a minimal executable shim that imports the compiled CLI.
- `src/cli/index.ts` as the command registration root.
- `src/cli/commands/*` for command handlers.
- `test/` or `tests-ts/` for Vitest-based CLI tests.

Rationale: This mirrors the OpenSpec release shape and gives users a normal npm CLI install path.

Alternatives considered:

- Keep the Python console script and only rewrite docs.
  Rejected because the user-facing CLI would still be Python.
- Use a TypeScript script without build output.
  Rejected because release packages should ship compiled JavaScript and type declarations where useful.

### 2. Make generated systems target-repo code, not bundled runtime code

OptimizeSpec's output should be artifacts and generated implementation in the user's target repository. If the target repository is TypeScript, the apply flow should produce TypeScript eval runners and optimization commands unless the approved design says otherwise. If the target repository is Python, generated Python is acceptable. The product itself should not require users to import a bundled Python runtime to run normal spec-authoring commands.

Rationale: The user's mental model is correct: OptimizeSpec builds an optimization system based on a spec. That system belongs with the target agent, not inside OptimizeSpec's release package.

Alternatives considered:

- Keep a reusable Python runtime package and make every generated system depend on it.
  Rejected because it forces a Python dependency onto non-Python target repos and makes OptimizeSpec look like a Python optimization framework rather than a spec-driven generator.
- Port all optimization execution to a bundled TypeScript runtime immediately.
  Deferred because generated target-repo code can be TypeScript without requiring a monolithic bundled runtime.

### 3. Demote the Python prototype to example, fixture, or reference material

Move the current Python implementation out of `src/optimizespec/` before release. Candidate locations:

- `examples/python-managed-agent/` for a runnable example
- `tests/fixtures/python-managed-agent/` for regression tests
- `reference/python-gepa-managed-agent/` for source material used by skills/templates

The release package may include selected example/reference files only if they are intentionally part of the CLI's templates or examples. It should not publish a Python package as the primary product.

Rationale: Keeping the prototype is useful because it has live validation coverage and demonstrates a real Claude Managed Agents flow. Shipping it as `src/optimizespec` sends the wrong product signal.

Alternatives considered:

- Delete the Python code immediately.
  Rejected because it is still useful for validation and as a reference while the TypeScript CLI and generated-system templates mature.
- Keep the Python code in `src/optimizespec` but hide the console script.
  Rejected because source layout still implies the Python package is the product.

### 4. Avoid Python delegation for normal product flows

Normal commands for creating, inspecting, validating, and applying specs should be implemented in TypeScript. A temporary Python adapter is acceptable only for explicitly marked legacy or example commands, such as running the old prototype demo while we still want regression coverage.

If a temporary adapter exists, it must:

- be isolated in a named compatibility module
- be absent from normal spec-authoring flows
- fail with clear setup guidance when Python prerequisites are missing
- be scheduled for removal or conversion

Rationale: A TypeScript CLI that secretly requires Python for core behavior would not satisfy the product direction.

Alternatives considered:

- Use Python delegation for most commands during migration.
  Rejected because it keeps Python as the true product runtime.

### 5. Treat JSON mode as a first-class agent contract

Agent-compatible commands should support `--json` and keep stdout valid JSON in that mode. Human progress, spinners, warnings, and logs should go to stderr or be suppressed.

Rationale: OpenSpec explicitly supports agent/script command paths with JSON output. OptimizeSpec is an agent-facing tool, so this contract matters for reliability.

Alternatives considered:

- Let agents parse human text.
  Rejected because it is brittle and hard to validate.

### 6. Keep release assets intentional

The npm package should include only runtime CLI assets and required templates/examples. Generated directories such as `runs/`, old `dist/` contents, `build/`, caches, `.env`, local registries, OpenSpec planning history, Python package metadata, and test fixtures not needed at runtime should be excluded.

If the root `skills/` and example changes are part of the product, the package must include them intentionally and the CLI must know how to locate them. If they are repo examples only, move them under `examples/` or keep them out of package files.

Rationale: The current Python wheel did not include repo-root skills or change examples, which makes release behavior ambiguous. The TypeScript package should make this explicit.

Alternatives considered:

- Package the whole repository.
  Rejected because it would include development-only artifacts and confuse the product surface.

## Risks / Trade-offs

- [Prototype code removal loses validation coverage] -> Move the Python prototype to examples or fixtures and keep regression tests pointed at the new location.
- [Generated target-repo code becomes too stack-specific] -> Keep templates language-aware and require design artifacts to choose target-repo language based on discovery.
- [Temporary Python adapter leaks into core product] -> Limit any adapter to legacy/example commands and add tasks to remove or replace it.
- [Command compatibility drift] -> Add snapshot or golden tests for help text and command registration.
- [JSON output polluted by logs] -> Test stdout parsing in JSON mode and send human logs to stderr.
- [Release package misses needed assets] -> Add package contents tests using `npm pack --dry-run` or equivalent.

## Migration Plan

1. Add TypeScript package infrastructure without deleting the Python prototype.
2. Implement normal spec-authoring and validation CLI paths in TypeScript.
3. Move the Python prototype from `src/optimizespec/` to examples, fixtures, or reference material.
4. Update docs to show npm/Node CLI usage and mark Python prototype commands as examples or legacy.
5. Add TypeScript command tests and packaging checks.
6. Remove the Python console script and Python package metadata from the public release path.
7. Generate target-repo runners from templates rather than requiring the installed OptimizeSpec package as their runtime.

Rollback is straightforward while the Python prototype remains in the repo: restore the Python console script as a development-only command or example runner and keep the TypeScript CLI disabled or unpublished.

## Open Questions

- Should any Python example be included in the npm package, or should it remain repo-only?
- Should the TypeScript CLI command names stay flat for compatibility or move to grouped commands such as `demo eval`, `self eval`, and `validation run`?
- Should root `skills/` and example changes ship in the npm package or remain repo-only examples/templates?
- Should the long Python validation harness be split into TypeScript validation logic plus Python example tests, or moved wholesale to development-only fixtures?
