# OptimizeSpec

OptimizeSpec helps you make an agent better in a measured way, even if you have never built an eval suite or optimization loop before.

You start with a plain-language goal, such as "make support-triage answers more complete." The OptimizeSpec skills guide your coding agent through turning that goal into eval cases, scoring criteria, a runner that calls your real agent, and an optimization loop.

You do not need to know the full system shape before you start. The skills draft the proposal, identify unknowns, ask for confirmation where needed, and then implement the eval runner, scorer, optimizer, adapter, and evidence ledger once the plan is clear.

## What You Get

- A structured workflow to work through the details of an optimization system for your agent.
- Production-equivalent evals against your real agent runtime, tools, skills, MCP servers, environment, and permissions.
- Traceable optimization results with candidate IDs, per-case rollouts, scores, feedback, and a selected best candidate.

## Quick Start

1. Install the CLI:

```bash
bun install -g optimizespec
```

2. Then install the skills:

```bash
npx skills add terminaluse/optimizespec --skill '*'
```

3. Initialize the project metadata once:

```bash
optimizespec init
```

Now create or update your optimization system with the skills:

```text
/optimizespec-new
Create a change named improve-agent-output that improves the agent's answer quality on support triage tasks.
```

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

## How OptimizeSpec Works

OptimizeSpec skills include contracts for building optimization systems for agents. Your coding agent uses those contracts to implement the runner, scorer, optimizer, adapter, evidence ledger, candidate registry, and verification flow for your agent.

The core contracts are runtime-neutral. The skills includes a reference system for Python Claude Managed Agents, and contributions for other hosted agent runtimes and languages are welcome.

### How the Self-Improvement Works

The generated self-improvement system uses GEPA's Optimize Anything API as the optimization engine. OptimizeSpec defines the eval runner, scorer, candidate surface, ASI feedback, and evidence ledger; GEPA uses those pieces to evaluate candidates, reflect on live failures, propose mutations, and select better candidates.

GEPA is a reflective evolutionary optimizer: it improves text-representable candidates by combining scores, traces, feedback, and Pareto-efficient search. Read [How GEPA Works](https://mintlify.wiki/gepa-ai/gepa/concepts/how-it-works) for the underlying optimization loop.

### What Spec Artifacts Get Created

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

### What a Run Produces

An optimizer run outputs:

- `optimizer-summary.json` records the selected candidate, score summary, per-case live scores, budgets, and artifact paths.
- `candidates.json` records every candidate with stable candidate IDs so scores can be traced back to prompts or other candidate surfaces.
- `rollout.json`, `score.json`, and `side_info.json` capture per-case execution evidence, grader output, feedback, errors, and ASI inputs.

## Learn More

- [Contract references](skills/optimizespec-common/references/core/reference-contracts.md) for runner, grader, candidate, optimizer, and runtime contracts.
- [TECHNICAL.md](TECHNICAL.md) for architecture, package boundaries, and release notes.
- [How GEPA Works](https://mintlify.wiki/gepa-ai/gepa/concepts/how-it-works) for GEPA's reflective evolutionary optimization loop.
- [DEVELOPMENT.md](DEVELOPMENT.md) for local development.

## Acknowledgements

OptimizeSpec is only possible due to all the great work [Lakshya](https://x.com/LakshyAAAgrawal) has done on GEPA.

OptimizeSpec's spec-driven development approach is strongly inspired by [OpenSpec](https://github.com/Fission-AI/OpenSpec) (we highly recommend it; this repo was build using OpenSpec)

## License

MIT
