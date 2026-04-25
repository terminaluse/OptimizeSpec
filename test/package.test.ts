import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';

describe('package contents', () => {
  it('keeps the Python prototype out of the npm package', () => {
    const output = execFileSync('npm', ['pack', '--dry-run', '--json', '--ignore-scripts'], {
      encoding: 'utf8',
    });
    const [pack] = JSON.parse(output) as Array<{ files: Array<{ path: string }> }>;
    const files = pack.files.map((file) => file.path);

    expect(files).toContain('bin/optimizespec.js');
    expect(files).toContain('dist/cli/index.js');
    expect(files.some((file) => file.startsWith('examples/python-managed-agent/'))).toBe(false);
    expect(files.some((file) => file.startsWith('tests/fixtures/reference-agents/'))).toBe(false);
    expect(files.some((file) => file === 'pyproject.toml')).toBe(false);
    expect(files.some((file) => file.startsWith('src/optimizespec/'))).toBe(false);
  });

  it('keeps committed reference agents narrow and generated systems out of examples', () => {
    const fixtureRoot = join(process.cwd(), 'tests', 'fixtures', 'reference-agents');
    const allowedFixtureFiles = new Set(['agent.yaml', 'request.md']);

    expect(existsSync(join(fixtureRoot, 'optimizespec-managed-agent', 'agent.yaml'))).toBe(true);
    expect(existsSync(join(process.cwd(), 'examples', 'python-managed-agent', 'optimizespec', 'changes'))).toBe(false);

    for (const fixtureId of readdirSync(fixtureRoot)) {
      const fixturePath = join(fixtureRoot, fixtureId);
      if (!statSync(fixturePath).isDirectory()) {
        continue;
      }
      for (const fileName of readdirSync(fixturePath)) {
        expect(allowedFixtureFiles.has(fileName)).toBe(true);
      }
    }
  });
});
