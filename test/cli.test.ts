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
    expect(output).toContain('apply');
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

  it('scaffolds TypeScript runner files in the agent project', () => {
    const project = tempProject();
    const target = tempProject();
    run(['new', 'change', 'typed-runner', '--path', project, '--json']);

    const result = JSON.parse(
      run([
        'apply',
        '--change',
        'typed-runner',
        '--path',
        project,
        '--target',
        target,
        '--stack',
        'typescript',
        '--json',
      ]),
    );
    expect(result.stack).toBe('typescript');
    expect(result.created).toEqual(expect.arrayContaining([expect.stringContaining('eval-runner.ts')]));

    const runner = readFileSync(join(target, 'optimizespec.generated', 'typed-runner', 'eval-runner.ts'), 'utf8');
    expect(runner).toContain('export async function runEvalCase');
  });

  it('can start from a committed reference-agent fixture and generate output in temp workspaces', () => {
    const fixture = join(process.cwd(), 'tests', 'fixtures', 'reference-agents', 'optimizespec-managed-agent');
    const project = tempProject();
    const target = tempProject();
    const request = readFileSync(join(fixture, 'request.md'), 'utf8').trim();
    run([
      'new',
      'change',
      'reference-agent-system',
      '--path',
      project,
      '--description',
      request || 'Generate an optimization system from the reference agent fixture.',
      '--json',
    ]);

    const result = JSON.parse(
      run([
        'apply',
        '--change',
        'reference-agent-system',
        '--path',
        project,
        '--target',
        target,
        '--stack',
        'typescript',
        '--json',
      ]),
    );

    expect(result.created).toHaveLength(3);
    expect(readFileSync(join(target, 'optimizespec.generated', 'reference-agent-system', 'optimizer.ts'), 'utf8')).toContain(
      'meanScore',
    );
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
