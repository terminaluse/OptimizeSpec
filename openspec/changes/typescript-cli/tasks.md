## 1. TypeScript CLI Project Setup

- [x] 1.1 Add Node package metadata for the TypeScript CLI, including `bin`, `files`, scripts, engines, dependencies, and dev dependencies.
- [x] 1.2 Add TypeScript compiler configuration for ESM Node output into `dist/`.
- [x] 1.3 Add the executable `bin/optimizespec.js` shim that loads the compiled CLI.
- [x] 1.4 Add build, dev, test, and package-inspection scripts.

## 2. Command Surface

- [x] 2.1 Implement the TypeScript command registration root and global options.
- [x] 2.2 Add spec-authoring commands for creating, inspecting, continuing, validating, and applying OptimizeSpec changes.
- [x] 2.3 Add target-repo scaffolding commands that generate runner/eval/optimizer files from the approved spec and detected target stack.
- [x] 2.4 Confirm no example-only or legacy Python commands are part of the core product flow.
- [x] 2.5 Add `--json` output support for agent-compatible commands.

## 3. Python Prototype Demotion

- [x] 3.1 Move the existing Python Managed Agents/GEPA implementation out of `src/optimizespec/` into an example, fixture, or reference directory.
- [x] 3.2 Remove Python package metadata and the Python console script from the public release path.
- [x] 3.3 Keep regression tests for the Python prototype pointed at its new example or fixture location.
- [x] 3.4 Confirm no example-only Python adapter remains in the public CLI.

## 4. Packaging And Documentation

- [x] 4.1 Update README and TECHNICAL docs to show the TypeScript/npm CLI as the public install and usage path.
- [x] 4.2 Remove or mark legacy Python console-script instructions and package references.
- [x] 4.3 Decide whether `skills/`, templates, and example changes are packaged runtime assets or repo-only examples, then update package allowlists accordingly.
- [x] 4.4 Add migration notes for existing users moving from the Python CLI.

## 5. Verification

- [x] 5.1 Add Vitest tests for help output, command registration, option parsing, and JSON-mode stdout.
- [x] 5.2 Add scaffolding tests that verify generated target-repo runners are emitted in the selected target language.
- [x] 5.3 Add package contents verification using an npm pack dry run or equivalent.
- [x] 5.4 Run existing Python prototype tests from the new example or fixture location to preserve regression coverage.
- [x] 5.5 Run live Managed Agents smoke tests against the example/fixture with explicit credentials and environment flags.
