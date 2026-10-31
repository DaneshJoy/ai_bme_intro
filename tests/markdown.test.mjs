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
