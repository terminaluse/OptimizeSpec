# Python Managed Agent Reference Package

This directory is a vendored runnable Python reference package for OptimizeSpec's Claude Managed Agents and GEPA loop. It is a complete executable implementation of `references/core/live-eval-runner-contract.md`: package metadata, dependency instructions, source code, live eval commands, live optimizer commands, and smoke/test instructions all live here.

Use it when you need to inspect or adapt a working Managed Agents evaluator, candidate compiler, GEPA optimization wrapper, live session runner, outcome capture loop, runtime-neutral rollout record writer, or evidence-ledger writer. Normal OptimizeSpec CLI usage may be implemented elsewhere in a host repo; this package is the concrete Python runtime reference for Claude Managed Agents apply and verify work.

The runtime uses the Anthropic Research Preview Managed Agents SDK surface with the `managed-agents-2026-04-01-research-preview` beta. The exact preview SDK wheel is pinned in `requirements-managed-agents-preview.txt`.

The live session loop in `src/optimizespec/runtime.py` intentionally drains outcome evaluation events after `session.status_idle`. Keep the `outcome_evaluation_in_progress` gate when adapting this package; otherwise a run can finish before `span.outcome_evaluation_end` is observed.

Rollout evidence written by `src/optimizespec/evaluator.py` and `src/optimizespec/self_improvement.py` uses runtime-neutral top-level fields: candidate id, eval case id, status, final output, trace summary, tool activity, usage, errors, timeout, cleanup, timestamps, score input references, and runtime metadata. Claude-specific Agent, Environment, Session, beta/header, file, skill, subagent, and cleanup details are nested under runtime metadata.

## Local Test Setup

From the repository root, use the maintained setup script. It creates or reuses a dedicated virtual environment outside this package, installs normal package dependencies, and installs the Managed Agents preview SDK requirements:

```bash
scripts/setup-python-managed-agent-example.sh
```

Then run the package health script from the repository root. It is live-only and requires `ANTHROPIC_API_KEY` with Managed Agents preview access:

```bash
ANTHROPIC_API_KEY=... scripts/test-python-managed-agent-example.sh
```

Both scripts fail if bytecode, build metadata, local env files, run outputs, or other generated artifacts are written into this skill package.

Run the live smoke example with an API key that has Research Preview access:

```bash
ANTHROPIC_API_KEY=... .venv/optimizespec-py-managed-agent-example/bin/python -m optimizespec.cli live-eval --run-dir runs/py-managed-agent-preview-wheel-smoke --max-runtime-seconds 120
ANTHROPIC_API_KEY=... .venv/optimizespec-py-managed-agent-example/bin/python -m optimizespec.cli live-optimize --run-dir runs/py-managed-agent-live-optimize --max-metric-calls 8 --max-runtime-seconds 120
```

A successful smoke run writes an evidence ledger under the run directory. `live-optimize` also writes `optimizer-summary.json` with the best candidate id, score summary, per-case live score manifest, budgets, and evidence locations. The optimizer `candidates.json` artifact is normalized after the GEPA run so every entry has `candidate_id`, `candidate_index`, and nested candidate fields. In the validated reference run, the demo produced output `a|b|c|d`, score `1.0`, `outcome_result: satisfied`, `outcome_success: 1.0`, and no errors or cleanup warnings.

## Package Map

- `src/optimizespec/runtime.py`: live Claude Managed Agents session lifecycle, preview beta setup, streamed event capture, timeout/interrupt behavior, outcome definition, output-file retrieval, idle settle polling, archive retries, and cleanup.
- `src/optimizespec/evaluator.py`: per-case live rollout execution, grading side information, score records, and runtime-neutral rollout records.
- `src/optimizespec/optimizer.py`: GEPA optimization loop integration that scores candidates through live rollouts.
- `src/optimizespec/candidate.py`: mutable candidate bundle, prompt rendering, skills, subagents, environment config, and task prompt/rubric rendering.
- `src/optimizespec/self_improvement.py`: durable run ledger orchestration.
- `src/optimizespec/cli.py`: `live-eval`, `live-optimize`, demo, compare, and candidate-inspection command entry points for live verification.
- `requirements-managed-agents-preview.txt`: exact Research Preview Python SDK wheel URL.
