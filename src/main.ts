import './styles.css';
import { restoreRoute } from './render';
import { renderRoute } from './routes';

type CourseData = {
  manifest: { title: string; description: string; lectures: { id: string; title: string; order: number }[] };
  lessons: { id: string; title: string; order: number; content: string; sourcePath: string; codes: { name: string; githubUrl: string; type: string }[] }[];
  codes: { name: string; session?: number; githubUrl: string; type: string; supplemental?: boolean }[];
};
const app = document.querySelector<HTMLElement>('#app')!;
const base = import.meta.env.BASE_URL;
const data: CourseData = await fetch(`${base}generated/course-data.json`).then((r) => { if (!r.ok) throw Error('اطلاعات دوره بارگذاری نشد.'); return r.json(); });
const savedRoute = sessionStorage.getItem('pages-route');
if (savedRoute) { sessionStorage.removeItem('pages-route'); history.replaceState(null, '', restoreRoute(savedRoute, base)); }
const path = location.pathname.startsWith(base) ? location.pathname.slice(base.length).replace(/\/$/, '') : '__not_found__';
app.innerHTML = renderRoute(path, data, base);
const currentTheme = localStorage.getItem('theme') || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
document.documentElement.dataset.theme = currentTheme;
document.querySelector('#theme')?.addEventListener('click', () => { const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'; document.documentElement.dataset.theme = next; localStorage.setItem('theme', next); });
