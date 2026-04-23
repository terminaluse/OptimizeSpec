## 1. Fixture and Artifacts

- [x] 1.1 Create an existing-agent fixture for this repo's Claude Managed Agent prototype
- [x] 1.2 Create proposal, design, spec, tasks, eval cases, and seed candidate for the meta-eval
- [x] 1.3 Define required concepts for proposal, design, specs/tasks, eval cases, and apply-plan generation

## 2. Meta-Eval Runner

- [x] 2.1 Implement generated artifact composition from fixture facts and mutable guidance fields
- [x] 2.2 Implement direct eval, compare, optimize, show-candidate, and generate commands
- [x] 2.3 Implement required-term scoring and field-specific ASI
- [x] 2.4 Persist generated artifacts and rollout artifacts
- [x] 2.5 Implement an end-to-end system-loop eval that runs generate, direct eval, and GEPA optimize

## 3. Verification

- [x] 3.1 Run generated artifact creation
- [x] 3.2 Run direct eval successfully
- [x] 3.3 Run compare successfully
- [x] 3.4 Add regression tests for the existing-agent meta-eval path
- [x] 3.5 Verify the system-loop eval scores `1.0` only after optimization artifacts are produced
