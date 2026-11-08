import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
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
  home: '\u0645\u062d\u062a\u0648\u0627',
  codeIndex: '\u06a9\u062f\u0647\u0627',
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

test('github alert callouts render with type styling, not raw tags', () => {
  const note = markdown('> [!NOTE]\n> متن یادداشت');
  assert.ok(note.includes('callout callout-note'), `note class missing: ${note}`);
  assert.ok(note.includes('یادداشت'), `Persian label missing: ${note}`);
  assert.ok(!note.includes('[!NOTE]'), `raw tag leaked: ${note}`);
  assert.ok(markdown('> [!WARNING]\n> متن هشدار').includes('callout-warning'));
  assert.ok(markdown('> [!TIP]\n> متن نکته').includes('callout-tip'));
  assert.ok(markdown('> [!IMPORTANT]\n> متن مهم').includes('callout-important'));
  assert.ok(markdown('> یک نقل‌قول معمولی').includes('<blockquote>') && !markdown('> یک نقل‌قول معمولی').includes('callout'), 'plain blockquote should stay plain');
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
  const home = renderRoute('', courseData, '/base/');
  const codeIndex = renderCodeIndex(courseData.codes, '/base/');
  assert.ok(home.includes(`aria-current="page">${labels.home}</a>`));
  assert.ok(codeIndex.includes(`aria-current="page">${labels.codeIndex}</a>`));
});
test('theme button renders inline SVG sun/moon icons with CSS state visibility', () => {
  const home = renderRoute('', courseData, '/base/');
  const codeIndex = renderCodeIndex(courseData.codes, '/base/');
  for (const rendered of [home, codeIndex]) {
    assert.ok(rendered.includes('<svg class="icon-sun"'), 'sun SVG missing from theme button');
    assert.ok(rendered.includes('<svg class="icon-moon"'), 'moon SVG missing from theme button');
    assert.doesNotMatch(rendered, /[\u2600\u{1F319}]/u, 'emoji theme icon leaked into markup');
  }
  assert.doesNotMatch(sourceMain, /textContent\s*=\s*theme/, 'emoji textContent swap must be removed');
  assert.match(css, /#theme\s*\{[^}]*inline-size:\s*40px/);
  assert.match(css, /#theme svg\s*\{[^}]*stroke:\s*currentColor/);
  assert.match(css, /:root\[data-theme="dark"\]\s*#theme\s+\.icon-sun/);
});
test('pre-paint theme initializer and storage-safe theme handling', () => {
  const inline = html.match(/<script>([\s\S]*?)<\/script>/);
  assert.ok(inline, 'no inline pre-paint theme script in index.html');
  const run = (saved, blocked, dark) => {
    const document = { documentElement: { dataset: {} } };
    const storage = {
      getItem: () => { if (blocked) throw new Error('storage blocked'); return saved; },
      setItem: () => { if (blocked) throw new Error('storage blocked'); },
    };
    vm.runInNewContext(inline[1], { document, localStorage: storage, matchMedia: () => ({ matches: dark }) });
    return document.documentElement.dataset.theme;
  };
  assert.equal(run('light', false, true), 'light', 'saved light must win over system dark');
  assert.equal(run('dark', false, false), 'dark', 'saved dark must win over system light');
  assert.equal(run(null, false, true), 'dark', 'missing saved falls back to system dark');
  assert.equal(run(null, false, false), 'light', 'missing saved falls back to system light');
  assert.equal(run('', false, true), 'dark', 'empty saved falls back to system dark');
  assert.equal(run('sepia', false, false), 'light', 'unknown saved falls back to system light');
  assert.equal(run('dark', true, false), 'light', 'storage failure falls back to system light');
  assert.equal(run(null, true, true), 'dark', 'storage failure falls back to system dark');
  assert.match(sourceMain, /currentTheme(?::\s*string\s*\|\s*null)?\s*=\s*document\.documentElement\.dataset\.theme/, 'main.ts must reuse existing data-theme');
  assert.match(sourceMain, /try\s*\{\s*currentTheme\s*=\s*localStorage\.getItem\('theme'\)/, 'storage read must be guarded');
  assert.match(sourceMain, /try\s*\{\s*localStorage\.setItem\('theme'/, 'storage write must be guarded');
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
test('static build contains 404.html', async () => {
  assert.ok((await readFile(path.join(root, 'dist/404.html'), 'utf8')).includes('pages-route'));
});
test('course stylesheet preserves RTL responsive layout and visible keyboard focus', () => {
  assert.match(html, /<html lang="fa" dir="rtl">/);
  assert.match(css, /:focus-visible/);
  assert.match(css, /@media/);
  assert.doesNotMatch(css, /\b(?:left|right)\s*:/);
});
