# OptimizeSpec

OptimizeSpec is a CLI and skill pack for spec-driven development of optimization systems for agents. It helps turn an improvement goal into reviewable specs, eval criteria, runner design, optimizer wiring, and evidence that a proposed change is actually better.

## Why Use It

- Turn vague agent-improvement goals into concrete eval and optimization specs.
- Keep runner, scorer, optimizer, and evidence requirements reviewable before code is generated.
- Drive implementation through coding-agent skills that adapt to the project's real stack instead of importing a bundled runtime.

## Quick Start

Install the CLI for project setup and CI checks. The installed command expects Bun on your `PATH`.

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

`$optimizespec-apply <change-name>` writes runner, scorer, optimizer, adapter, and evidence code to that recorded path. The TypeScript CLI creates, continues, inspects, and validates OptimizeSpec artifacts; the installed skills implement the optimization system. The optimization system should call into the real agent factory, tools, skills, MCP servers, environment configuration, and permissions through a narrow adapter.

The core workflow is runtime-neutral. V1 apply support is Claude Managed Agent-specific, with runtime guidance bundled under the installed skill folders.

## Learn More

- [TECHNICAL.md](TECHNICAL.md) for architecture, package boundaries, and release notes.
- [skills/optimizespec-common/references/core/reference-contracts.md](skills/optimizespec-common/references/core/reference-contracts.md) for runner, grader, ASI, candidate, optimizer, runtime, evidence, and verification contracts.

## Acknowledgements

OptimizeSpec builds on [OpenSpec](https://github.com/Fission-AI/OpenSpec)'s spec-driven development approach. It also takes inspiration from [Symphony](https://github.com/openai/symphony)'s pattern of publishing the system as a Markdown specification that an agent can use to build or port the implementation.

## Development

Bun 1.3.0 or newer is required for local development and CLI execution.

```bash
bun install
bun run test
bun run pack:check
```

## License

MIT
