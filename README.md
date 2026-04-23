# Agent GEPA

Create a self-improvement system for your agent.

Agent GEPA gives you a repeatable loop for improving a Claude Managed Agent with evidence instead of guesswork. You define evals, run the agent, capture scores and useful feedback, let GEPA propose better instructions/configuration, and compare the improved candidate against the baseline.

Most agent work still looks like manual prompt tuning: try a change, run a few examples, hope it generalizes. Agent GEPA turns that into a workflow:

1. Describe what good behavior means.
2. Run evals against the current agent.
3. Capture numeric scores plus Actionable Side Information.
4. Let GEPA mutate prompts, skills, environment settings, rubrics, and subagent specs.
5. Compare the new candidate against the old one on the same evals.

The result is not just a benchmark. It is an improvement loop with artifacts: what changed, why it changed, which cases improved, and what still failed.

## What You Get

- A working Claude Managed Agents runtime wired to GEPA.
- A candidate model GEPA can optimize across prompts, skills, environment config, rubrics, and subagents.
- Direct eval, optimize, and compare commands.
- A repo-local skill pack for creating eval-driven self-improvement workflows in other agent projects.
- Validation fixtures that prove eval generation, scoring, comparison, optimization, and failure handling all run end to end.

## Quick Start

Install the repo:

```bash
uv venv
source .venv/bin/activate
uv pip install -e '.[dev]'
```

Run the local test suite:

```bash
pytest -q
```

Run a deterministic eval smoke test:

```bash
agent-gepa self-eval \
  --cases skills/gepa-evals-common/assets/templates/eval-cases.yaml \
  --candidate skills/gepa-evals-common/assets/templates/seed-candidate.yaml \
  --run-dir runs/self-eval-smoke
```

That command does not call the live API. It proves the self-improvement eval runner can load eval cases, load a candidate, execute rollouts, score them, and persist ASI artifacts.

## Live Managed Agents

Live runs require Anthropic Research Preview access for Claude Managed Agents.

Install the Research Preview SDK:

```bash
uv pip install -r requirements-managed-agents-preview.txt
```

Set your API key:

```bash
export ANTHROPIC_API_KEY=...
```

Run one live evaluation:

```bash
agent-gepa eval-demo --max-runtime-seconds 300
```

Run a small live optimization smoke:

```bash
agent-gepa optimize-demo --max-metric-calls 1 --max-runtime-seconds 300
```

Run the live improvement sanity check:

```bash
AGENT_GEPA_RUN_LIVE_IMPROVEMENT=1 pytest tests/test_gepa_improvement_live.py -q
```

The sanity check starts from a deliberately weak candidate, runs GEPA, and asserts the optimized candidate improves from `0.0` to `1.0`.

## Commands

| Command | What it does |
| --- | --- |
| `pytest -q` | Runs the default local test suite. Live GEPA tests are skipped unless explicitly enabled. |
| `agent-gepa self-show-candidate --candidate <file>` | Prints a self-improvement candidate so you can inspect the mutable fields. |
| `agent-gepa self-eval --cases <cases.yaml> --candidate <candidate.yaml>` | Runs deterministic eval cases and writes rollout artifacts, scores, and ASI. |
| `agent-gepa self-compare --cases <cases.yaml> --baseline <a.yaml> --candidate <b.yaml>` | Compares two candidates on the same eval cases and reports deltas. |
| `agent-gepa eval-demo` | Runs one live Claude Managed Agents evaluation. Best first live check. |
| `agent-gepa optimize-demo --max-metric-calls 1` | Runs a small live GEPA optimization smoke. |
| `agent-gepa compare-demo` | Runs optimize plus before/after live evaluations across the demo suite. Useful, but slower and more expensive. |

`--max-metric-calls` is GEPA's eval budget. Higher values give GEPA more chances to test and improve candidates, but each call can mean another live rollout.

## Skills For Other Agent Projects

The `skills/` folder contains a workflow a coding agent can use to create evals and apply GEPA to another Claude Managed Agents project:

```text
skills/
  gepa-evals-new/
  gepa-evals-continue/
  gepa-evals-apply/
  gepa-evals-verify/
  gepa-evals-common/
```

Use them in this order:

1. `gepa-evals-new`: define the target agent, eval objective, input/output examples, scoring, qualitative rubric, and ASI needs.
2. `gepa-evals-continue`: create the design, specs, and task artifacts.
3. `gepa-evals-apply`: implement the eval runner, scorers, compare path, and GEPA optimizer.
4. `gepa-evals-verify`: check artifact completeness, ASI quality, direct eval, compare, and optimize readiness.

If your coding agent loads repo-local skills, point it at this repository and ask it to use the relevant `gepa-evals-*` skill. If it expects global skills, copy the needed `skills/gepa-evals-*` folders into that skills directory.

## Current Scope

Agent GEPA currently focuses on Claude Managed Agents. Other runtimes can be added later, but this first version keeps the runtime surface narrow so the eval and optimization loop can be validated end to end.

For implementation details, candidate fields, preview SDK notes, validation internals, and heavier commands, see [TECHNICAL.md](TECHNICAL.md).

## License

MIT
