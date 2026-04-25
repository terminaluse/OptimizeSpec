# Technical Notes

This repository now has two clear layers:

- The public product is the TypeScript CLI and OptimizeSpec skill/template system.
- The Python Claude Managed Agents + GEPA implementation is a reference harness under `examples/py-claude-managed-agent/`.
- Reference agents are committed as test inputs under `tests/fixtures/reference-agents/`; optimization systems are generated outputs.

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

The npm package allowlist intentionally includes `bin`, `dist`, `skills`, and documentation. It does not include `examples/py-claude-managed-agent/`, `tests/fixtures/reference-agents/`, root run artifacts, Python package metadata, caches, generated optimization systems, or OpenSpec planning history.

## CLI Commands

The TypeScript CLI focuses on spec authoring and scaffolding for the agent project:

```bash
optimizespec init [path]
optimizespec new change <name> [--description <text>]
optimizespec status --change <name> [--json]
optimizespec validate <name> [--json]
optimizespec apply --change <name> --target <path> --stack typescript|python [--json]
```

`apply` writes files to the optimization-system path recorded in the proposal's `Optimization System Location` section. If that section does not name a concrete path, the CLI falls back to:

```text
optimizespec/systems/<change-name>/
```

Generated code is deliberately local to the project being improved. A TypeScript project gets TypeScript runner files; a Python project can get Python runner files. The optimization system should import or adapt the project's real agent factory, tools, environment configuration, and command conventions instead of copying a parallel agent implementation. OptimizeSpec itself does not require projects to import a bundled Python runtime.

## Reference Fixtures

Committed reference agents live under:

```text
tests/fixtures/reference-agents/<fixture-id>/
  agent.yaml
  request.md
```

These files are source inputs for tests and skills. They should stay narrow and hand-authored. Do not commit full generated `optimizespec/changes/<change-name>/` systems, generated optimization-system folders, run ledgers, optimizer traces, or generated runner directories as examples.

Tests that need an optimization system should generate one in a temporary workspace or an ignored `runs/` directory. If deterministic comparison data is needed, keep it as a focused expected-output fixture rather than a complete runnable system.

To add a reference agent, create `tests/fixtures/reference-agents/<fixture-id>/agent.yaml` and `request.md`, then add or update a test that generates the optimization-system artifacts from that fixture in a temporary directory. Keep the fixture limited to source inputs and metadata. If a regression needs expected output, store only the stable contract being asserted, such as a CLI JSON shape or a short generated-file excerpt, and regenerate it through an explicit test update rather than committing a full runnable system.

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

## Python Reference Example

The Python reference harness lives at:

```text
examples/py-claude-managed-agent/
```

It contains the original modules for:

- candidate compilation into Claude Managed Agents config
- Managed Agents runtime sessions and event collection
- GEPA evaluator and optimizer wiring
- deterministic validation harness
- evidence-ledger generation in temporary or ignored run directories

Run Python regression tests from the repo root:

```bash
pytest -q
```

The root `pytest.ini` adds `examples/py-claude-managed-agent/src` to `PYTHONPATH`.

Live example runs require:

```bash
uv pip install -e examples/py-claude-managed-agent[dev]
uv pip install -r examples/py-claude-managed-agent/requirements-managed-agents-preview.txt
export ANTHROPIC_API_KEY=...
```

Live tests remain opt-in through environment flags such as `OPTIMIZESPEC_RUN_LIVE_IMPROVEMENT=1`.

## Release Boundary

Before release, verify:

- `npm test` passes.
- `npm run pack:check` does not include `examples/py-claude-managed-agent/`, `tests/fixtures/reference-agents/`, or generated optimization systems.
- `pytest -q` passes for the Python reference example.
- Documentation presents the TypeScript CLI as the public command surface.
- Python commands are documented only as reference harness workflows.
