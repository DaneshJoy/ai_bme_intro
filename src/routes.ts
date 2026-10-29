import { escape, markdown, renderCodeIndex } from './render.ts';

type CourseData = {
  manifest: { title: string; description: string };
  lessons: { id: string; title: string; order: number; content: string; codes: { name: string; githubUrl: string; type: string }[] }[];
  codes: { name: string; session?: number; githubUrl: string; type: string; supplemental?: boolean }[];
};

export function renderRoute(path: string, data: CourseData, base: string) {
  const nav = `<header><a href="${base}">خانه</a><a href="${base}code/">فهرست کدها</a><button id="theme" type="button" aria-label="تغییر پوسته">◐</button></header>`;
  if (path === '') return `${nav}<section class="hero"><p>دورهٔ آموزشی</p><h1>${escape(data.manifest.title)}</h1><p>${escape(data.manifest.description)}</p><a href="${base}code/">مشاهدهٔ کدها و دفترچه‌ها</a></section><h2>جلسه‌ها</h2><ol>${data.lessons.map((item) => `<li><a href="${base}sessions/${item.id}/">${escape(item.title)}</a></li>`).join('')}</ol>`;
  if (path === 'code') return renderCodeIndex(data.codes, base);
  const match = path.match(/^sessions\/([^/]+)$/);
  const lesson = match && data.lessons.find((item) => item.id === match[1]);
  if (lesson) {
    const index = data.lessons.indexOf(lesson);
    return `${nav}<article><p>جلسه ${lesson.order}</p><h1>${escape(lesson.title)}</h1><div class="content">${markdown(lesson.content)}</div><aside>${lesson.codes.length ? `<h2>کدهای این جلسه</h2>${lesson.codes.map((code) => `<a href="${escape(code.githubUrl)}" dir="ltr" rel="noopener noreferrer">${escape(code.name)}</a>`).join(' · ')}` : ''}</aside><footer>${index ? `<a href="${base}sessions/${data.lessons[index - 1].id}/">جلسهٔ قبل</a>` : ''}${index < data.lessons.length - 1 ? `<a href="${base}sessions/${data.lessons[index + 1].id}/">جلسهٔ بعد</a>` : ''}</footer></article>`;
  }
  return `${nav}<h1>صفحه پیدا نشد</h1><p>صفحهٔ درخواستی وجود ندارد.</p>`;
}
