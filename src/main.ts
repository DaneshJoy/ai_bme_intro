import './styles.css';
import 'katex/dist/katex.min.css';
import courseData from '../generated/course-data.json';
import { restoreRoute } from './render';
import { renderRoute } from './routes';

type CourseData = {
  manifest: { title: string; description: string; lectures: { id: string; title: string; order: number }[] };
  lessons: { id: string; title: string; order: number; content: string; sourcePath: string; codes: { name: string; githubUrl: string; type: string }[] }[];
  codes: { name: string; session?: number; githubUrl: string; type: string; supplemental?: boolean }[];
};
const app = document.querySelector<HTMLElement>('#app')!;
const base = import.meta.env.BASE_URL;
const data: CourseData = courseData;
const savedRoute = sessionStorage.getItem('pages-route');
if (savedRoute) { sessionStorage.removeItem('pages-route'); history.replaceState(null, '', restoreRoute(savedRoute, base)); }
const path = location.protocol === 'file:' ? '' : location.pathname.startsWith(base) ? location.pathname.slice(base.length).replace(/\/$/, '') : '__not_found__';
app.innerHTML = renderRoute(path, data, base);
for (const pre of [...app.querySelectorAll('pre')]) {
  const block = document.createElement('div');
  block.className = 'code-block';
  const header = document.createElement('div');
  header.className = 'code-header';
  header.innerHTML = `<span>کد</span>`;
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'copy-btn';
  const label = document.createTextNode('کپی');
  button.append(label);
  button.addEventListener('click', () => {
    navigator.clipboard?.writeText(pre.innerText).then(() => {
      label.textContent = '✓ کپی شد';
      button.classList.add('copied');
      setTimeout(() => { label.textContent = 'کپی'; button.classList.remove('copied'); }, 2000);
    });
  });
  header.append(button);
  pre.before(block);
  block.append(header, pre);
}
const maths = [...app.querySelectorAll<HTMLElement>('.math')];
if (maths.length) {
  const { default: katex } = await import('katex');
  for (const node of maths) {
    const tex = node.textContent ?? '';
    if (tex.trim()) katex.render(tex, node, { throwOnError: false, displayMode: node.classList.contains('math-display') });
  }
}
let currentTheme: string | null = document.documentElement.dataset.theme;
if (currentTheme !== 'dark' && currentTheme !== 'light') {
  try { currentTheme = localStorage.getItem('theme'); } catch { currentTheme = null; }
}
if (currentTheme !== 'dark' && currentTheme !== 'light') currentTheme = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
document.documentElement.dataset.theme = currentTheme;
const themeButton = document.querySelector<HTMLButtonElement>('#theme');
const applyTheme = (theme: string) => {
  document.documentElement.dataset.theme = theme;
};
applyTheme(currentTheme);
themeButton?.addEventListener('click', () => { const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'; applyTheme(next); try { localStorage.setItem('theme', next); } catch { /* storage unavailable */ } });
const diagrams = [...app.querySelectorAll<HTMLElement>('.mermaid')];
if (diagrams.length) {
  const originals = diagrams.map((node) => node.textContent ?? '');
  const mermaid = (await import('mermaid')).default;
  mermaid.initialize({ startOnLoad: false, theme: document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light' });
  try { await mermaid.run({ nodes: diagrams }); }
  catch (error) {
    console.error('mermaid rendering failed', error);
    diagrams.forEach((node, index) => { node.textContent = originals[index]; });
  }
}
