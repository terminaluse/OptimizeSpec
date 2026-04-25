# OptimizeSpec

OptimizeSpec is a TypeScript CLI and skill pack for creating spec-driven optimization systems for agents.

It does not ship a Python optimization runtime as the product. Instead, it helps you define an eval contract, design the runner and optimizer, and generate target-repo files that match the target agent's stack.

## What You Get

- A TypeScript/Node CLI for creating and validating OptimizeSpec artifacts.
- Repo-local skills for proposal, design, apply, and verification workflows.
- Target-repo scaffolding for eval runners and optimizer entrypoints.
- A Python Claude Managed Agents + GEPA harness kept as reference/test material under `examples/python-managed-agent/`.
- Reference agent fixtures under `tests/fixtures/reference-agents/`; optimization systems are generated during tests instead of committed as examples.

## Install For Development

```bash
npm install
npm run build
node bin/optimizespec.js --help
```

Node.js 20.19.0 or newer is required.

## Install For Users

After release, install the CLI globally:

```bash
npm install -g optimizespec
optimizespec --help
```

Or run it without a global install:

```bash
npx optimizespec@latest --help
```

## CLI Quickstart

Initialize OptimizeSpec files in a target project:

```bash
optimizespec init
```

Create a new optimization-system change:

```bash
optimizespec new change improve-agent-output \
  --description "Improve the agent's answer quality on support triage tasks."
```

Inspect and validate the change:

```bash
optimizespec status --change improve-agent-output
optimizespec validate improve-agent-output
```

Generate TypeScript runner files into the target repository:

```bash
optimizespec apply \
  --change improve-agent-output \
  --target . \
  --stack typescript
```

Agent-compatible commands support `--json`:

```bash
optimizespec status --change improve-agent-output --json
optimizespec validate improve-agent-output --json
```

## Skills

The repo includes a `skills/` folder for coding agents that can use repo-local skills:

```text
skills/
  optimizespec-new/
  optimizespec-continue/
  optimizespec-apply/
  optimizespec-verify/
  optimizespec-common/
```

Use them in this order:

1. `optimizespec-new`: draft the eval contract from intent and examples.
2. `optimizespec-continue`: create the design, specs, and tasks.
3. `optimizespec-apply`: implement the eval runner and optimizer in the target repo.
4. `optimizespec-verify`: check eval, compare, optimize, and evidence readiness.

## Python Reference Example

The original Python Managed Agents + GEPA prototype moved to:

```text
examples/python-managed-agent/
```

It remains useful as a reference harness for candidate compilation, Claude Managed Agents sessions, GEPA evaluator wiring, and evidence-ledger structure. It is not the public OptimizeSpec package and is not required for normal CLI usage.

Reference agents live in:

```text
tests/fixtures/reference-agents/
```

Those fixtures are committed inputs. Generated optimization systems, run ledgers, optimizer traces, and `optimizespec.generated/` output should be created in temporary test workspaces or ignored local `runs/` directories, not committed as product examples.

Run its deterministic tests from the repo root:

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

- [TECHNICAL.md](TECHNICAL.md) for architecture and release notes.
- [skills/optimizespec-new/SKILL.md](skills/optimizespec-new/SKILL.md) for creating a new OptimizeSpec workflow.
- [skills/optimizespec-common/references/reference-contracts.md](skills/optimizespec-common/references/reference-contracts.md) for shared evidence, runner, grader, ASI, candidate, optimizer, runtime, and verification contracts.

## License

MIT
