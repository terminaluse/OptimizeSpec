import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';

function listFiles(root: string): string[] {
  const files: string[] = [];
  for (const entry of readdirSync(root)) {
    const path = join(root, entry);
    if (statSync(path).isDirectory()) {
      files.push(...listFiles(path));
    } else {
      files.push(path);
    }
  }
  return files;
}

describe('package contents', () => {
  it('keeps the Python prototype out of the npm package', () => {
    const output = execFileSync('npm', ['pack', '--dry-run', '--json', '--ignore-scripts'], {
      encoding: 'utf8',
    });
    const [pack] = JSON.parse(output) as Array<{ files: Array<{ path: string }> }>;
    const files = pack.files.map((file) => file.path);

    expect(files).toContain('bin/optimizespec.js');
    expect(files).toContain('dist/cli/index.js');
    expect(files.some((file) => file.startsWith('examples/py-claude-managed-agent/'))).toBe(false);
    expect(files.some((file) => file.startsWith('tests/fixtures/reference-agents/'))).toBe(false);
    expect(files.some((file) => file === 'pyproject.toml')).toBe(false);
    expect(files.some((file) => file.startsWith('src/optimizespec/'))).toBe(false);
  });

  it('keeps committed reference agents narrow and generated systems out of examples', () => {
    const fixtureRoot = join(process.cwd(), 'tests', 'fixtures', 'reference-agents');
    const allowedFixtureFiles = new Set(['agent.yaml', 'request.md']);

    expect(existsSync(join(fixtureRoot, 'optimizespec-managed-agent', 'agent.yaml'))).toBe(true);
    expect(existsSync(join(process.cwd(), 'examples', 'py-claude-managed-agent', 'optimizespec', 'changes'))).toBe(false);
    expect(existsSync(join(process.cwd(), 'optimizespec', 'systems'))).toBe(false);

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

  it('keeps installed skill folders self-contained', () => {
    const skillRoot = join(process.cwd(), 'skills');
    const forbiddenPatterns = [/\.\.\//, /\/Users\//, /\bexamples\//, /\btests\/fixtures\//];

    for (const skillName of readdirSync(skillRoot)) {
      const skillPath = join(skillRoot, skillName);
      if (!statSync(skillPath).isDirectory()) {
        continue;
      }

      for (const filePath of listFiles(skillPath)) {
        const content = readFileSync(filePath, 'utf8');
        for (const pattern of forbiddenPatterns) {
          expect(content, `${filePath} contains non-self-contained reference ${pattern}`).not.toMatch(pattern);
        }

        for (const match of content.matchAll(/`((?:assets|references)\/[^`]+)`/g)) {
          const relativeReference = match[1];
          expect(
            existsSync(join(skillPath, relativeReference)),
            `${filePath} references missing skill-local file ${relativeReference}`,
          ).toBe(true);
        }
      }
    }
  });
});
