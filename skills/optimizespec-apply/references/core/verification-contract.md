# Verification Contract

Verification decides whether an OptimizeSpec system is ready to use. It must inspect emitted evidence, not only command exit codes or printed aggregate scores.

## Live Smoke

Verification requires live credentials and runtime access for the inferred agent runtime. Run the smallest useful live smoke and verify:

- required commands can be invoked
- run manifest exists
- candidate registry exists
- per-case score, judge, ASI, and rollout records exist
- comparison evidence exists
- optimizer lineage and leaderboard exist
- promotion or no-promotion decision exists
- verification output states residual risks

Live verification evidence must come from the real runtime. Local fixture, dry-run, static prompt, template-output, or no-credential checks can support readiness diagnostics, but they do not replace live optimization evidence.

## Readiness Reporting

Report readiness only from live evidence. If credentials or runtime access are missing, verification fails with a runtime blocker. If evidence is missing, verification fails even when commands returned zero.

## Failure Report

A useful failure report names missing artifacts, failed commands, runtime blockers, grader reliability risks, and whether manual review is required.
