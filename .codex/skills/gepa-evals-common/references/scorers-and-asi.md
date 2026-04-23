# Scorers and ASI Reference

## Scorer Types

- `exact_match`: string equality.
- `json_match`: parse JSON and compare structures.
- `file_exists`: verify an expected generated file.
- `custom`: repo-owned scorer function.
- `rubric`: model or human qualitative judgement mapped to a numeric score.

Prefer deterministic scorers when the success condition is exact. Use qualitative rubric scoring for judgment-heavy tasks.

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
    "agent_id": "...",
    "agent_version": 1,
    "environment_id": "...",
    "session_id": "...",
    "usage": {}
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

## Quality Checklist

- Specific: "expected X, got Y" beats "wrong".
- Causal: explain why the result failed or succeeded.
- Actionable: suggest which behavior or field should change.
- Structured: use consistent keys across cases.
- Balanced: include success feedback so reflection preserves good behavior.
- Higher-is-better: invert latency, cost, or error metrics before putting them in `scores`.
