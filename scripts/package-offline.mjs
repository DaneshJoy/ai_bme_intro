import { mkdir, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const run = (command, args) => new Promise((resolve, reject) => {
  const child = spawn(command, args, { cwd: root, stdio: 'inherit' });
  child.on('error', reject);
  child.on('exit', (code) => code === 0 ? resolve() : reject(new Error(`${command} exited with ${code}`)));
});

await run(process.platform === 'win32' ? 'npm.cmd' : 'npm', ['run', 'build:offline']);
const output = path.join(root, 'offline', 'ai-bme-intro-offline.zip');
await mkdir(path.dirname(output), { recursive: true });
await rm(output, { force: true });
await run(process.platform === 'win32' ? 'python' : 'python3', ['scripts/create-zip.py', 'dist', output]);
