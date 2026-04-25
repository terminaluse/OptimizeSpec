## 1. CLI Surface

- [x] 1.1 Remove the `apply` command registration from `src/cli/index.ts`.
- [x] 1.2 Remove or make unreachable apply-only scaffold helpers and placeholder runner renderers.
- [x] 1.3 Ensure `optimizespec --help` no longer lists `apply`.
- [x] 1.4 Ensure invoking `optimizespec apply` exits non-zero as an unsupported command.

## 2. Tests

- [x] 2.1 Update CLI help tests to assert supported commands and absence of `apply`.
- [x] 2.2 Remove tests that expect `optimizespec apply` to generate placeholder runner files.
- [x] 2.3 Add a test for unsupported `apply` invocation.
- [x] 2.4 Keep JSON status/validate/new/continue tests intact.

## 3. Documentation

- [x] 3.1 Remove `optimizespec apply` from README and TECHNICAL command examples.
- [x] 3.2 Document `$optimizespec-apply <change-name>` as the supported implementation path.
- [x] 3.3 Clarify that the CLI creates, continues, inspects, and validates artifacts, while skills implement the optimization system.
- [x] 3.4 Search docs and active artifacts for stale `optimizespec apply` references and update current guidance.

## 4. Verification

- [x] 4.1 Run `openspec validate remove-cli-apply`.
- [x] 4.2 Run `npm test`.
- [x] 4.3 Run `npm run pack:check`.
- [x] 4.4 Inspect package contents to confirm `skills/optimizespec-apply` is still included.
