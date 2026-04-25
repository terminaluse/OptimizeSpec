## 1. Reference Layout

- [ ] 1.1 Create `references/core/` in `optimizespec-common` and each phase skill that vendors references.
- [ ] 1.2 Create `references/runtimes/claude-managed-agent/` in `optimizespec-common` and each phase skill that needs Managed Agent runtime guidance.
- [ ] 1.3 Move runtime-neutral contracts into `core/`.
- [ ] 1.4 Move Managed Agent-specific contracts into `runtimes/claude-managed-agent/`.
- [ ] 1.5 Remove or update old root-level reference paths after all consumers point to scoped paths.

## 2. Skill Integration

- [ ] 2.1 Update `optimizespec-new` to load core proposal references and record target runtime without hardcoding Claude Managed Agents in generic template fields.
- [ ] 2.2 Update `optimizespec-continue` to load core design references plus Claude Managed Agent runtime references only when that runtime is selected.
- [ ] 2.3 Update `optimizespec-apply` to require a supported runtime subtree and keep Claude Managed Agents as the only v1 implementation target.
- [ ] 2.4 Update `optimizespec-verify` to load core verification/evidence references plus runtime-specific evidence expectations when applicable.
- [ ] 2.5 Update common reference index guidance so phase skills can discover core and runtime-specific contract paths.

## 3. Templates And Docs

- [ ] 3.1 Update proposal templates so `Runtime:` is a target-agent field rather than a hardcoded Claude Managed Agents value.
- [ ] 3.2 Update design templates to separate generic optimization-system sections from Claude Managed Agent runtime sections.
- [ ] 3.3 Update README or TECHNICAL wording to state that the workflow is general but v1 apply support is Claude Managed Agent-specific.
- [ ] 3.4 Update any OpenSpec artifacts or comments that mention old root reference paths if they would confuse future maintainers.

## 4. Verification

- [ ] 4.1 Search the repo for old root reference paths and update stale links.
- [ ] 4.2 Run tests that verify installed skills are self-contained.
- [ ] 4.3 Run `npm test`.
- [ ] 4.4 Run `npm run pack:check`.
- [ ] 4.5 Run deterministic Python reference tests if the change touches Python reference paths or runtime guidance consumed by Python fixtures.
