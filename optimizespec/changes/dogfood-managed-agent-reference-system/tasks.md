## 1. Generated System Structure

- [x] 1.1 Create the generated dogfood system under `runs/optimizespec-dogfood/dogfood-managed-agent-reference-system`.
- [x] 1.2 Add a command script that can run from the generated system directory and resolve the repository root.
- [x] 1.3 Add a README that documents direct eval, compare, optimize, show-candidate, verify, and run-all commands.

## 2. Harness Adapter

- [x] 2.1 Import and reuse `optimizespec.eval_validation` from `examples/py-claude-managed-agent/src`.
- [x] 2.2 Use `optimizespec-managed-agent` as the default fixture.
- [x] 2.3 Add optional `.env` loading for live credentials without requiring credentials for deterministic commands.
- [x] 2.4 Expose `show-candidate` as JSON for the default seed candidate and mutable fields.

## 3. Runner Operations

- [x] 3.1 Implement `direct-eval` using the existing fixture-backed eval command.
- [x] 3.2 Implement `compare` using the existing fixture-backed compare command.
- [x] 3.3 Implement `optimize` using the existing GEPA/eval-validation optimizer with a configurable metric-call budget.
- [x] 3.4 Implement `run-all` to execute generate, direct eval, compare, optimize, and verify in order.

## 4. Evidence And Verification

- [x] 4.1 Persist generated artifacts, command logs, direct eval evidence, comparison evidence, optimizer lineage, leaderboard, and promotion evidence through the existing harness.
- [x] 4.2 Implement `verify` so missing evidence records produce a non-zero exit code.
- [x] 4.3 Print deterministic system-loop readiness separately from live Managed Agent improvement claims.

## 5. Local Validation

- [x] 5.1 Run the generated `show-candidate` command.
- [x] 5.2 Run the generated `run-all` command with a fresh run directory.
- [x] 5.3 Inspect `verification/verification.json` and required evidence files.
- [x] 5.4 Run `optimizespec validate dogfood-managed-agent-reference-system`.
