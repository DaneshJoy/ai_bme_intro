import test from 'node:test';
import assert from 'node:assert/strict';
import { markdown } from '../src/render.ts';

test('nested lists can switch list type at each indentation level', () => {
  assert.equal(markdown('- parent\n  1. nested ordered\n- sibling'), '<ul><li>parent<ol><li>nested ordered</li></ol></li><li>sibling</li></ul>');
  assert.equal(markdown('1. parent\n  - nested unordered\n2. sibling'), '<ol><li>parent<ul><li>nested unordered</li></ul></li><li>sibling</li></ol>');
});

test('rendering escapes raw HTML and script XSS and rejects non-http Markdown URL schemes', () => {
  assert.equal(markdown('<img src=x>\n\n<script>alert(1)</script>\n\n[unsafe](javascript:alert(1)'), '<p>&lt;img src=x&gt;</p>\n<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>\n<p>unsafe</p>');
});

test('authored raw HTML blocks render through the tag/attribute allowlist', () => {
  const rendered = markdown('<div dir="ltr" align="center">\n\n<table style="border-collapse:collapse"><tr><th></th><th>x</th></tr><tr><td style="background:#7cc4ff"><b>🚑 S</b><br><small>(0,0)</small></td><td>■</td></tr></table>\n\n<p align="center"><i>caption <sub>M</sub></i></p>\n\n</div>');
  for (const expected of ['<div dir="ltr" align="center">', '<table style="border-collapse:collapse">', '<b>🚑 S</b>', '<br>', '<small>(0,0)</small>', '<p align="center"><i>caption <sub>M</sub></i></p>', '</div>']) {
    assert.ok(rendered.includes(expected), `missing ${expected}: ${rendered}`);
  }
  assert.ok(!rendered.includes('&lt;table'), `table escaped: ${rendered}`);
});

test('raw HTML blocks still neuter scripts, images and unsafe styles', () => {
  const rendered = markdown('<table><tr><td><script>alert(1)</script><img src=x onerror="alert(2)"></td></tr><tr><td style="background:url(javascript:alert(3))">x</td></tr></table>');
  assert.ok(!rendered.includes('<script'), `script survived: ${rendered}`);
  assert.ok(!rendered.includes('<img'), `image survived: ${rendered}`);
  assert.ok(!rendered.includes('url('), `unsafe style survived: ${rendered}`);
  assert.ok(rendered.includes('&lt;script&gt;'), `text not preserved: ${rendered}`);
});

test('inline and display math are wrapped for KaTeX, content stays escaped', () => {
  assert.equal(markdown('عمق <b>نمی‌شود</b> $d$ یعنی $x<y$'), '<p>عمق &lt;b&gt;نمی‌شود&lt;/b&gt; <span class="math math-inline">d</span> یعنی <span class="math math-inline">x&lt;y</span></p>');
  assert.equal(markdown('$a*b*c$'), '<p><span class="math math-inline">a*b*c</span></p>');
  assert.equal(markdown('$$T_{\\text{BFS}} = O(b^d)$$'), '<div class="math math-display">T_{\\text{BFS}} = O(b^d)</div>');
  assert.equal(markdown('| زمان | $O(b^d)$ |\n|--:|--:|\n| حافظه | $O(bm)$ |'), '<div class="table-scroll"><table><thead><tr><th style="text-align:end">زمان</th><th style="text-align:end"><span class="math math-inline">O(b^d)</span></th></tr></thead><tbody><tr><td style="text-align:end">حافظه</td><td style="text-align:end"><span class="math math-inline">O(bm)</span></td></tr></tbody></table></div>');
});

test('table cells pass only the authored LTR span and br allowlist; other HTML stays escaped', () => {
  assert.equal(markdown('| گام | پشته |\n|---|---|\n| ۱ | <span dir="ltr">`ER,` **`RAD, LAB`**</span> |'), '<div class="table-scroll"><table><thead><tr><th>گام</th><th>پشته</th></tr></thead><tbody><tr><td>۱</td><td><span dir="ltr"><code dir="ltr">ER,</code> <strong><code dir="ltr">RAD, LAB</code></strong></span></td></tr></tbody></table></div>');
  assert.equal(markdown('| گام | پشته |\n|---|---|\n| ۱ | **`PHARM`**<br>`LAB`<br>━━━━ |'), '<div class="table-scroll"><table><thead><tr><th>گام</th><th>پشته</th></tr></thead><tbody><tr><td>۱</td><td><strong><code dir="ltr">PHARM</code></strong><br><code dir="ltr">LAB</code><br>━━━━</td></tr></tbody></table></div>');
  assert.equal(markdown('<span dir="rtl">x</span><span onclick="y()">z</span><br/>'), '<p>&lt;span dir=&quot;rtl&quot;&gt;x&lt;/span&gt;&lt;span onclick=&quot;y()&quot;&gt;z&lt;/span&gt;&lt;br/&gt;</p>');
});

test('details/summary blocks render as real elements and keep inner markdown', () => {
  assert.equal(markdown('<details>\n<summary>کلید پاسخ</summary>\n\n1. جواب `S`\n\n</details>'), '<details class="answer"><summary>کلید پاسخ</summary><ol><li>جواب <code dir="ltr">S</code></li></ol></details>');
});
