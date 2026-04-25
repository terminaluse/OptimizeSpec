# OptimizeSpec

OptimizeSpec is a TypeScript CLI and skill pack for spec-driven development of optimization systems for agents.

Agent improvement is easy to start and hard to trust. A prompt tweak can fix one case while breaking another, and a real optimization loop needs more than a few examples: it needs an eval contract, runner design, scoring rules, candidate lineage, optimizer wiring, and evidence that the new agent is actually better.

OptimizeSpec gives you a spec-first workflow for building that system inside the agent repository you already own. You describe what good behavior means, turn that into checked artifacts, and generate files in that project for eval runners and optimizer entrypoints.

## Why Use It

- Turn vague agent-improvement goals into concrete eval and optimization specs.
- Keep runner, scorer, optimizer, and evidence requirements reviewable before code is generated.
- Generate implementation scaffolding that matches that project's stack instead of importing a bundled runtime.
- Give coding agents a repeatable skill workflow for creating, applying, and verifying optimization systems.
- Keep test/reference agents separate from the public CLI package.

OptimizeSpec is not a Python optimization runtime. The public package is the TypeScript CLI plus the OptimizeSpec skill pack. The Python Claude Managed Agents + GEPA code in this repo is reference and regression-test material.

## Quick Start

Install the CLI:

```bash
npm install -g optimizespec
optimizespec --help
```

Or run it without a global install:

```bash
npx optimizespec@latest --help
```

Initialize OptimizeSpec in an agent project:

```bash
optimizespec init
```

Create a change for an optimization system:

```bash
optimizespec new change improve-agent-output \
  --description "Improve the agent's answer quality on support triage tasks."
```

Inspect and validate the artifacts:

```bash
optimizespec status --change improve-agent-output
optimizespec validate improve-agent-output
```

Generate runner scaffolding into your agent project:

```bash
optimizespec apply \
  --change improve-agent-output \
  --target . \
  --stack typescript
```

Here `--target .` means "write the generated files into the current project."

Agent-compatible commands support `--json`:

```bash
optimizespec status --change improve-agent-output --json
optimizespec validate improve-agent-output --json
```

## Workflow

OptimizeSpec follows the same shape you would want from a careful engineering review:

1. Define the agent behavior you want to improve.
2. Capture eval inputs, expected outputs, scoring criteria, and qualitative feedback needs.
3. Design the runner, grader, optimizer, candidate surface, and evidence ledger.
4. Validate that the spec is complete enough to implement.
5. Generate files in the project and wire them to the real agent runtime.
6. Run eval, compare, optimize, and promotion checks in that project.

The goal is not just to produce a benchmark. The goal is to make agent optimization reproducible: what changed, why it changed, which cases improved, which cases regressed, and what evidence supports promotion.

## Generated Artifacts

OptimizeSpec creates planning artifacts in the project you are improving:

```text
optimizespec/changes/<change-name>/
  proposal.md
  design.md
  specs/
  tasks.md
```

When a change is applied, generated scaffolding is written under:

```text
optimizespec.generated/<change-name>/
```

Generated files are deliberately local to the project you are improving. A TypeScript project gets TypeScript runner scaffolding; a Python project can get Python runner scaffolding. OptimizeSpec does not require your project to adopt a bundled optimization runtime.

## What You Get

- A TypeScript/Node CLI for creating, validating, and applying OptimizeSpec artifacts.
- Repo-local skills for proposal, design, implementation, and verification workflows.
- Templates and reference contracts for runners, graders, ASI, candidates, optimizers, runtime integration, evidence ledgers, and promotion checks.
- Project-local scaffolding for eval runners and optimizer entrypoints.
- Reference agent fixtures used to test the workflow without committing generated optimization systems as product examples.

Node.js 20.19.0 or newer is required.

## Skills For Coding Agents

The repo includes a `skills/` folder for coding agents that can use repo-local skills:

```text
skills/
  optimizespec-new/
  optimizespec-continue/
  optimizespec-apply/
  optimizespec-verify/
  optimizespec-common/
```

Each phase skill is self-contained: the references, templates, or assets it instructs an agent to load are bundled inside that same skill folder.

Use them in this order:

1. `optimizespec-new`: draft the eval contract from intent and examples.
2. `optimizespec-continue`: create the design, specs, and tasks.
3. `optimizespec-apply`: implement the eval runner and optimizer in the agent project.
4. `optimizespec-verify`: check eval, compare, optimize, and evidence readiness.

## Reference Agents

The original Python Managed Agents + GEPA prototype lives in:

```text
examples/python-managed-agent/
```

It remains useful as a reference harness for candidate compilation, Claude Managed Agents sessions, GEPA evaluator wiring, and evidence-ledger structure. It is not part of the public npm package and is not required for normal CLI usage.

Reference agents live in:

```text
tests/fixtures/reference-agents/
```

Those fixtures are committed inputs. Generated optimization systems, run ledgers, optimizer traces, and `optimizespec.generated/` output should be created in temporary test workspaces or ignored local `runs/` directories, not committed as product examples.

Run deterministic Python reference tests from the repo root:

```bash
pytest -q
```

Live Managed Agents example runs require Anthropic preview access and the example requirements:

```bash
uv pip install -e examples/python-managed-agent[dev]
uv pip install -r examples/python-managed-agent/requirements-managed-agents-preview.txt
export ANTHROPIC_API_KEY=...
```

## Learn More

- [TECHNICAL.md](TECHNICAL.md) for architecture, package boundaries, and release notes.
- [skills/optimizespec-new/SKILL.md](skills/optimizespec-new/SKILL.md) for creating a new OptimizeSpec workflow.
- [skills/optimizespec-common/references/reference-contracts.md](skills/optimizespec-common/references/reference-contracts.md) for shared evidence, runner, grader, ASI, candidate, optimizer, runtime, and verification contracts.

## Development

Install dependencies and run the local TypeScript checks:

```bash
npm install
npm test
```

Build and inspect the package contents:

```bash
npm run build
npm run pack:check
```

## License

MIT
