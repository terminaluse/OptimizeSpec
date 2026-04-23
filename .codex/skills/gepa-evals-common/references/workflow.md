# Workflow Reference

Use OpenSpec as product motivation: lightweight repo-local artifacts, iterative planning, readable Markdown contracts, and an apply step that turns approved artifacts into implementation. Do not copy OpenSpec feature-for-feature.

## Default Directory

```text
gepa-evals/
  changes/
    <change-name>/
      proposal.md
      design.md
      specs/
        <capability>.md
      tasks.md
      eval-cases.yaml
      seed-candidate.yaml
```

## Artifact Roles

- `proposal.md`: self-improvement contract. Defines target agent, behavior to improve, examples, scoring intent, qualitative rubric, ASI needs, and unknowns.
- `design.md`: technical design. Defines target repo discovery, Managed Agents runtime, runner invocation, rollout lifecycle, trace capture, ASI mapping, candidate fields, and optimizer configuration.
- `specs/*.md`: testable requirements using SHALL/MUST and scenarios.
- `tasks.md`: checkboxed implementation checklist.

## Flow

1. Start with the feedback loop GEPA needs, not just eval examples.
2. Define candidate fields GEPA may mutate.
3. Define the ASI contract before implementing rollouts.
4. Define eval cases and scorers.
5. Design Managed Agent rollouts.
6. Implement direct eval, optimize, compare, and candidate inspection.
7. Verify ASI quality before trusting optimization results.
