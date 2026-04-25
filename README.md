# OptimizeSpec

OptimizeSpec is a TypeScript CLI and skill pack for spec-driven development of optimization systems for agents.

Agent improvement is easy to start and hard to trust. A prompt tweak can fix one case while breaking another, and a real optimization loop needs more than a few examples: it needs an eval contract, runner design, scoring rules, optimizer wiring, and evidence that the new agent is actually better.

OptimizeSpec gives you a spec-first workflow for building that system inside the agent repository you already own. You describe what good behavior means, turn that into checked artifacts, and generate files in that project for eval runners and optimizer entrypoints.

## Why Use It

- Turn vague agent-improvement goals into concrete eval and optimization specs.
- Keep runner, scorer, optimizer, and evidence requirements reviewable before code is generated.
- Generate implementation scaffolding that matches that project's stack instead of importing a bundled runtime.


## Quick Start

Install the CLI for project setup and CI checks:

```bash
npm install -g optimizespec
```

Install the coding-agent skills separately:

```bash
npx skills add terminal-use/OptimizeSpec --skill '*'
```

Initialize the project metadata once:

```bash
optimizespec init
```

Then drive the workflow through the coding-agent skills from inside the agent project:

In Codex, invoke an installed skill with `$`, for example `$optimizespec-new`.

```text
$optimizespec-new
Create a change named improve-agent-output that improves the agent's answer quality on support triage tasks.
```

Continue the change until the proposal, design, specs, and tasks are complete:

```text
$optimizespec-continue
```

Apply the completed plan to the current project:

```text
$optimizespec-apply
```

Verify the resulting eval, compare, optimize, and evidence-ledger behavior:

```text
$optimizespec-verify
```

For scripted checks, use the CLI's machine-readable output:

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

## Artifacts And Code Location

OptimizeSpec keeps its planning artifacts in one root folder:

```text
optimizespec/changes/<change-name>/
  proposal.md
  design.md
  specs/
  tasks.md
```

The proposal also records where the durable optimization-system code will live:

```text
## Optimization System Location

- Decision: create new folder|use existing folder
- Path: <repo-relative path>
- Why this path fits the repo:
- Existing agent code to reuse:
```

That code path is chosen from repo inspection and user confirmation. It can be an existing eval folder or a new folder such as `optimizespec/systems/<change-name>/`. Apply writes runner, scorer, optimizer, adapter, and evidence code to the recorded path instead of guessing late in the workflow.

The optimization system should call into the real agent factory, tools, skills, MCP servers, environment configuration, and permissions through a narrow adapter. It should not fork or copy the agent implementation.


## Skills

Use them in this order:

1. `optimizespec-new`: draft the eval contract from intent and examples.
2. `optimizespec-continue`: create the design, specs, and tasks.
3. `optimizespec-apply`: implement the eval runner and optimizer in the agent project.
4. `optimizespec-verify`: check eval, compare, optimize, and evidence readiness.

## Reference Agents

An example Python Claude Managed Agent + GEPA prototype lives in:

```text
examples/py-claude-managed-agent/
```

It remains useful as a reference harness for candidate compilation, Claude Managed Agents sessions, GEPA evaluator wiring, and evidence-ledger structure. It is not part of the public npm package and is not required for normal CLI usage.

Reference agents live in:

```text
tests/fixtures/reference-agents/
```

Those fixtures are committed inputs. Generated optimization systems, run ledgers, optimizer traces, and run outputs should be created in temporary test workspaces or ignored local `runs/` directories, not committed as product examples.

Run deterministic Python reference tests from the repo root:

```bash
pytest -q
```

Live Managed Agents example runs require Anthropic preview access and the example requirements:

```bash
uv pip install -e examples/py-claude-managed-agent[dev]
uv pip install -r examples/py-claude-managed-agent/requirements-managed-agents-preview.txt
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
