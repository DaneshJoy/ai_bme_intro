import { cp, mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
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
const dist = path.join(root, 'dist');
const app = await readFile(path.join(dist, 'assets', 'app.js'), 'utf8');
if (app.includes('</script>')) throw new Error('offline app bundle contains </script>');
const stylesheet = (await readdir(path.join(dist, 'assets'))).find((file) => file.endsWith('.css'));
if (!stylesheet) throw new Error('offline stylesheet not found');
let index = await readFile(path.join(dist, 'index.html'), 'utf8');
index = index.replace(/<script type="module"[^>]*src="\.\/assets\/app\.js"><\/script>\s*/, () => `<script type="module">${app}</script>\n`);
const css = (await readFile(path.join(dist, 'assets', stylesheet), 'utf8')).replaceAll('url(./', 'url(./assets/');
index = index.replace(new RegExp(`<link rel="stylesheet"[^>]*href="\\.\\/assets\\/${stylesheet}">`), () => `<style>${css}</style>`);
await writeFile(path.join(dist, 'index.html'), index);
await mkdir(path.join(root, 'dist', 'generated'), { recursive: true });
await Promise.all([
  cp(path.join(root, 'generated', 'course-data.json'), path.join(root, 'dist', 'generated', 'course-data.json')),
  cp(path.join(root, 'course.json'), path.join(root, 'dist', 'course.json')),
  cp(path.join(root, 'code'), path.join(root, 'dist', 'code'), { recursive: true }),
]);
