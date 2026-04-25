# Python Managed Agent Example

This directory contains the original Python prototype for OptimizeSpec's Claude Managed Agents and GEPA loop. It is reference and regression-test material, not the public OptimizeSpec package.

Use it when you need to inspect a working Managed Agents evaluator, candidate compiler, GEPA optimization wrapper, or evidence-ledger example. Normal OptimizeSpec CLI usage is implemented by the TypeScript package at the repository root.

## Local Test Setup

```bash
uv venv
source .venv/bin/activate
uv pip install -e examples/python-managed-agent[dev]
```

Live Managed Agents runs also require the preview SDK requirements:

```bash
uv pip install -r examples/python-managed-agent/requirements-managed-agents-preview.txt
```
