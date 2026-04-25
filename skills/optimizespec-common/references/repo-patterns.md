# Local Repo Patterns

This repo provides concrete GEPA plus Claude Managed Agents patterns.

## Files

- `examples/python-managed-agent/src/optimizespec/candidate.py`: `dict[str, str]` candidate surface, structured compilation, canonicalization.
- `examples/python-managed-agent/src/optimizespec/runtime.py`: Managed Agent resource creation, sessions, event streaming, output collection, cleanup.
- `examples/python-managed-agent/src/optimizespec/evaluator.py`: evaluator returning `(score, side_info)`, scored failures, run artifact persistence.
- `examples/python-managed-agent/src/optimizespec/optimizer.py`: `optimize_anything(...)`, train/val sets, reflection prompts, compare flow.
- `examples/python-managed-agent/src/optimizespec/self_improvement.py`: portable eval case schema, scorer templates, ASI builder, direct eval, compare, GEPA optimize wrapper.

## Adaptation Rule

Use these as reference patterns. Do not blindly copy the package layout into agent projects. Reuse each project's existing factories, commands, test conventions, and dependency management.
