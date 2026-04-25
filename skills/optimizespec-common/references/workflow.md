# Workflow Reference

Use OpenSpec as product motivation: lightweight repo-local artifacts, iterative planning, readable Markdown contracts, and an apply step that turns approved artifacts into implementation. Do not copy OpenSpec feature-for-feature.

## Default Directory

```text
optimizespec/
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

- `proposal.md`: self-improvement contract. Defines target agent, behavior to improve, success criteria, draft eval contract, examples, scoring intent, qualitative rubric, grader trust, optimizer acceptance, ASI needs, and unknowns.
- `design.md`: technical design. Defines target repo discovery, Managed Agents runtime, eval design, runner invocation, rollout lifecycle, trace capture, scoring, grader strategy, ASI mapping, candidate fields, optimizer configuration, and acceptance rules.
- `specs/*.md`: testable requirements using SHALL/MUST and scenarios.
- `tasks.md`: checkboxed implementation checklist.

## Flow

1. Start with the user outcome and success criteria, not just eval examples.
2. Draft the eval contract from intent and examples, then ask the user to confirm or correct it.
3. Define candidate fields GEPA may mutate.
4. Define the ASI contract before implementing rollouts.
5. Define eval cases, scorer strategy, grader trust, and optimizer acceptance.
6. Design Managed Agent rollouts.
7. Implement direct eval, optimize, compare, and candidate inspection.
8. Verify criteria quality and ASI quality before trusting optimization results.
