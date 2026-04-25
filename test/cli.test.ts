import { execFileSync, spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';

const cli = join(process.cwd(), 'bin', 'optimizespec.js');

function run(args: string[], cwd = process.cwd()): string {
  return execFileSync(process.execPath, [cli, ...args], {
    cwd,
    encoding: 'utf8',
  });
}

function tempProject(): string {
  return mkdtempSync(join(tmpdir(), 'optimizespec-test-'));
}

describe('optimizespec cli', () => {
  it('prints help from the TypeScript command surface', () => {
    const output = run(['--help']);
    expect(output).toContain('Spec-driven optimization system generator');
    expect(output).toContain('init');
    expect(output).toContain('continue');
    expect(output).toContain('validate');
    expect(output).not.toMatch(/\bapply\b/);
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
    expect(created.created).toEqual(
      expect.arrayContaining([
        expect.stringContaining('proposal.md'),
        expect.stringContaining('design.md'),
        expect.stringContaining('tasks.md'),
      ]),
    );

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
    expect(result.created).toEqual(expect.arrayContaining([expect.stringContaining('proposal.md')]));
    expect(readFileSync(join(project, 'optimizespec', 'changes', 'partial-flow', 'proposal.md'), 'utf8')).toContain(
      '## Why',
    );
  });

  it('does not expose the removed apply command', () => {
    const result = spawnSync(process.execPath, [cli, 'apply'], { encoding: 'utf8' });

    expect(result.status).toBe(1);
    expect(result.stderr).toContain("unknown command 'apply'");
  });

  it('emits structured JSON errors for invalid changes', () => {
    const project = tempProject();
    const result = spawnSync(
      process.execPath,
      [cli, 'validate', 'BadName', '--path', project, '--json'],
      { encoding: 'utf8' },
    );
    expect(result.status).toBe(1);
    const payload = JSON.parse(result.stdout);
    expect(payload.error.code).toBe('invalid_change_name');
    expect(payload.error.remediation).toContain('kebab-case');
  });
});
