# Workflow Reference

Use OpenSpec as product motivation: lightweight repo-local artifacts, iterative planning, readable Markdown contracts, and an apply step that turns approved artifacts into implementation. OptimizeSpec keeps those ideas focused on agent self-improvement loops.

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

- `proposal.md`: self-improvement contract. Defines the agent being improved, optimization-system location, behavior to improve, success criteria, draft eval contract, examples, scoring intent, qualitative rubric, grader trust, optimizer acceptance, ASI needs, and unknowns.
- `design.md`: technical design. Defines what was found in the agent project, inferred target runtime, eval design, runner invocation, rollout lifecycle, trace capture, scoring, grader strategy, ASI mapping, candidate fields, optimizer configuration, and acceptance rules.
- `specs/*.md`: testable requirements using SHALL/MUST and scenarios.
- `tasks.md`: checkboxed implementation checklist.

## Flow

1. Start with the user outcome and success criteria, not just eval examples.
2. Draft the eval contract from intent and examples, then ask the user to confirm or correct it.
3. Inspect the repo and record whether optimization code will use an existing folder or create a new one.
4. Define candidate fields GEPA may mutate.
5. Define the ASI contract before implementing rollouts.
6. Define eval cases, scorer strategy, grader trust, and optimizer acceptance.
7. Design runtime-specific rollouts using the inferred runtime contracts.
8. Implement direct eval, optimize, compare, and candidate inspection in the recorded folder.
9. Verify criteria quality and ASI quality before trusting optimization results.
