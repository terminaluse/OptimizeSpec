#!/usr/bin/env node
import { execFileSync } from 'node:child_process';
import { existsSync, rmSync } from 'node:fs';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);

const runTsc = (args = []) => {
  const tscPath = require.resolve('typescript/bin/tsc');
  execFileSync(process.execPath, [tscPath, ...args], { stdio: 'inherit' });
};

console.log('Building OptimizeSpec CLI...\n');

if (existsSync('dist')) {
  console.log('Cleaning dist directory...');
  rmSync('dist', { recursive: true, force: true });
}

console.log('Compiling TypeScript...');
try {
  runTsc(['--version']);
  runTsc();
  console.log('\nBuild completed successfully.');
} catch {
  console.error('\nBuild failed.');
  process.exit(1);
}
