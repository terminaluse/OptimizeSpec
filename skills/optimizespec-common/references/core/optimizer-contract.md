# Optimizer Contract

The optimizer contract defines how GEPA chooses candidates, which evidence it consumes, and what must be recorded before a candidate can be accepted.

## Objective and Metrics

- Name the optimized metric and ensure it reflects the primary success criterion.
- Name diagnostic metrics that help interpret behavior, such as ASI quality, grader trust, latency, or cost.
- Name guardrail metrics that can block promotion.
- Define regression tolerance for hard contracts, guardrails, and softer prose or behavior metrics.

## Candidate Selection

For each proposed candidate, record parent id, mutation summary, train score, validation score when available, diagnostics, guardrails, and rejection reason if it is not selected.

## Lineage and Leaderboard

Persist optimizer lineage and leaderboard records. The lineage should explain parentage and mutation events. The leaderboard should make it easy to compare candidate ids, objective scores, diagnostics, guardrails, and selected status.

## Promotion and Rejection Evidence

Promotion requires a recorded decision. The decision must cite compared candidates, objective metric movement, guardrail results, manual review requirement, and rollback path. Rejections should preserve enough evidence to explain why a candidate was not kept.

## Budget and Safety

Record metric-call budget, timeout, reflection model, component selector, and any live-credential requirement. Do not spend live budget unless the user or environment explicitly enables it.
