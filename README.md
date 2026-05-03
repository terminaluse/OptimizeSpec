# OptimizeSpec: A plugin to build agent optimization systems

OptimizeSpec helps you make your agent better in a measured way, even if you have never built an eval suite or optimization loop before.

You start with a plain-language goal, such as "make support-triage answers more complete."

OptimizeSpec guides your coding agent through a spec-driven development workflow to turn your request into an eval spec, scoring criteria, and optimization code.

Even if you haven’t collected evals yet, this exercise will give you an understanding of what your evals should look like and what you need to collect.

## What You Get

- A structured workflow for turning an improvement idea into evals, scoring, and optimization code.
- Production-equivalent evals against your real agent runtime, tools, skills, MCP servers, environment, and permissions.
- Traceable optimization results with candidate IDs, per-case rollouts, scores, feedback, and a selected best candidate.

If OptimizeSpec helps you build better agent evals and optimization loops, give us a ⭐!

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
Create an optimization system to improve the agent in this folder
```

Continue until all the spec artifacts are generated:

```text
/optimizespec-continue
```

Implement the spec:

```text
/optimizespec-apply
```


## How OptimizeSpec Works

OptimizeSpec skills include contracts for building optimization systems for agents. Your coding agent uses those contracts to implement the runner, scorer, optimizer, adapter, evidence ledger, candidate registry, and verification flow for your agent.

The core contracts are runtime-neutral. The skills include a reference system for Python Claude Managed Agents, and contributions for other hosted agent runtimes and languages are welcome.

<details>
<summary> How Optimization Works</summary>

The generated optimization system uses GEPA's Optimize Anything API as the optimization engine. OptimizeSpec defines the eval runner, scorer, candidate surface, ASI feedback, and evidence ledger; GEPA uses those pieces to evaluate candidates, reflect on live failures, propose mutations, and select better candidates.

GEPA is a reflective evolutionary optimizer: it improves text-representable candidates by combining scores, traces, feedback, and Pareto-efficient search. Read [How GEPA Works](https://mintlify.wiki/gepa-ai/gepa/concepts/how-it-works) for the underlying optimization loop.

</details>

<details>
<summary> What Spec Artifacts Get Created </summary>

OptimizeSpec keeps planning artifacts in one root folder:

```text
optimizespec/changes/<change-name>/
  proposal.md
  design.md
  specs/
  tasks.md
```

The proposal records where the optimization-system code will live and where run evidence will be written:

```text
## Optimization System Location

- Decision: create new folder|use existing folder
- Path: <repo-relative eval, tooling, or package-adjacent path>
- Import/runtime access plan: <how generated code imports or invokes the real agent modules>
- Run outputs path: runs/
```

`$optimizespec-apply <change-name>` writes runner, scorer, optimizer, adapter, and evidence-ledger code to the recorded executable path.

**Note:** Choose the path based on your repo's structure. The executable optimization system should usually live in an existing eval, test, tooling, or agent package-adjacent folder, where it can import or invoke the real agent, tools, skills, MCP servers, environment configuration, and permissions through a narrow adapter.

</details>

<details>
<summary>What a Run Produces</summary>

An optimizer run outputs:

- `optimizer-summary.json` records the selected candidate, score summary, per-case live scores, budgets, and artifact paths.
- `candidates.json` records every candidate with stable candidate IDs so scores can be traced back to prompts or other candidate surfaces.
- `rollout.json`, `score.json`, and `side_info.json` capture per-case execution evidence, grader output, feedback, errors, and ASI inputs.

</details>

## Learn More

- [Contract references](skills/optimizespec-common/references/core/reference-contracts.md) for runner, grader, candidate, optimizer, and runtime contracts.
- [TECHNICAL.md](TECHNICAL.md) for architecture, package boundaries, and release notes.
- [How GEPA Works](https://mintlify.wiki/gepa-ai/gepa/concepts/how-it-works) for GEPA's reflective evolutionary optimization loop.
- [DEVELOPMENT.md](DEVELOPMENT.md) for local development.

## Acknowledgements

OptimizeSpec is only possible due to all the great work [Lakshya](https://x.com/LakshyAAAgrawal) has done on GEPA.

OptimizeSpec's spec-driven development approach is inspired by [OpenSpec](https://github.com/Fission-AI/OpenSpec) which we highly recommend for daily development.

## License

MIT
