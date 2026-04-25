# ASI Contract

Actionable Side Information is the feedback passed from evaluation into GEPA reflective evolution. It must be specific, causal, and tied to candidate fields so the reflection model can improve behavior without losing what already works.

## Required Shape

ASI should include:

- `Input`
- `Expected`
- `Actual`
- `Feedback`
- `Error`
- `Agent Trajectory`
- `Runtime`
- `scores`
- field-specific sections such as `system_prompt_specific_info`

The `scores` object must contain higher-is-better metrics. Field-specific sections should include the current value or pointer, feedback, and any field-local score signals.

## Persistence

Persist ASI for every candidate and eval-case pair, even when the rollout succeeds. Store whether the ASI was passed into GEPA reflection, and keep enough case and candidate identifiers to trace it back to the evidence ledger.

## Quality Rules

- Specific: state what was expected and what happened.
- Causal: explain why the behavior succeeded or failed.
- Actionable: identify the field or behavior likely to improve the result.
- Balanced: preserve success feedback so GEPA does not erase useful behavior.
- Structured: keep keys consistent across cases.

## Failure Handling

Timeouts, runtime errors, grader abstentions, and missing outputs still need ASI. In failure cases, `Error`, `Agent Trajectory`, runtime ids, and generated files become the primary debugging evidence.
