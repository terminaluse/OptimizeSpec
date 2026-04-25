## Why

OptimizeSpec is intended to be a spec-driven system generator, not a Python optimization package. The current Python package exists because the first prototype proved a Claude Managed Agents plus GEPA loop end to end, but the release product should follow the OpenSpec-style distribution model: a TypeScript/Node CLI with a small executable shim, compiled `dist/` output, Node package metadata, and agent-friendly JSON command paths.

## What Changes

- **BREAKING** Replace the Python-facing `optimizespec` console entry point with a TypeScript/Node CLI as the supported public command surface.
- **BREAKING** Stop treating `src/optimizespec/*.py` as the release package. Move the Python Managed Agents/GEPA prototype to examples, fixtures, or reference material.
- Add a TypeScript CLI package layout modeled after OpenSpec: `package.json`, `tsconfig.json`, `bin/optimizespec.js`, `src/cli/`, compiled `dist/`, and Node 20+ runtime requirements.
- Make the TypeScript CLI generate or guide optimization systems from specs and templates instead of shipping one Python runtime as the product.
- Preserve the existing Python Managed Agents and GEPA implementation only as a reference example and regression fixture unless a short-lived internal adapter is explicitly required for compatibility.
- Require the TypeScript CLI to expose spec/workflow operations and any approved example commands without making Python a normal installation prerequisite.
- Require machine-readable `--json` output for commands intended for agents or scripts.
- Move release packaging to npm-first CLI distribution. Python packaging, if kept at all, is development-only or example-only.
- Add tests for command parsing, JSON output, generated project scaffolding, error handling, and release packaging.

## Capabilities

### New Capabilities

- `typescript-cli`: TypeScript/Node command surface, packaging, spec-driven system generation, JSON output, release behavior, and Python-prototype demotion for OptimizeSpec.

### Modified Capabilities

- None.

## Impact

Affected systems include CLI entrypoints, package metadata, release artifacts, documentation, examples, tests, and any command references in OpenSpec/OptimizeSpec artifacts. Existing Python modules under `src/optimizespec/` should move out of the shipped package into `examples/`, `reference/`, or test fixtures. The product CLI should create and validate optimization-system artifacts for target repositories, and generated runners should live in those target repositories rather than in OptimizeSpec's runtime package.
