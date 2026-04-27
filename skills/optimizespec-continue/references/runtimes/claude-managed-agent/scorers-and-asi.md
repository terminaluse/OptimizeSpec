# Scorers and ASI Reference

Claude Managed Agents graders consume live rollout records. Score the final output or report and use trace/runtime metadata when expectations depend on runtime behavior. Static prompt-text coverage can support diagnostics, but the primary objective score comes from live rollout evidence.

## Scorer Types

- `exact_match`: string equality.
- `json_match`: parse JSON and compare structures.
- `file_exists`: verify an expected generated file.
- `custom`: repo-owned scorer function.
- `rubric`: model or human qualitative judgement mapped to a numeric score.

Prefer deterministic scorers when the success condition is exact. Use qualitative rubric scoring for judgment-heavy tasks.

Every scorer plan should state why the grader can be trusted. Include the grader type, calibration examples, known reliability risks, and human review triggers. LLM graders need a tight rubric and constrained score output before they are used as GEPA optimization feedback.

For BotVisibility-style agents, grade the actual report and trace:

- Report sections, category table, findings table, recommendations, limitations, and evidence citations.
- Effective denominator handling when items are N/A.
- CLI-only Agent-Native items that require authenticated API evidence.
- Unsupported or speculative claims.
- Trace behavior such as the two-round fetch policy and maximum Round 2 fetches.

## Metric Roles

- Optimized metric: the score GEPA should improve.
- Diagnostic metrics: extra signals GEPA can use for reflection, such as latency, cost, formatting, or tool-use quality.
- Guardrail metrics: metrics that can block best-candidate selection or optional promotion even when the optimized metric improves.

System-loop metrics prove the eval runner and optimizer executed. Agent quality metrics prove the agent improved on behavior users care about. Keep these separate in compare output and ASI.

## ASI Shape

```json
{
  "Input": "...",
  "Expected": "...",
  "Actual": "...",
  "Feedback": "...",
  "Error": null,
  "Agent Trajectory": [],
  "Runtime": {
    "setup_error": null,
    "runtime_metadata": {
      "agent_id": "...",
      "agent_version": 1,
      "environment_id": "...",
      "session_id": "..."
    },
    "usage": {},
    "cleanup": {}
  },
  "scores": {
    "correctness": 1.0,
    "latency_inv": 0.2,
    "cost_inv": 0.01
  },
  "system_prompt_specific_info": {
    "Feedback": "..."
  }
}
```

When a failure is caused by missing credentials, preview SDK mismatch, permissions, environment setup, timeout, or cleanup behavior, put that in `Runtime.setup_error` or a runtime-specific diagnostic. Keep field-specific candidate feedback for mutable fields that can actually improve live behavior.

## Quality Checklist

- Specific: "expected X, got Y" beats "wrong".
- Causal: explain why the result failed or succeeded.
- Actionable: suggest which behavior or field should change.
- Structured: use consistent keys across cases.
- Balanced: include success feedback so reflection preserves good behavior.
- Higher-is-better: invert latency, cost, or error metrics before putting them in `scores`.
