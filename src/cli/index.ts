import { Command } from 'commander';
import { mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

type JsonValue = string | number | boolean | null | JsonValue[] | { [key: string]: JsonValue };

type PackageJson = {
  version?: string;
  description?: string;
};

type ArtifactStatus = {
  id: string;
  outputPath: string;
  status: 'done' | 'missing';
};

type ContinueResult = {
  change: string;
  complete: boolean;
  created: string[];
  artifacts: ArtifactStatus[];
};

type CliError = Error & {
  code?: string;
  remediation?: string;
};

const cliSourceDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(cliSourceDir, '..', '..');
const packageJson = JSON.parse(readFileSync(join(packageRoot, 'package.json'), 'utf8')) as PackageJson;

function makeError(message: string, code: string, remediation: string): CliError {
  const error = new Error(message) as CliError;
  error.code = code;
  error.remediation = remediation;
  return error;
}

function writeJson(payload: JsonValue): void {
  process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
}

function ensureDir(path: string): void {
  mkdirSync(path, { recursive: true });
}

function writeFileIfMissing(path: string, content: string): boolean {
  try {
    statSync(path);
    return false;
  } catch {
    ensureDir(dirname(path));
    writeFileSync(path, content, 'utf8');
    return true;
  }
}

function fileExists(path: string): boolean {
  try {
    return statSync(path).isFile();
  } catch {
    return false;
  }
}

function dirExists(path: string): boolean {
  try {
    return statSync(path).isDirectory();
  } catch {
    return false;
  }
}

function listMarkdownFiles(path: string): string[] {
  if (!dirExists(path)) {
    return [];
  }
  const out: string[] = [];
  for (const entry of readdirSync(path)) {
    const full = join(path, entry);
    const stats = statSync(full);
    if (stats.isDirectory()) {
      out.push(...listMarkdownFiles(full));
    } else if (entry.endsWith('.md')) {
      out.push(full);
    }
  }
  return out.sort();
}

function readOptional(path: string): string {
  return fileExists(path) ? readFileSync(path, 'utf8') : '';
}

function validateChangeName(name: string): void {
  if (!/^[a-z0-9][a-z0-9-]*[a-z0-9]$/.test(name)) {
    throw makeError(
      `Invalid change name: ${name}`,
      'invalid_change_name',
      'Use kebab-case with lowercase letters, numbers, and hyphens.',
    );
  }
}

function changeDir(root: string, change: string): string {
  return join(root, 'optimizespec', 'changes', change);
}

function getArtifactStatus(root: string, change: string): ArtifactStatus[] {
  const base = changeDir(root, change);
  const specsDir = join(base, 'specs');
  return [
    {
      id: 'proposal',
      outputPath: 'proposal.md',
      status: fileExists(join(base, 'proposal.md')) ? 'done' : 'missing',
    },
    {
      id: 'design',
      outputPath: 'design.md',
      status: fileExists(join(base, 'design.md')) ? 'done' : 'missing',
    },
    {
      id: 'specs',
      outputPath: 'specs/**/*.md',
      status: listMarkdownFiles(specsDir).length > 0 ? 'done' : 'missing',
    },
    {
      id: 'tasks',
      outputPath: 'tasks.md',
      status: fileExists(join(base, 'tasks.md')) ? 'done' : 'missing',
    },
  ];
}

function changeArtifactFiles(summary: string, change = '<change-name>'): Record<string, string> {
  return {
    'proposal.md': `## Why\n\n${summary}\n\n## Optimization System Location\n\n- Decision: create new folder or reuse an existing eval/optimization folder after repo inspection.\n- Path: <repo-relative path where generated code can import or invoke the agent modules>\n- Why: choose a location that keeps optimization code reviewable while preserving access to the production agent package boundary.\n- Import/runtime access plan:\n  - Identify the repo-root command, package entrypoint, editable install, workspace module resolution, or module path required to import the real agent modules.\n- Existing code to reuse:\n  - Identify the real agent factory, tools, environment configuration, and test commands before applying.\n\n## What Changes\n\n- Define the agent behavior to improve.\n- Specify eval cases, scoring, evidence, and optimization-system code expectations.\n\n## Capabilities\n\n### New Capabilities\n- \`optimization-system\`: Eval runner and optimizer for the agent project.\n\n### Modified Capabilities\n- None.\n\n## Impact\n\nAgent-project evals, optimization-system files, optimizer configuration, and documentation.\n`,
    'design.md': `## Context\n\nDocument the project stack, agent runtime, candidate surface, eval runner shape, and generated commands.\n\n## Goals / Non-Goals\n\n**Goals:**\n- Generate an optimization system that fits the project being improved.\n- Keep evidence and scoring inspectable.\n\n**Non-Goals:**\n- Require a bundled OptimizeSpec runtime package in the project.\n\n## Decisions\n\nDescribe language choice, runner invocation, scorer strategy, and optimizer wiring.\n\n## Risks / Trade-offs\n\n- [Unknown project stack] -> Inspect the repository before applying.\n`,
    'specs/optimization-system/spec.md': `## ADDED Requirements\n\n### Requirement: Generated optimization system\nThe agent project SHALL contain generated eval and optimization entrypoints based on this OptimizeSpec change.\n\n#### Scenario: Runner generated\n- **WHEN** the change is applied to an agent project\n- **THEN** the agent project contains runner files in the selected language\n`,
    'tasks.md': `## 1. Generate Optimization System\n\n- [ ] 1.1 Inspect the project stack and agent runtime.\n- [ ] 1.2 Generate eval runner files in the selected language.\n- [ ] 1.3 Generate optimizer entrypoint and README instructions.\n- [ ] 1.4 Run local validation for generated files.\n`,
  };
}

function initProject(targetPath: string): string[] {
  const root = resolve(targetPath);
  const created: string[] = [];
  for (const dir of [
    join(root, 'optimizespec'),
    join(root, 'optimizespec', 'changes'),
  ]) {
    if (!dirExists(dir)) {
      ensureDir(dir);
      created.push(dir);
    }
  }
  const readme = join(root, 'optimizespec', 'README.md');
  if (
    writeFileIfMissing(
      readme,
      '# OptimizeSpec\n\nThis directory contains optimization-system specs and generated implementation plans.\n',
    )
  ) {
    created.push(readme);
  }
  return created;
}

function createChange(rootPath: string, name: string, description: string | undefined): string[] {
  validateChangeName(name);
  const root = resolve(rootPath);
  initProject(root);
  const base = changeDir(root, name);
  if (dirExists(base)) {
    throw makeError(
      `Change already exists: ${name}`,
      'change_exists',
      `Use a different name or edit ${base}.`,
    );
  }
  ensureDir(join(base, 'specs', 'optimization-system'));
  const created: string[] = [];
  const summary = description ?? 'Describe the optimization system to build.';
  const files = changeArtifactFiles(summary, name);
  for (const [relative, content] of Object.entries(files)) {
    const path = join(base, relative);
    writeFileIfMissing(path, content);
    created.push(path);
  }
  return created;
}

function continueChange(rootPath: string, name: string): ContinueResult {
  validateChangeName(name);
  const root = resolve(rootPath);
  const base = changeDir(root, name);
  if (!dirExists(base)) {
    throw makeError(
      `Change does not exist: ${name}`,
      'change_missing',
      `Create it first with: optimizespec new change ${name}`,
    );
  }

  const files = changeArtifactFiles('Describe the optimization system to build.', name);
  const artifactPaths: Record<string, string> = {
    proposal: 'proposal.md',
    design: 'design.md',
    specs: 'specs/optimization-system/spec.md',
    tasks: 'tasks.md',
  };
  const created: string[] = [];
  const missing = getArtifactStatus(root, name).find((artifact) => artifact.status === 'missing');
  if (missing) {
    const relative = artifactPaths[missing.id];
    const path = join(base, relative);
    writeFileIfMissing(path, files[relative]);
    created.push(path);
  }
  const artifacts = getArtifactStatus(root, name);
  return {
    change: name,
    complete: artifacts.every((artifact) => artifact.status === 'done'),
    created,
    artifacts,
  };
}

function validateChange(rootPath: string, name: string): { valid: boolean; errors: string[]; warnings: string[] } {
  validateChangeName(name);
  const root = resolve(rootPath);
  const base = changeDir(root, name);
  const errors: string[] = [];
  const warnings: string[] = [];
  if (!dirExists(base)) {
    errors.push(`Change directory does not exist: ${base}`);
    return { valid: false, errors, warnings };
  }
  for (const artifact of getArtifactStatus(root, name)) {
    if (artifact.status !== 'done') {
      errors.push(`Missing ${artifact.outputPath}`);
    }
  }
  for (const spec of listMarkdownFiles(join(base, 'specs'))) {
    const text = readOptional(spec);
    if (!text.includes('### Requirement:')) {
      errors.push(`${spec}: missing requirement heading`);
    }
    if (!text.includes('#### Scenario:')) {
      errors.push(`${spec}: missing scenario heading`);
    }
    if (!text.includes('- **WHEN**') || !text.includes('- **THEN**')) {
      errors.push(`${spec}: scenarios must include WHEN and THEN bullets`);
    }
  }
  const tasks = readOptional(join(base, 'tasks.md'));
  if (tasks && !tasks.includes('- [ ]') && !tasks.includes('- [x]')) {
    warnings.push('tasks.md has no checkbox tasks');
  }
  return { valid: errors.length === 0, errors, warnings };
}

function handleError(error: unknown, json: boolean): never {
  const err = error as CliError;
  if (json) {
    writeJson({
      error: {
        code: err.code ?? 'error',
        message: err.message,
        remediation: err.remediation ?? 'Run with --help or inspect the change artifacts.',
      },
    });
  } else {
    process.stderr.write(`Error: ${err.message}\n`);
    if (err.remediation) {
      process.stderr.write(`${err.remediation}\n`);
    }
  }
  process.exit(1);
}

export function createProgram(): Command {
  const program = new Command();

  program
    .name('optimizespec')
    .description(packageJson.description ?? 'Spec-driven optimization system generator.')
    .version(packageJson.version ?? '0.0.0')
    .option('--no-color', 'Disable color output');

  program
    .command('init')
    .description('Initialize OptimizeSpec files in a project.')
    .argument('[path]', 'Target project path', '.')
    .option('--json', 'Output machine-readable JSON')
    .action((path: string, options: { json?: boolean }) => {
      try {
        const created = initProject(path);
        const payload = { path: resolve(path), created };
        options.json ? writeJson(payload) : process.stdout.write(`Initialized OptimizeSpec at ${payload.path}\n`);
      } catch (error) {
        handleError(error, Boolean(options.json));
      }
    });

  const newCommand = program.command('new').description('Create new OptimizeSpec artifacts.');
  newCommand
    .command('change')
    .description('Create a new optimization-system change.')
    .argument('<name>', 'Kebab-case change name')
    .option('--path <path>', 'Project path', '.')
    .option('--description <text>', 'Initial change description')
    .option('--json', 'Output machine-readable JSON')
    .action((name: string, options: { path?: string; description?: string; json?: boolean }) => {
      try {
        const created = createChange(options.path ?? '.', name, options.description);
        const payload = { change: name, created };
        options.json ? writeJson(payload) : process.stdout.write(`Created OptimizeSpec change ${name}\n`);
      } catch (error) {
        handleError(error, Boolean(options.json));
      }
    });

  program
    .command('continue')
    .description('Create the next missing artifact for an existing OptimizeSpec change.')
    .requiredOption('--change <name>', 'Change name')
    .option('--path <path>', 'Project path', '.')
    .option('--json', 'Output machine-readable JSON')
    .action((options: { change: string; path?: string; json?: boolean }) => {
      try {
        const result = continueChange(options.path ?? '.', options.change);
        if (options.json) {
          writeJson(result);
        } else if (result.created.length > 0) {
          process.stdout.write(`Created next artifact for ${options.change}: ${result.created[0]}\n`);
        } else {
          process.stdout.write(`Change ${options.change} already has all required artifacts\n`);
        }
      } catch (error) {
        handleError(error, Boolean(options.json));
      }
    });

  program
    .command('status')
    .description('Display artifact completion status for a change.')
    .requiredOption('--change <name>', 'Change name')
    .option('--path <path>', 'Project path', '.')
    .option('--json', 'Output machine-readable JSON')
    .action((options: { change: string; path?: string; json?: boolean }) => {
      try {
        validateChangeName(options.change);
        const artifacts = getArtifactStatus(resolve(options.path ?? '.'), options.change);
        const payload = {
          change: options.change,
          complete: artifacts.every((artifact) => artifact.status === 'done'),
          artifacts,
        };
        if (options.json) {
          writeJson(payload);
        } else {
          process.stdout.write(`Change: ${options.change}\n`);
          for (const artifact of artifacts) {
            process.stdout.write(`[${artifact.status === 'done' ? 'x' : ' '}] ${artifact.id} ${artifact.outputPath}\n`);
          }
        }
      } catch (error) {
        handleError(error, Boolean(options.json));
      }
    });

  program
    .command('validate')
    .description('Validate an OptimizeSpec change.')
    .argument('<change>', 'Change name')
    .option('--path <path>', 'Project path', '.')
    .option('--json', 'Output machine-readable JSON')
    .action((change: string, options: { path?: string; json?: boolean }) => {
      try {
        const result = validateChange(options.path ?? '.', change);
        if (options.json) {
          writeJson({ change, ...result });
        } else if (result.valid) {
          process.stdout.write(`Change '${change}' is valid\n`);
        } else {
          process.stderr.write(`Change '${change}' is invalid\n${result.errors.join('\n')}\n`);
        }
        process.exitCode = result.valid ? 0 : 1;
      } catch (error) {
        handleError(error, Boolean(options.json));
      }
    });

  return program;
}

export function main(argv = process.argv): void {
  createProgram().parse(argv);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}
