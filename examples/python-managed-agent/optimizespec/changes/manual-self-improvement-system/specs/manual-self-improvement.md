## ADDED Requirements

### Requirement: Manual runner persists the evidence ledger
The manual self-improvement runner SHALL persist a durable evidence ledger for direct eval, compare, optimize, and verify operations.

#### Scenario: Optimization completes
- **WHEN** a seed candidate and selected candidate are compared
- **THEN** the run directory contains manifest, candidate registry, evaluation records, comparison records, optimizer lineage, leaderboard, events, and promotion decision files

### Requirement: Runner supports deterministic and live optimization modes
The manual self-improvement runner SHALL support a deterministic reference mode for structural verification and a GEPA mode for live optimization.

#### Scenario: Deterministic mode runs
- **WHEN** the runner is invoked with `--mode reference`
- **THEN** it records optimizer evidence using the reference improved candidate without requiring live credentials

#### Scenario: GEPA mode runs
- **WHEN** the runner is invoked with `--mode gepa`
- **THEN** it loads `ANTHROPIC_API_KEY` from the environment or `.env`, runs GEPA, compares the selected candidate, and records promotion evidence
