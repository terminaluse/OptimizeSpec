# Technical Notes

This repository now has two clear layers:

- The public product is the TypeScript CLI and OptimizeSpec skill/template system.
- The Python Claude Managed Agents + GEPA implementation is a reference example under `examples/python-managed-agent/`.

## TypeScript CLI

The release CLI follows an OpenSpec-style Node package layout:

```text
package.json
bin/optimizespec.js
src/cli/index.ts
dist/
skills/
```

The package entrypoint is `bin/optimizespec.js`, which imports the compiled JavaScript from `dist/`. The CLI is implemented with `commander` and targets Node.js 20.19.0 or newer.

Build and test:

```bash
npm install
npm run build
npm test
```

Package inspection:

```bash
npm run pack:check
```

The npm package allowlist intentionally includes `bin`, `dist`, `skills`, and documentation. It does not include `examples/python-managed-agent/`, root run artifacts, Python package metadata, caches, or OpenSpec planning history.

## CLI Commands

The TypeScript CLI focuses on spec authoring and target-repo scaffolding:

```bash
optimizespec init [path]
optimizespec new change <name> [--description <text>]
optimizespec status --change <name> [--json]
optimizespec validate <name> [--json]
optimizespec apply --change <name> --target <path> --stack typescript|python [--json]
```

`apply` generates target-repo files under:

```text
optimizespec.generated/<change-name>/
```

Generated code is deliberately local to the target repository. A TypeScript target gets TypeScript runner files; a Python target can get Python runner files. OptimizeSpec itself does not require target repos to import a bundled Python runtime.

## Artifact Layout

The default artifact layout in a target project is:

```text
optimizespec/changes/<change-name>/
  proposal.md
  design.md
  specs/
  tasks.md
```

Specs use OpenSpec-style requirement blocks:

```markdown
### Requirement: Generated optimization system
The target repository SHALL contain generated eval and optimization entrypoints.

#### Scenario: Runner generated
- **WHEN** the change is applied
- **THEN** runner files are written in the selected target language
```

## Skills And References

The skill pack remains repo-local and packageable:

- `skills/optimizespec-new`
- `skills/optimizespec-continue`
- `skills/optimizespec-apply`
- `skills/optimizespec-verify`
- `skills/optimizespec-common`

Shared contracts live under `skills/optimizespec-common/references/`. The most important contract is the evidence ledger: applied systems should persist run manifest, candidate registry, per-case scores, judge records when present, ASI, rollout records, comparison records, optimizer lineage, and promotion decisions.

## Python Reference Example

The Python example lives at:

```text
examples/python-managed-agent/
```

It contains the original modules for:

- candidate compilation into Claude Managed Agents config
- Managed Agents runtime sessions and event collection
- GEPA evaluator and optimizer wiring
- deterministic validation harness
- evidence-ledger examples

Run Python regression tests from the repo root:

```bash
pytest -q
```

The root `pytest.ini` adds `examples/python-managed-agent/src` to `PYTHONPATH`.

Live example runs require:

```bash
uv pip install -e examples/python-managed-agent[dev]
uv pip install -r examples/python-managed-agent/requirements-managed-agents-preview.txt
export ANTHROPIC_API_KEY=...
```

Live tests remain opt-in through environment flags such as `OPTIMIZESPEC_RUN_LIVE_IMPROVEMENT=1`.

## Release Boundary

Before release, verify:

- `npm test` passes.
- `npm run pack:check` does not include `examples/python-managed-agent/`.
- `pytest -q` passes for the Python reference example.
- Documentation presents the TypeScript CLI as the public command surface.
- Python commands are documented only as reference/example workflows.
