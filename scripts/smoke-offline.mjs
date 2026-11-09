// Offline smoke test: renders dist/index.html via file:// and asserts the app works.
// Spawns the system Chrome/Chromium directly because this repo has no Playwright dependency.
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const candidates = [process.env.CHROME_PATH, 'google-chrome', 'chromium', 'chromium-browser'].filter(Boolean);
const browser = candidates.find((name) => spawnSync(name, ['--version']).status === 0);
if (!browser) throw new Error(`no headless browser found; set CHROME_PATH (tried: ${candidates.join(', ')})`);

const result = spawnSync(browser, [
  '--headless=new',
  '--disable-gpu',
  '--no-sandbox',
  '--enable-logging=stderr',
  '--virtual-time-budget=5000',
  '--dump-dom',
  pathToFileURL(path.join(root, 'dist', 'index.html')).href,
], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });
if (result.error || result.status !== 0) throw new Error(`headless browser failed: ${result.error ?? result.status}`);

const consoleLines = result.stderr.split('\n').filter((line) => line.includes(':CONSOLE'));
if (consoleLines.length) throw new Error(`browser console errors:\n${consoleLines.join('\n')}`);
const sessions = result.stdout.match(/href="#\/sessions\//g)?.length ?? 0;
if (!sessions) throw new Error('no session links rendered in offline index.html');
console.log(`offline smoke test passed: ${sessions} session links rendered, no console errors (${browser})`);
