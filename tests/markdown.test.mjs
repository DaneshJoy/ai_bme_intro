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
