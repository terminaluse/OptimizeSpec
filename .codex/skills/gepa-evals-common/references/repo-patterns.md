# Local Repo Patterns

This repo provides concrete GEPA plus Claude Managed Agents patterns.

## Files

- `src/claude_gepa/candidate.py`: `dict[str, str]` candidate surface, structured compilation, canonicalization.
- `src/claude_gepa/runtime.py`: Managed Agent resource creation, sessions, event streaming, output collection, cleanup.
- `src/claude_gepa/evaluator.py`: evaluator returning `(score, side_info)`, scored failures, run artifact persistence.
- `src/claude_gepa/optimizer.py`: `optimize_anything(...)`, train/val sets, reflection prompts, compare flow.
- `src/claude_gepa/self_improvement.py`: portable eval case schema, scorer templates, ASI builder, direct eval, compare, GEPA optimize wrapper.

## Adaptation Rule

Use these as reference patterns. Do not blindly copy the package layout into target repos. Reuse existing target repo factories, commands, test conventions, and dependency management.
