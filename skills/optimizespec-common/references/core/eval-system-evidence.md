# Eval System Evidence Contract

Every applied OptimizeSpec system must persist a run ledger that can be inspected after direct eval, compare, optimize, and promotion decisions. Aggregate scores are not enough; reviewers need candidate versions, case-level evidence, judge output when present, ASI, rollout artifacts, optimizer lineage, and promotion rationale.

## Required Ledger Records

- Run manifest: run id, command, fixture or agent, runtime, start time when available, candidate ids, eval case ids, and output roots.
- Candidate registry: candidate id, parent candidate id when applicable, mutable files or fields, creation reason, source path or diff, and rollback target.
- Evaluation summary: aggregate score, split scores, case list, objective metric, diagnostic metrics, and guardrail metrics.
- Per-case score: score, bounds or direction, criterion measured, scorer identity, feedback, errors, and abstention status when relevant.
- Judge record: grader type, rubric or criterion version, structured output, rationale summary, calibration status, reliability warnings, and human review trigger when present.
- ASI record: actionable side information tied to candidate id and case id, including whether it was passed into GEPA reflection.
- Rollout record: input, output, final answer, trajectory or event summary, generated files, runtime ids, usage, errors, and timeout or cleanup status.
- Comparison record: compared candidates, per-case deltas, aggregate deltas, objective metric movement, guardrail movement, and regression notes.
- Optimizer lineage: candidate parentage, mutation summary, optimizer event log, leaderboard, selected candidate, rejected candidates, and selection reason.
- Promotion decision: promoted candidate or explicit no-promotion decision, compared candidates, metric results, guardrail results, manual review requirement, and rollback path.

## Recommended Layout

```text
runs/<run-id>/
  evidence/
    manifest.json
    candidate-registry.json
    evaluations/<candidate-id>/summary.json
    evaluations/<candidate-id>/cases/<case-id>/score.json
    evaluations/<candidate-id>/cases/<case-id>/judge.json
    evaluations/<candidate-id>/cases/<case-id>/side_info.json
    evaluations/<candidate-id>/cases/<case-id>/rollout.json
    comparisons/<comparison-id>.json
    optimizer/lineage.json
    optimizer/leaderboard.json
    optimizer/events.jsonl
    promotion.json
```

The layout can be adapted to the agent project, but the same records must remain discoverable. Minimal smoke runs may store compact records, yet they still need a manifest, candidate id, case-level scores, rollout evidence, ASI, and a promotion decision or no-promotion record.

## Evidence Boundaries

System-loop evidence proves the machinery ran: commands executed, files were written, scorers returned, and optimizer calls completed. Agent-quality evidence proves the agent improved on user-meaningful criteria. System-loop success alone supports readiness, not improvement claims.

## Review Checklist

- The ledger identifies every evaluated candidate version.
- Per-case evidence exists for scores, judge output when present, ASI, and rollouts.
- Comparison and optimizer records explain accepted and rejected candidates.
- Promotion evidence states why a candidate was or was not promoted.
- Failures preserve enough diagnostics to reproduce or investigate them.
