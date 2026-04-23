Create evals and a GEPA optimizer for the existing `agent-gepa` Managed Agent prototype.

The generated workflow should:

- inspect the current candidate, runtime, evaluator, optimizer, task, and CLI files
- identify the mutable candidate fields
- define input/output eval cases for file-transform tasks and structured runtime behavior
- define numeric and qualitative scoring
- define Actionable Side Information for GEPA reflection
- design direct eval, optimize, compare, and candidate-inspection operations
- avoid inventing support for non-Managed-Agent runtimes
