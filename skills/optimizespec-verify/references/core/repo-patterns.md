# Agent Project Patterns

Use these patterns when adapting OptimizeSpec to an agent project. They are included here so each installed skill folder has the context it needs.

## Candidate Surface

Represent mutable candidate state as structured fields or files with stable identifiers. Keep candidate ids, parent ids, mutation summaries, and rollback paths explicit. Canonicalize candidate data before scoring so repeated runs are comparable.

## Runtime Integration

Reuse the project's existing agent factories, tool wiring, environment setup, session or request execution, event streaming, output collection, and cleanup conventions. Prefer the existing runtime path when the project has one.

## Evaluator Shape

Each rollout should return a numeric score plus Actionable Side Information. Failed rollouts still need scored failure records, captured errors, and enough context for the optimizer or reviewer to understand the failure.

## Optimizer Flow

Keep train and validation cases separate. Record optimizer inputs, candidate mutations, selected and rejected candidates, leaderboard entries, and promotion decisions. Compare baseline and candidate outputs on the same eval cases.

## Adaptation Rule

Adapt these patterns to the target project's factories, commands, test conventions, and dependency management.
