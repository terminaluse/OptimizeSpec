# Verification Contract

Verification decides whether an OptimizeSpec system is ready to use. It must inspect emitted evidence, not only command exit codes or printed aggregate scores.

## Deterministic Smoke

Run local checks that require no live Anthropic credentials. A deterministic smoke should verify:

- required commands can be invoked
- run manifest exists
- candidate registry exists
- per-case score, judge, ASI, and rollout records exist
- comparison evidence exists
- optimizer lineage and leaderboard exist
- promotion or no-promotion decision exists
- verification output states residual risks

## Live Smoke

When live credentials and runtime access are available, run the smallest useful live smoke for the inferred runtime. Inspect run manifest, rollout records, per-case scores, judge output when present, ASI, optimizer lineage, and promotion decision before reporting readiness.

## Readiness Reporting

Report system-loop readiness separately from agent-quality improvement. If only deterministic machinery checks ran, say that live agent-quality evidence is still pending. If evidence is missing, verification fails even when commands returned zero.

## Failure Report

A useful failure report names missing artifacts, failed commands, runtime blockers, grader reliability risks, and whether manual review is required.
