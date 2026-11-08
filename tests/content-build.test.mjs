import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, readdir, rm, writeFile, copyFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { generate } from '../scripts/build-content.mjs';
import { readFile as readSource } from 'node:fs/promises';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const manifest = JSON.parse(await readFile(path.join(root, 'course.json'), 'utf8'));
const names = (await readdir(root)).filter((n) => /^session_\d{2}_.+\.md$/.test(n)).sort();
const temporary = await mkdtemp(path.join(os.tmpdir(), 'ai-bme-'));
const sourceDir = path.join(temporary, 'source');
const outputDir = path.join(temporary, 'out');
async function setup() {
  await rm(sourceDir, { recursive: true, force: true });
  await mkdir(path.join(sourceDir, 'code'), { recursive: true });
  for (const name of names) await copyFile(path.join(root, name), path.join(sourceDir, name));
  await copyFile(path.join(root, 'course.json'), path.join(sourceDir, 'course.json'));
  for (const name of await readdir(path.join(root, 'code'))) await copyFile(path.join(root, 'code', name), path.join(sourceDir, 'code', name));
}

test('generates student lessons published whole', async () => {
  await setup();
  try {
    const data = await generate({ sourceDir, outputDir });
    assert.equal(data.lessons.length, names.length);
    assert.equal(data.codes.filter((code) => !code.supplemental).length, data.lessons.flatMap((lesson) => lesson.codes).length);
    if (names.length >= 5) assert.deepEqual(data.lessons[4].codes.map((code) => code.name), ['session_05_bfs_dfs.ipynb', 'session_05_bfs_dfs.py']);
    const selfStudy = data.codes.at(-1);
    assert.equal(selfStudy.path, 'code/python_selfstudy.ipynb');
    assert.equal(selfStudy.githubUrl, 'https://github.com/DaneshJoy/ai_bme_intro/blob/main/code/python_selfstudy.ipynb');
    assert.equal(selfStudy.supplemental, true);
    assert.equal('session' in selfStudy, false);
    assert.ok((await readFile(path.join(outputDir, 'course-data.json'), 'utf8')).length);
    for (const [i, lesson] of data.lessons.entries()) {
      const original = await readFile(path.join(sourceDir, lesson.sourcePath), 'utf8');
      assert.equal(lesson.order, i + 1);
      assert.equal(lesson.content, original);
    }
  } finally { await rm(sourceDir, { recursive: true, force: true }); await rm(outputDir, { recursive: true, force: true }); }
});

test('course metadata contains Persian Unicode', () => {
  const containsPersian = (value) => /[\u0600-\u06ff]/u.test(value);
  for (const value of [manifest.title, manifest.description, manifest.level, manifest.category, ...manifest.tags]) {
    assert.ok(containsPersian(value), `Expected Persian Unicode in: ${value}`);
    assert.ok(!value.includes('?'), `Unexpected question mark in: ${value}`);
  }
});

test('generated lecture titles preserve Persian Unicode', async () => {
  const containsPersian = (value) => /[\u0600-\u06ff]/u.test(value);
  await setup();
  try {
    const data = await generate({ sourceDir, outputDir });
    for (const lesson of data.lessons) {
      assert.ok(containsPersian(lesson.title), `Expected Persian title for ${lesson.id}`);
      assert.ok(!lesson.title.includes('?'), `Unexpected question mark in title for ${lesson.id}`);
    }
  } finally { await rm(sourceDir, { recursive: true, force: true }); await rm(outputDir, { recursive: true, force: true }); }
});

test('course manifest passes the standalone Ajv schema validator', async () => {
  const { spawnSync } = await import('node:child_process');
  const result = spawnSync('node', ['scripts/validate-manifest.mjs', path.join(root, 'course.json')], { cwd: root, encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr || result.stdout);
  assert.match(result.stdout, /manifest valid: ai-bme-intro \(\d+ lectures\)/);
});

test('plain CLI invocation regenerates generated/course-data.json', async () => {
  const { spawnSync } = await import('node:child_process');
  const { rm, stat, readFile } = await import('node:fs/promises');
  const target = path.join(root, 'generated', 'course-data.json');
  await rm(target, { force: true });
  const result = spawnSync('node', ['scripts/build-content.mjs'], { cwd: root, encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr || result.stdout);
  const existsAfter = await stat(target).then(() => true, () => false);
  assert.ok(existsAfter, 'generated/course-data.json missing after plain CLI run');
  const data = JSON.parse(await readFile(target, 'utf8'));
  assert.equal(data.lessons.length, names.length);
});

test('missing metadata and invalid code mapping fail without artifact', async () => {
  await setup();
  try {
    await writeFile(path.join(sourceDir, names[0]), 'no title');
    await assert.rejects(generate({ sourceDir, outputDir }), /Missing title metadata/);
    await copyFile(path.join(root, names[0]), path.join(sourceDir, names[0]));
    await writeFile(path.join(sourceDir, 'course.json'), JSON.stringify(manifest));
    await rm(path.join(sourceDir, 'code', 'session_05_bfs_dfs.py'));
    await assert.rejects(generate({ sourceDir, outputDir }), /Invalid code mapping/);
    await assert.rejects(readFile(path.join(outputDir, 'course-data.json')));
  } finally { await rm(sourceDir, { recursive: true, force: true }); await rm(outputDir, { recursive: true, force: true }); }
});

test('non-conforming session filenames fail loud instead of vanishing', async () => {
  await setup();
  try {
    await writeFile(path.join(sourceDir, 'session_6_stray.md'), '# جلسه شش');
    await assert.rejects(generate({ sourceDir, outputDir }), /files must match session_NN/);
    await assert.rejects(readFile(path.join(outputDir, 'course-data.json')));
  } finally { await rm(sourceDir, { recursive: true, force: true }); await rm(outputDir, { recursive: true, force: true }); }
});

test.after(async () => rm(temporary, { recursive: true, force: true }));
