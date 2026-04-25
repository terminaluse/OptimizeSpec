## 1. Fixture Boundary

- [x] 1.1 Create a dedicated reference-agent fixture root for committed agent inputs.
- [x] 1.2 Move current agent fixtures into the reference-agent fixture root.
- [x] 1.3 Define the minimal allowed fixture files and metadata for reference agents.
- [x] 1.4 Add fixture-loading helpers so tests do not depend on the old example path.

## 2. Generated Output Cleanup

- [x] 2.1 Remove or relocate committed full optimization-system directories from `examples/python-managed-agent/optimizespec/changes/`.
- [x] 2.2 Replace imports of committed optimization-system scripts with generated temp-workspace flows or test-support helpers.
- [x] 2.3 Move any useful deterministic comparison data into narrow expected-output fixtures.
- [x] 2.4 Ensure run directories, generated systems, and optimizer traces are ignored or created under temporary test directories.

## 3. CLI And Skill Tests

- [x] 3.1 Add a CLI test that starts from a reference-agent fixture and generates an optimization-system change in a temporary workspace.
- [x] 3.2 Add a test that verifies generated runner output structure without committing the generated runner.
- [x] 3.3 Update Python regression tests to use reference fixtures and temp outputs instead of committed generated changes.
- [x] 3.4 Keep the live Managed Agents smoke test opt-in and pointed at generated or temp artifacts.

## 4. Documentation And Release Checks

- [x] 4.1 Update README and TECHNICAL docs to describe reference agents as inputs and optimization systems as generated outputs.
- [x] 4.2 Update package contents checks to assert generated systems and Python reference fixtures are not shipped.
- [x] 4.3 Add verification that release-visible committed paths do not contain unapproved generated optimization systems.
- [x] 4.4 Document how to add a new reference agent and how to regenerate expected output fixtures.

## 5. Verification

- [x] 5.1 Run `npm test`.
- [x] 5.2 Run Python deterministic regression tests.
- [x] 5.3 Run the opt-in live Managed Agents smoke test when credentials are available.
- [x] 5.4 Run `openspec validate reference-agent-fixtures`.
- [x] 5.5 Run package dry-run verification and whitespace checks.
