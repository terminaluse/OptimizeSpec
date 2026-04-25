# Python Managed Agent Example

This directory contains the original Python prototype for OptimizeSpec's Claude Managed Agents and GEPA loop. It is reference harness and regression-test material, not the public OptimizeSpec package.

Use it when you need to inspect a working Managed Agents evaluator, candidate compiler, GEPA optimization wrapper, or evidence-ledger writer. Normal OptimizeSpec CLI usage is implemented by the TypeScript package at the repository root.

Reference agent inputs live at `tests/fixtures/reference-agents/`. Generated optimization systems and evidence ledgers should be created in temporary test directories or ignored `runs/` directories, not committed under this example.

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
