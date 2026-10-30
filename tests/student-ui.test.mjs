import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { escape, markdown, renderCodeIndex, restoreRoute } from '../src/render.ts';
import { renderRoute } from '../src/routes.ts';
import { generate } from '../scripts/build-content.mjs';
import vm from 'node:vm';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const html = await readFile(path.join(root, 'index.html'), 'utf8');
const css = await readFile(path.join(root, 'src/styles.css'), 'utf8');
const courseData = await generate({ outputDir: path.join(root, 'dist/generated') });
const sourceMain = await readFile(path.join(root, 'src/main.ts'), 'utf8');
const sourceRoutes = await readFile(path.join(root, 'src/routes.ts'), 'utf8');
const labels = {
  home: '\u062e\u0627\u0646\u0647',
  codeIndex: '\u0641\u0647\u0631\u0633\u062a \u06a9\u062f\u0647\u0627',
  sessions: '\u062c\u0644\u0633\u0647\u200c\u0647\u0627',
  notFound: '\u0635\u0641\u062d\u0647 \u067e\u06cc\u062f\u0627 \u0646\u0634\u062f',
};
test('markdown renders real and alignment-colon separator tables', () => {
  const rendered = markdown('| دوره | رویداد |\n|--:|--:|\n| ۱۹۵۰ | آزمون |');
  assert.ok(rendered.includes('<table>'), `no table: ${rendered}`);
  assert.ok(rendered.includes('text-align:end'), `no right-align: ${rendered}`);
  assert.ok(rendered.includes('آزمون</td>'), `cell not parsed: ${rendered}`);
  const centered = markdown('| الف | ب |\n|:---:|:---|\n| ۱ | ۲ |');
  assert.ok(centered.includes('text-align:center'), `center-align missing: ${centered}`);
  assert.ok(centered.includes('text-align:start'), `left-align missing: ${centered}`);
  const plain = markdown('| الف | ب |\n|---|---|\n| ۱ | ۲ |');
  assert.ok(plain.includes('<th>الف</th>') && plain.includes('<td>۱</td>'), `dash table regressed: ${plain}`);
  const paragraph = markdown('| this is just text |');
  assert.ok(!paragraph.includes('<table>'), `orphan pipe row parsed as table: ${paragraph}`);
});

test('lone RTL wrapper div tags are dropped from output', () => {
  const rendered = markdown('<div dir="rtl">\n| الف | ب |\n|--:|--:|\n| ۱ | ۲ |\n</div>');
  assert.ok(!rendered.includes('&lt;div'), `wrapper leaked: ${rendered}`);
  assert.ok(rendered.includes('<table>'), `table lost next to wrapper: ${rendered}`);
});

test('mermaid fences render as mermaid blocks, not raw code', () => {
  const rendered = markdown('```mermaid\ngraph TD; A-->B;\n```');
  assert.ok(rendered.includes('<div class="mermaid">'), `no mermaid div: ${rendered}`);
  assert.ok(rendered.includes('graph TD; A--&gt;B;'), `content not escaped properly: ${rendered}`);
  assert.ok(!rendered.includes('<pre'), `mermaid leaked into pre: ${rendered}`);
});

test('rendered lesson pages emit mermaid diagram blocks', () => {
  const lesson = courseData.lessons.find((item) => item.content.includes('```mermaid'));
  assert.ok(lesson, 'no session file contains a mermaid block');
  const rendered = renderRoute(`sessions/${lesson.id}`, courseData, '/ai_bme_intro/');
  assert.ok(rendered.includes('<div class="mermaid">'), 'mermaid block missing from lesson page');
});

test('routes render verified Persian UI labels without mojibake', () => {
  const routes = [
    [renderRoute('', courseData, '/base/'), [labels.home, '\u062c\u0644\u0633\u0647\u200c\u0647\u0627']],
    [renderRoute('code', courseData, '/base/'), [labels.codeIndex]],
    [renderRoute('missing', courseData, '/base/'), [labels.notFound]],
  ];
  for (const [rendered, expected] of routes) {
    for (const label of expected) assert.ok(rendered.includes(label), `missing Persian label: ${label}`);
    assert.doesNotMatch(rendered, /\ufffd/u);
  }
  for (const label of Object.values(labels)) assert.ok(sourceRoutes.includes(label), `missing Persian source label: ${label}`);
  assert.doesNotMatch(sourceRoutes, /\ufffd/u);
  assert.ok(renderCodeIndex(courseData.codes, '/base/').includes(labels.codeIndex));
});
test('route restoration preserves base path, query, and hash', () => {
  assert.equal(restoreRoute(JSON.stringify({ relative: 'sessions/one/', query: '?q=fa', hash: '#part' }), '/ai_bme_intro/'), '/ai_bme_intro/sessions/one/?q=fa#part');
});
test('code index renders supplemental notebook label and URL', async () => {
  const data = await generate({ outputDir: path.join(root, 'dist/generated') });
  const notebook = data.codes.find((code) => code.supplemental);
  assert.ok(notebook);
  const rendered = renderCodeIndex(data.codes, '/ai_bme_intro/');
  assert.ok(rendered.includes('تکمیلی · بدون وابستگی به جلسه'));
  assert.ok(rendered.includes(`href="${notebook.githubUrl}"`));
  assert.ok(rendered.includes(`>${notebook.name}</a>`));
});
test('404 route preserves the project path, query, and hash', async () => {
  const source = await readFile(path.join(root, 'public/404.html'), 'utf8');
  const script = source.match(/<script>([\s\S]*?)<\/script>/)[1];
  const location = new URL('https://example.test/ai_bme_intro/sessions/missing/?q=fa#part');
  const savedValues = new Map();
  let redirect;
  vm.runInNewContext(script, {
    location: { pathname: location.pathname, search: location.search, hash: location.hash, replace: (value) => { redirect = value; } },
    sessionStorage: { setItem: (key, value) => savedValues.set(key, value) },
  });
  const saved = JSON.parse(savedValues.get('pages-route'));
  assert.deepEqual(saved, { relative: 'sessions/missing/', query: '?q=fa', hash: '#part' });
  assert.equal(redirect, '/ai_bme_intro/');
  assert.equal(restoreRoute(JSON.stringify(saved), '/ai_bme_intro/'), '/ai_bme_intro/sessions/missing/?q=fa#part');
});
test('static build contains 404.html and excludes the instructor-tail marker', async () => {
  assert.ok((await readFile(path.join(root, 'dist/404.html'), 'utf8')).includes('pages-route'));
  const marker = (await readFile(path.join(root, 'session_06_uninformed_search_ucs_ids.md'), 'utf8')).match(/^## .*راهنمای مدرس.*$/m)[0];
  const sentinel = marker.match(/\(([^()]+)\)$/)[1];
  async function filesUnder(directory) {
    return (await Promise.all((await readdir(directory, { withFileTypes: true })).map((entry) => {
      const file = path.join(directory, entry.name);
      return entry.isDirectory() ? filesUnder(file) : [file];
    }))).flat();
  }
  for (const directory of ['generated', 'dist']) {
    const target = path.join(root, directory);
    try {
      for (const file of await filesUnder(target)) {
        assert.ok(!(await readFile(file)).includes(Buffer.from(sentinel)), `instructor marker leaked into ${file}`);
      }
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
    }
  }
});
test('course stylesheet preserves RTL responsive layout and visible keyboard focus', () => {
  assert.match(html, /<html lang="fa" dir="rtl">/);
  assert.match(css, /:focus-visible/);
  assert.match(css, /@media/);
  assert.doesNotMatch(css, /\b(?:left|right)\s*:/);
});
