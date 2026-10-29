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

test('generates 29 student lessons, publishes sessions 1–5 whole, clips 6–29', async () => {
  await setup();
  try {
    const data = await generate({ sourceDir, outputDir });
    assert.equal(data.lessons.length, 29);
    assert.equal(data.codes.length, 25);
    const guideTail = await readFile(path.join(sourceDir, names[5]), 'utf8');
    const guideMatch = guideTail.match(/^## .*راهنمای مدرس.*$/m);
    const sentinel = guideTail.slice(guideMatch.index + guideMatch[0].length).trim().split(/\s+/)[0];
    assert.ok(sentinel);
    const privateSource = guideTail.replace(sentinel, `INSTRUCTOR-ONLY-${sentinel}-9f3c`);
    await writeFile(path.join(sourceDir, names[5]), privateSource);
    const privateData = await generate({ sourceDir, outputDir });
    assert.ok(!JSON.stringify(privateData).includes(`INSTRUCTOR-ONLY-${sentinel}-9f3c`));
    assert.ok(!(await readFile(path.join(outputDir, 'course-data.json'), 'utf8')).includes(`INSTRUCTOR-ONLY-${sentinel}-9f3c`));
    await writeFile(path.join(sourceDir, names[5]), guideTail);
    const selfStudy = data.codes.at(-1);
    assert.equal(selfStudy.path, 'code/python_selfstudy.ipynb');
    assert.equal(selfStudy.githubUrl, 'https://github.com/DaneshJoy/ai_bme_intro/blob/main/code/python_selfstudy.ipynb');
    assert.equal(selfStudy.supplemental, true);
    assert.equal('session' in selfStudy, false);
    assert.ok((await readFile(path.join(outputDir, 'course-data.json'), 'utf8')).length);
    for (const [i, lesson] of data.lessons.entries()) {
      const original = await readFile(path.join(sourceDir, lesson.sourcePath), 'utf8');
      assert.equal(lesson.order, i + 1);
      if (i < 5) assert.equal(lesson.content, original);
      else {
        const boundary = original.match(/^## .*راهنمای مدرس.*$/m);
        assert.ok(boundary);
        assert.equal(lesson.content, original.slice(0, boundary.index).trimEnd());
      }
    }
  } finally { await rm(sourceDir, { recursive: true, force: true }); await rm(outputDir, { recursive: true, force: true }); }
});

test('missing or duplicate Unicode guide headings fail without public artifact', async () => {
  await setup();
  const file = path.join(sourceDir, names[5]);
  const original = await readFile(file, 'utf8');
  try {
    await generate({ sourceDir, outputDir });
    assert.ok((await readFile(path.join(outputDir, 'course-data.json'), 'utf8')).length);
    await writeFile(file, original.replace(/^## .*راهنمای مدرس.*$/mu, '## unknown boundary'));
    await assert.rejects(generate({ sourceDir, outputDir }), new RegExp(names[5]));
    await assert.rejects(readFile(path.join(outputDir, 'course-data.json')));
    await writeFile(file, original + '\n## راهنمای مدرس duplicate\n');
    await assert.rejects(generate({ sourceDir, outputDir }), /exactly one/);
    await assert.rejects(readFile(path.join(outputDir, 'course-data.json')));
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
  assert.match(result.stdout, /manifest valid: ai-bme-intro \(29 lectures\)/);
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

test.after(async () => rm(temporary, { recursive: true, force: true }));
