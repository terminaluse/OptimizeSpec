## 1. Fixture Boundary

- [ ] 1.1 Create a dedicated reference-agent fixture root for committed agent inputs.
- [ ] 1.2 Move current agent fixtures into the reference-agent fixture root.
- [ ] 1.3 Define the minimal allowed fixture files and metadata for reference agents.
- [ ] 1.4 Add fixture-loading helpers so tests do not depend on the old example path.

## 2. Generated Output Cleanup

- [ ] 2.1 Remove or relocate committed full optimization-system directories from `examples/python-managed-agent/optimizespec/changes/`.
- [ ] 2.2 Replace imports of committed optimization-system scripts with generated temp-workspace flows or test-support helpers.
- [ ] 2.3 Move any useful deterministic comparison data into narrow expected-output fixtures.
- [ ] 2.4 Ensure run directories, generated systems, and optimizer traces are ignored or created under temporary test directories.

## 3. CLI And Skill Tests

- [ ] 3.1 Add a CLI test that starts from a reference-agent fixture and generates an optimization-system change in a temporary workspace.
- [ ] 3.2 Add a test that verifies generated runner output structure without committing the generated runner.
- [ ] 3.3 Update Python regression tests to use reference fixtures and temp outputs instead of committed generated changes.
- [ ] 3.4 Keep the live Managed Agents smoke test opt-in and pointed at generated or temp artifacts.

## 4. Documentation And Release Checks

- [ ] 4.1 Update README and TECHNICAL docs to describe reference agents as inputs and optimization systems as generated outputs.
- [ ] 4.2 Update package contents checks to assert generated systems and Python reference fixtures are not shipped.
- [ ] 4.3 Add verification that release-visible committed paths do not contain unapproved generated optimization systems.
- [ ] 4.4 Document how to add a new reference agent and how to regenerate expected output fixtures.

## 5. Verification

- [ ] 5.1 Run `npm test`.
- [ ] 5.2 Run Python deterministic regression tests.
- [ ] 5.3 Run the opt-in live Managed Agents smoke test when credentials are available.
- [ ] 5.4 Run `openspec validate reference-agent-fixtures`.
- [ ] 5.5 Run package dry-run verification and whitespace checks.
