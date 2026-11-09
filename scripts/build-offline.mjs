import { cp, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';
import { generate } from './build-content.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const run = (command, args, options = {}) => new Promise((resolve, reject) => {
  const child = spawn(command, args, { cwd: root, stdio: 'inherit', ...options });
  child.on('error', reject);
  child.on('exit', (code) => code === 0 ? resolve() : reject(new Error(`${command} exited with ${code}`)));
});

await generate();
await run(process.platform === 'win32' ? 'npx.cmd' : 'npx', ['vite', 'build'], { env: { ...process.env, COURSE_BASE: './' } });
await mkdir(path.join(root, 'dist', 'generated'), { recursive: true });
await Promise.all([
  cp(path.join(root, 'generated', 'course-data.json'), path.join(root, 'dist', 'generated', 'course-data.json')),
  cp(path.join(root, 'course.json'), path.join(root, 'dist', 'course.json')),
  cp(path.join(root, 'code'), path.join(root, 'dist', 'code'), { recursive: true }),
]);
