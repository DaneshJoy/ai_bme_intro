import { escape, markdown, renderCodeIndex } from './render.ts';

type CourseData = {
  manifest: { title: string; description: string };
  lessons: { id: string; title: string; order: number; content: string; codes: { name: string; githubUrl: string; type: string }[] }[];
  codes: { name: string; session?: number; githubUrl: string; type: string; supplemental?: boolean }[];
};

const fa = (value: string) => value.replace(/\d/g, (d) => '۰۱۲۳۴۵۶۷۸۹'[+d]);
const badges = ['badge-green', 'badge-blue', 'badge-pink', 'badge-yellow', 'badge-purple', 'badge-teal'];

export function renderRoute(path: string, data: CourseData, base: string) {
  const nav = `<header><a href="${base}">خانه</a><a href="${base}code/">فهرست کدها</a><button id="theme" type="button" aria-label="تغییر پوسته" title="تغییر پوسته">☀️</button></header>`;
  if (path === '') return `${nav}<section class="hero"><div class="hero-badge">🎓 دورهٔ آموزشی</div><h1>${escape(data.manifest.title)}</h1><p class="hero-desc">${escape(data.manifest.description)}</p><div class="meta-row"><div class="meta-pill">📚 تعداد جلسات: <span>${fa(String(data.lessons.length))}</span></div></div></section><h2 class="section-title">💬 جلسه‌ها</h2><ol class="session-list">${data.lessons.map((item, index) => `<li><a class="session-card" href="${base}sessions/${item.id}/"><span class="step-num ${badges[index % badges.length]}">${fa(String(item.order))}</span><span class="session-card__title">${escape(item.title)}</span></a></li>`).join('')}</ol>`;
  if (path === 'code') return renderCodeIndex(data.codes, base);
  const match = path.match(/^sessions\/([^/]+)$/);
  const lesson = match && data.lessons.find((item) => item.id === match[1]);
  if (lesson) {
    const index = data.lessons.indexOf(lesson);
    return `${nav}<article><span class="lesson-badge">📖 جلسه ${fa(String(lesson.order))}</span><div class="content">${markdown(lesson.content)}</div><aside class="lesson-code">${lesson.codes.length ? `<h2>🧩 کدهای این جلسه</h2>${lesson.codes.map((code) => `<a href="${escape(code.githubUrl)}" dir="ltr" rel="noopener noreferrer">${escape(code.name)}</a>`).join('')}` : ''}</aside><footer class="article-nav">${index ? `<a href="${base}sessions/${data.lessons[index - 1].id}/">جلسهٔ قبل →</a>` : '<span></span>'}${index < data.lessons.length - 1 ? `<a href="${base}sessions/${data.lessons[index + 1].id}/">← جلسهٔ بعد</a>` : '<span></span>'}</footer></article>`;
  }
  return `${nav}<h1>صفحه پیدا نشد</h1><p>صفحهٔ درخواستی وجود ندارد.</p>`;
}
