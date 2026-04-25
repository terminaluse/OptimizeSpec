## Runner Invocation

The manual runner is `manual_self_improve.py`. It exposes `show-candidate`, `eval`, `compare`, `optimize`, and `verify`.

## Candidate Surface

The mutable fields are `answer_template` and `reflection_guidance`. The executor uses `answer_template.format(input=case.input, expected=case.expected)` to produce output. `reflection_guidance` is persisted for GEPA reflection context and field-specific ASI.

## Eval Design

The eval suite contains exact-match train and validation cases. The seed candidate fails all cases. The reference candidate and expected GEPA-improved candidate use `{input}` to echo the case input exactly.

## Evidence Ledger

The runner writes the following durable structure under each run directory:

```text
evidence/
  manifest.json
  candidate-registry.json
  evaluations/<candidate-id>/summary.json
  evaluations/<candidate-id>/cases/<case-id>/score.json
  evaluations/<candidate-id>/cases/<case-id>/judge.json
  evaluations/<candidate-id>/cases/<case-id>/side_info.json
  evaluations/<candidate-id>/cases/<case-id>/rollout.json
  comparisons/comparison.json
  optimizer/lineage.json
  optimizer/leaderboard.json
  optimizer/events.jsonl
  promotion.json
```

## Optimizer Lineage

The live mode calls GEPA through `optimize_candidate`. The reference mode records the known improved candidate so deterministic tests can exercise the same output and promotion paths without live credentials.

## Verification Plan

`verify` checks the evidence ledger shape, candidate registry, per-case evidence records, comparison output, optimizer lineage, leaderboard, events log, and promotion decision.
