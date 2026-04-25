## Target Agent

This change manually builds a complete repo-local GEPA self-improvement system around a small deterministic target. The target candidate is a `dict[str, str]` with an `answer_template` field that controls how outputs are produced for exact-match eval cases.

## Improvement Target

The seed candidate intentionally returns `wrong` for every case. The self-improvement system should evaluate that failure, compare it with a corrected candidate, run optimization, and persist a full evidence ledger that a reviewer can inspect.

## Evidence Model

The runner writes a run manifest, candidate registry, evaluation summaries, per-case score records, judge records, ASI records, rollout records, comparison records, optimizer lineage, leaderboard records, and a promotion decision under `runs/.../evidence/`.

## Contract References

- `skills/optimizespec-common/references/eval-system-evidence.md`
- `skills/optimizespec-common/references/runner-contract.md`
- `skills/optimizespec-common/references/optimizer-contract.md`
- `skills/optimizespec-common/references/verification-contract.md`
