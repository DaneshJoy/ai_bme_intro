export const escape = (text: string) => text.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');
const url = (value: string) => { try { const parsed = new URL(value); return parsed.protocol === 'https:' || parsed.protocol === 'http:' ? escape(value) : ''; } catch { return ''; } };
const inline = (text: string) => escape(text)
  .replace(/`([^`]+)`/g, '<code dir="ltr">$1</code>')
  .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  .replace(/\*([^*]+)\*/g, '<em>$1</em>')
  .replace(/\[([^\]]+)\]\(([^\s)]+)\)/g, (_match, label: string, target: string) => { const safe = url(target); return safe ? `<a href="${safe}" rel="noopener noreferrer">${label}</a>` : label; });

export const markdown = (source: string) => {
  // RTL wrapper tags are authoring noise (already RTL document); drop lone wrapper lines only.
  const lines = source.split(/\r?\n/).filter((entry) => !/^\s*(<\/?div( dir="rtl")?\s*\/?>)\s*$/.test(entry));
  const out: string[] = [];
  for (let i = 0; i < lines.length;) {
    const line = lines[i];
    const fence = line.match(/^```([^`]*)$/);
    if (fence) { const body: string[] = []; i++; while (i < lines.length && !/^```\s*$/.test(lines[i])) body.push(lines[i++]); i++; if (fence[1].trim() === 'mermaid') { out.push(`<div class="mermaid">${escape(body.join('\n'))}</div>`); continue; } out.push(`<pre dir="ltr"><code>${escape(body.join('\n'))}</code></pre>`); continue; }
    if (/^(-{3,}|\*{3,})\s*$/.test(line)) { out.push('<hr>'); i++; continue; }
    const heading = line.match(/^(#{1,6})\s+(.+)$/);
    if (heading) { const n = heading[1].length; out.push(`<h${n}>${inline(heading[2])}</h${n}>`); i++; continue; }
    const cells = (row: string) => { const trimmed = row.trim().replace(/^\|/, '').replace(/\|$/, ''); return trimmed.length ? trimmed.split('|') : []; };
    const alignOf = (cell: string) => /^\s*:/.test(cell) && /:\s*$/.test(cell) ? 'center' : /:\s*$/.test(cell) ? 'end' : /^\s*:/.test(cell) ? 'start' : '';
    if (/^\s*\|.*\|\s*$/.test(line) && i + 1 < lines.length && cells(line).length > 1) {
      const separator = cells(lines[i + 1]);
      if (separator.length > 1 && separator.every((cell) => /^\s*:?-+:?\s*$/.test(cell))) {
        const aligns = separator.map(alignOf);
        const rowHtml = (row: string, tag: 'th' | 'td') => cells(row).map((cell, index) => `<${tag}${aligns[index] ? ` style="text-align:${aligns[index]}"` : ''}>${inline(cell.trim())}</${tag}>`).join('');
        const rows = [line]; i += 2; while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i])) rows.push(lines[i++]);
        out.push(`<div class="table-scroll"><table><thead><tr>${rowHtml(rows[0], 'th')}</tr></thead><tbody>${rows.slice(1).map((row) => `<tr>${rowHtml(row, 'td')}</tr>`).join('')}</tbody></table></div>`); continue;
      }
    }
    if (/^>\s?/.test(line)) {
      const alert = lines[i].match(/^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s?(.*)$/);
      const alerts = { note: { icon: 'ℹ️', label: 'یادداشت' }, tip: { icon: '💡', label: 'نکته' }, important: { icon: '❗', label: 'مهم' }, warning: { icon: '⚠️', label: 'هشدار' }, caution: { icon: '🚫', label: 'اخطار جدی' } };
      if (alert) {
        const meta = alerts[alert[1].toLowerCase()];
        const body: string[] = alert[2] ? [inline(alert[2])] : [];
        i++; while (i < lines.length && /^>\s?/.test(lines[i])) body.push(inline(lines[i++].replace(/^>\s?/, '')));
        out.push(`<blockquote class="callout callout-${alert[1].toLowerCase()}"><div class="callout-title">${meta.icon} ${meta.label}</div><p>${body.filter(Boolean).join('<br>')}</p></blockquote>`);
        continue;
      }
      const quote: string[] = []; while (i < lines.length && /^>\s?/.test(lines[i])) quote.push(inline(lines[i++].replace(/^>\s?/, ''))); out.push(`<blockquote>${quote.join('<br>')}</blockquote>`); continue; }
    if (/^\s*([-*+] |\d+\. )/.test(line)) {
      const parseList = (indent: number, type?: 'ol' | 'ul'): string => {
        const marker = lines[i].match(/^(\s*)([-*+] |\d+\. )/)!;
        const tag = type ?? (/^\d/.test(marker[2]) ? 'ol' : 'ul');
        const items: string[] = [];
        while (i < lines.length) {
          const match = lines[i].match(/^(\s*)([-*+] |\d+\. )(.*)$/);
          if (!match) break;
          const level = match[1].length;
          const itemTag = /^\d/.test(match[2]) ? 'ol' : 'ul';
          if (level < indent) break;
          if (level > indent) {
            const nested = parseList(level, itemTag as 'ol' | 'ul');
            if (items.length) items[items.length - 1] = items.at(-1)!.replace('</li>', `${nested}</li>`);
            continue;
          }
          if (itemTag !== tag) break;
          items.push(`<li>${inline(match[3])}`);
          i++;
          if (i < lines.length) {
            const nested = lines[i].match(/^(\s*)([-*+] |\d+\. )/);
            if (nested && nested[1].length > indent) items[items.length - 1] += parseList(nested[1].length, /^\d/.test(nested[2]) ? 'ol' : 'ul');
          }
          items[items.length - 1] += '</li>';
        }
        return `<${tag}>${items.join('')}</${tag}>`;
      };
      out.push(parseList(line.match(/^\s*/)?.[0].length ?? 0)); continue;
    }
    if (!line.trim()) { i++; continue; }
    const para: string[] = []; while (i < lines.length && lines[i].trim() && !/^(#{1,6}\s|```|>\s?|\s*[-*+] |\s*\d+\. )/.test(lines[i])) para.push(lines[i++]);
    out.push(`<p>${para.map(inline).join('<br>')}</p>`);
  }
  return out.join('\n');
};

export function renderCodeIndex(codes: { supplemental?: boolean; session?: number; githubUrl: string; name: string }[], base: string) {
  return `<header><a href="${base}">خانه</a><a href="${base}code/">فهرست کدها</a><button id="theme" type="button" aria-label="تغییر پوسته" title="تغییر پوسته">☀️</button></header><h1>فهرست کدها و دفترچه‌ها</h1><ul class="code-index">${codes.map((code) => `<li>${code.supplemental ? 'تکمیلی · بدون وابستگی به جلسه' : `جلسه ${code.session}`} · <a href="${escape(code.githubUrl)}" dir="ltr" rel="noopener noreferrer">${escape(code.name)}</a></li>`).join('')}</ul>`;
}

export function restoreRoute(saved: string, base: string) {
  const route = JSON.parse(saved) as { relative: string; query: string; hash: string };
  return `${base}${route.relative}${route.query}${route.hash}`;
}
