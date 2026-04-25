## 1. Reference Contracts

- [x] 1.1 Add `skills/optimizespec-common/references/eval-system-evidence.md` defining run manifest, candidate registry, per-case scores, judge output, ASI, rollout artifacts, comparison records, optimizer lineage, leaderboard, and promotion decisions.
- [x] 1.2 Add `skills/optimizespec-common/references/runner-contract.md` defining direct eval, compare, optimize, rollout lifecycle, command inputs, command outputs, and failure behavior.
- [x] 1.3 Add `skills/optimizespec-common/references/grader-contract.md` defining numeric scores, qualitative judge output, grader type, calibration, reliability risks, and human review triggers.
- [x] 1.4 Add `skills/optimizespec-common/references/asi-contract.md` defining how actionable side information is captured, stored, and passed into GEPA reflective evolution.
- [x] 1.5 Add `skills/optimizespec-common/references/candidate-surface.md` defining mutable candidate files, immutable eval files, candidate ids, diffs, rollback, and promotion boundaries.
- [x] 1.6 Add `skills/optimizespec-common/references/optimizer-contract.md` defining objective metric, diagnostics, guardrails, candidate selection, lineage, promotion, and rejection evidence.
- [x] 1.7 Add `skills/optimizespec-common/references/managed-agents-runtime-contract.md` defining Claude Managed Agents SDK/header setup, invocation assumptions, rollout records, and preview-feature caveats.
- [x] 1.8 Add `skills/optimizespec-common/references/verification-contract.md` defining deterministic smoke checks, live checks, evidence inspection, and release readiness.
- [x] 1.9 Update or add a common reference index so skills can discover which contract to load for each phase.

## 2. Skill Integration

- [x] 2.1 Update `skills/optimizespec-common/SKILL.md` to describe the reference-contract library and progressive loading rules.
- [x] 2.2 Update proposal/new skill guidance to load criteria-first, candidate surface, grader, and evidence contracts when drafting eval specs.
- [x] 2.3 Update continue/design skill guidance to load runner, optimizer, runtime, grader, ASI, and evidence contracts when designing the eval runner and optimizer system.
- [x] 2.4 Update apply skill guidance, if present, to implement runner, evidence, grader, ASI, optimizer, runtime, and verification contracts.
- [x] 2.5 Update verify skill guidance, if present, to inspect evidence ledger, candidate history, judge outputs, ASI, optimizer lineage, and promotion decisions.
- [x] 2.6 Keep user-facing questions lightweight; the contracts should guide the agent's work without adding a new user-facing phase.

## 3. Templates and Docs

- [x] 3.1 Update `skills/optimizespec-common/assets/templates/proposal.md` with a concise evidence-model expectation and contract references.
- [x] 3.2 Update `skills/optimizespec-common/assets/templates/design.md` with eval runner invocation, rollout lifecycle, evidence ledger, optimizer lineage, and verification sections.
- [x] 3.3 Update `TECHNICAL.md` to explain the reference-contract layer and evidence ledger at a high level.
- [x] 3.4 Avoid duplicating long contract text in README; the README should stay value-focused and link to technical details.

## 4. Validation

- [x] 4.1 Update artifact validation to score whether designs define a durable evidence ledger rather than only aggregate scores.
- [x] 4.2 Update validation to detect missing runner invocation details, rollout persistence, judge output persistence, ASI persistence, optimizer lineage, and promotion decision.
- [x] 4.3 Add or update negative fixtures for aggregate-only scoring, missing judge records, missing ASI records, missing optimizer lineage, and missing promotion evidence.
- [x] 4.4 Add or update positive fixtures that show candidate versions, run records, per-case scores, judge output, ASI, and promotion decisions.
- [x] 4.5 Ensure tests avoid exact markdown prose assertions and instead inspect parsed artifact sections, structured fixture data, or validator behavior.

## 5. Verification

- [x] 5.1 Run `openspec validate shared-reference-contracts`.
- [x] 5.2 Run the deterministic test suite.
- [x] 5.3 Run a local validation smoke that does not require live Anthropic credentials.
- [x] 5.4 If live credentials are available and relevant code changed, run the opt-in live Managed Agents smoke and inspect the emitted evidence ledger.
