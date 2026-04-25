# OptimizeSpec

OptimizeSpec is a TypeScript CLI and skill pack for spec-driven development of optimization systems for agents. It helps turn an improvement goal into reviewable specs, eval criteria, runner design, optimizer wiring, and evidence that a proposed change is actually better.

## Why Use It

- Define what "better" means before tuning prompts, tools, or config.
- Keep eval, scorer, optimizer, and evidence requirements reviewable.
- Generate project-local optimization code that reuses your existing agent runtime instead of a bundled runtime.

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

Then drive the workflow through the coding-agent skills from inside the agent project. In Codex, invoke an installed skill with `$`, for example `$optimizespec-new`.

```text
$optimizespec-new
Create a change named improve-agent-output that improves the agent's answer quality on support triage tasks.
```

```text
$optimizespec-continue
```

```text
$optimizespec-apply improve-agent-output
```

```text
$optimizespec-verify improve-agent-output
```

## What Gets Created

OptimizeSpec keeps planning artifacts in one root folder:

```text
optimizespec/changes/<change-name>/
  proposal.md
  design.md
  specs/
  tasks.md
```

The proposal records where the durable optimization-system code will live:

```text
## Optimization System Location

- Decision: create new folder|use existing folder
- Path: <repo-relative path>
```

Apply writes runner, scorer, optimizer, adapter, and evidence code to that recorded path. The optimization system should call into the real agent factory, tools, skills, MCP servers, environment configuration, and permissions through a narrow adapter.

## Learn More

- [TECHNICAL.md](TECHNICAL.md) for architecture, package boundaries, reference agents, and release notes.
- [skills/optimizespec-new/SKILL.md](skills/optimizespec-new/SKILL.md) for creating a new OptimizeSpec workflow.
- [skills/optimizespec-common/references/reference-contracts.md](skills/optimizespec-common/references/reference-contracts.md) for runner, grader, ASI, candidate, optimizer, runtime, evidence, and verification contracts.

## Development

Node.js 20.19.0 or newer is required.

```bash
npm install
npm test
npm run pack:check
```

The Python Claude Managed Agent reference harness lives under `examples/py-claude-managed-agent/` and is not part of the npm package.

## License

MIT
