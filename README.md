# OptimizeSpec

OptimizeSpec is a skill pack and CLI for creating repo-local self-improvement systems for agents. Given a goal like "make support-triage answers better," it guides your coding agent to create the eval specs, runner, scorer, optimizer, adapter, and evidence ledger.

## What You Get

- A self-improvement system for your agent: runner, scorer, optimizer, adapter, evidence ledger, candidate registry, and verification flow.
- A reviewable plan with proposal, design, tasks, eval criteria, and a clear definition of what can be optimized.
- Production-equivalent live evals against your real agent runtime, tools, skills, MCP servers, environment, and permissions.
- Traceable optimization results with candidate IDs, per-case rollouts, scores, feedback, and a selected best candidate.
- Portable contracts that let coding agents implement the system inside your repo while preserving your runtime and integration choices.

## Quick Start

Install the CLI:

```bash
bun install -g optimizespec
```

Then install the skills:

```bash
npx skills add terminal-use/OptimizeSpec --skill '*'
```

Initialize the project metadata once:

```bash
optimizespec init
```

Then drive the workflow through the coding-agent skills from inside the agent project:

```text
/optimizespec-new
Create a change named improve-agent-output that improves the agent's answer quality on support triage tasks.
```

For Codex, invoke the same skills with a `$` prefix, for example `$optimizespec-new`.

Continue until all the spec artifacts are generated:

```text
/optimizespec-continue
```

Implement the spec:

```text
/optimizespec-apply improve-agent-output
```

The apply skill runs verification as part of implementation. If you correct the implementation afterward, run the `verify` skill again:

```text
/optimizespec-verify improve-agent-output
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

`$optimizespec-apply <change-name>` writes runner, scorer, optimizer, adapter, and evidence code to that recorded path.

> [!NOTE]
> Choose the path based on your repo's structure. The optimization system should live where it can call into the real agent, tools, skills, MCP servers, environment configuration, and permissions through a narrow adapter, so optimization runs evaluate the same integrations your production agent uses.

## How OptimizeSpec Works

OptimizeSpec ships as portable skills and contracts. The generated system lives inside your repo, and a coding agent uses those contracts to implement the runner, scorer, optimizer, adapter, evidence ledger, candidate registry, and verification flow for your agent.

The repo-local adapter connects the optimizer to your existing agent factory, tools, skills, MCP servers, environment configuration, and permissions, so scores reflect the behavior your users actually get.

The core contracts are runtime-neutral. The skill pack includes a reference self-improvement system for Python Claude Managed Agents, and contributions for other hosted agent runtimes and languages are welcome.

## How the Self-Improvement Works

The generated self-improvement system uses GEPA's Optimize Anything API as the optimization engine. OptimizeSpec defines the eval runner, scorer, candidate surface, ASI feedback, and evidence ledger; GEPA uses those pieces to evaluate candidates, reflect on live failures, propose mutations, and select better candidates.

GEPA is a reflective evolutionary optimizer: it improves text-representable candidates by combining scores, traces, feedback, and Pareto-efficient search. Read [How GEPA Works](https://mintlify.wiki/gepa-ai/gepa/concepts/how-it-works) for the underlying optimization loop.

## What a Run Produces

An optimizer run writes a stable evidence ledger:

- `optimizer-summary.json` records the selected candidate, score summary, per-case live scores, budgets, and artifact paths.
- `candidates.json` records every candidate with stable candidate IDs so scores can be traced back to prompts or other candidate surfaces.
- `rollout.json`, `score.json`, and `side_info.json` capture per-case execution evidence, grader output, feedback, errors, and ASI inputs.

> [!NOTE]
> GEPA may also emit internal scratch directories such as `generated_best_outputs_valset/`. These are useful for GEPA internals, but they are not the stable evidence contract.

## Learn More

- [Contract references](skills/optimizespec-common/references/core/reference-contracts.md) for runner, grader, ASI, candidate, optimizer, runtime, evidence, and verification contracts.
- [TECHNICAL.md](TECHNICAL.md) for architecture, package boundaries, and release notes.
- [How GEPA Works](https://mintlify.wiki/gepa-ai/gepa/concepts/how-it-works) for GEPA's reflective evolutionary optimization loop.
- [DEVELOPMENT.md](DEVELOPMENT.md) for local development, package checks, and live reference test commands.

## Acknowledgements

OptimizeSpec builds on [OpenSpec](https://github.com/Fission-AI/OpenSpec)'s spec-driven development approach. 

## License

MIT
