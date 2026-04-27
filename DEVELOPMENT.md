# Development

Bun 1.3.0 or newer is required for local development and CLI execution.

```bash
bun install
bun run test
bun run pack:check
```

The bundled Python Claude Managed Agents reference package is tested from repo-root scripts:

```bash
bun run example:py:setup
ANTHROPIC_API_KEY=... bun run example:py:test
```

For a package cleanliness check without live API calls:

```bash
scripts/test-python-managed-agent-example.sh --check-only
```

The example test command is live-only and requires preview credentials. It runs the packaged live optimizer loop and verifies that no generated artifacts are written back into the skill package. `prepublishOnly` runs the unit tests and pack check; run the live example separately before publishing when preview credentials are available.
