# Python Managed Agent Reference Package

This directory is a vendored runnable Python reference package for OptimizeSpec's Claude Managed Agents and GEPA loop. It lives inside the skill reference tree so an agent using the OptimizeSpec skill can copy, adapt, and test a live Managed Agents executor without depending on repo-level examples.

Use it when you need to inspect or adapt a working Managed Agents evaluator, candidate compiler, GEPA optimization wrapper, live session runner, outcome capture loop, or evidence-ledger writer. Normal OptimizeSpec CLI usage may be implemented elsewhere in a host repo; this package is the concrete Python runtime reference for Claude Managed Agents apply and verify work.

The runtime uses the Anthropic Research Preview Managed Agents SDK surface with the `managed-agents-2026-04-01-research-preview` beta. The exact preview SDK wheel is pinned in `requirements-managed-agents-preview.txt`.

The live session loop in `src/optimizespec/runtime.py` intentionally drains outcome evaluation events after `session.status_idle`. Keep the `outcome_evaluation_in_progress` gate when adapting this package; otherwise a run can finish before `span.outcome_evaluation_end` is observed.

## Local Test Setup

Run from a scratch copy so package build metadata and bytecode artifacts do not get written into the installed skill folder:

```bash
work_dir="$(mktemp -d)"
cp -R . "$work_dir/python-managed-agent-package"
cd "$work_dir/python-managed-agent-package"
uv venv
source .venv/bin/activate
uv pip install -e '.[dev]'
uv pip install -r requirements-managed-agents-preview.txt
```

Direct installs from the skill folder can create `*.egg-info` or `__pycache__` artifacts inside the installed skill, so prefer the scratch-copy flow above.

Run the live smoke example with an API key that has Research Preview access:

```bash
ANTHROPIC_API_KEY=... .venv/bin/python -m optimizespec.cli eval-demo --run-dir runs/py-managed-agent-preview-wheel-smoke --max-runtime-seconds 120
```

A successful smoke run writes an evidence ledger under the run directory. In the validated reference run, the demo produced output `a|b|c|d`, score `1.0`, `outcome_result: satisfied`, `outcome_success: 1.0`, and no errors or cleanup warnings.

## Package Map

- `src/optimizespec/runtime.py`: live Claude Managed Agents session lifecycle, preview beta setup, streamed event capture, outcome definition, output-file retrieval, and cleanup.
- `src/optimizespec/evaluator.py`: per-case rollout execution and evidence records.
- `src/optimizespec/optimizer.py`: GEPA optimization loop integration.
- `src/optimizespec/candidate.py`: mutable candidate bundle, prompt rendering, skills, subagents, environment config, and task prompt/rubric rendering.
- `src/optimizespec/self_improvement.py`: durable run ledger orchestration.
- `src/optimizespec/cli.py`: `eval-demo` and related command entry points for local verification.
- `requirements-managed-agents-preview.txt`: exact Research Preview Python SDK wheel URL.
