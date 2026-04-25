import { execFileSync } from 'node:child_process';
import { describe, expect, it } from 'vitest';

describe('package contents', () => {
  it('keeps the Python prototype out of the npm package', () => {
    const output = execFileSync('npm', ['pack', '--dry-run', '--json'], {
      encoding: 'utf8',
    });
    const [pack] = JSON.parse(output) as Array<{ files: Array<{ path: string }> }>;
    const files = pack.files.map((file) => file.path);

    expect(files).toContain('bin/optimizespec.js');
    expect(files).toContain('dist/cli/index.js');
    expect(files.some((file) => file.startsWith('examples/python-managed-agent/'))).toBe(false);
    expect(files.some((file) => file === 'pyproject.toml')).toBe(false);
    expect(files.some((file) => file.startsWith('src/optimizespec/'))).toBe(false);
  });
});
