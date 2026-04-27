import { execFileSync, spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';

const cli = join(process.cwd(), 'bin', 'optimizespec.js');
const bun = process.env.BUN_BIN ?? 'bun';

function run(args: string[], cwd = process.cwd()): string {
  return execFileSync(bun, [cli, ...args], {
    cwd,
    encoding: 'utf8',
  });
}

function tempProject(): string {
  return mkdtempSync(join(tmpdir(), 'optimizespec-test-'));
}

describe('optimizespec cli', () => {
  it('prints help from the TypeScript command surface', () => {
    const result = spawnSync(bun, [cli, '--help'], { encoding: 'utf8' });

    expect(result.status).toBe(0);
  });

  it('creates, reports, and validates a change as JSON', () => {
    const project = tempProject();
    const created = JSON.parse(
      run([
        'new',
        'change',
        'improve-agent-output',
        '--path',
        project,
        '--description',
        'Improve the agent output.',
        '--json',
      ]),
    );
    expect(created.change).toBe('improve-agent-output');
    expect(Array.isArray(created.created)).toBe(true);
    expect(created.created.length).toBeGreaterThan(0);

    const status = JSON.parse(run(['status', '--path', project, '--change', 'improve-agent-output', '--json']));
    expect(status.complete).toBe(true);
    expect(status.artifacts).toHaveLength(4);

    const validation = JSON.parse(run(['validate', 'improve-agent-output', '--path', project, '--json']));
    expect(validation.valid).toBe(true);
  });

  it('continues a partial change by creating the next missing artifact', () => {
    const project = tempProject();
    run(['init', project, '--json']);
    mkdirSync(join(project, 'optimizespec', 'changes', 'partial-flow'), { recursive: true });

    const result = JSON.parse(run(['continue', '--path', project, '--change', 'partial-flow', '--json']));

    expect(result.complete).toBe(false);
    expect(Array.isArray(result.created)).toBe(true);
    expect(result.created.length).toBeGreaterThan(0);
  });

  it('does not expose the removed apply command', () => {
    const result = spawnSync(bun, [cli, 'apply'], { encoding: 'utf8' });

    expect(result.status).toBe(1);
  });

  it('emits structured JSON errors for invalid changes', () => {
    const project = tempProject();
    const result = spawnSync(
      bun,
      [cli, 'validate', 'BadName', '--path', project, '--json'],
      { encoding: 'utf8' },
    );
    expect(result.status).toBe(1);
    const payload = JSON.parse(result.stdout);
    expect(payload.error.code).toBe('invalid_change_name');
  });
});
