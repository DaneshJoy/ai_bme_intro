import { readFile, readdir, mkdir, writeFile, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const generated = path.join(root, 'generated');
const guide = /^## .*راهنمای مدرس.*$/gmu;
const codeMappings = [
  [5, 'session_05_bfs_dfs.py'], [6, 'session_06_uninformed_search_ucs_ids.py'], [7, 'session_07_informed_heuristics.py'],
  [8, 'session_08_a_star.py'], [9, 'session_09_search_workshop.ipynb'], [9, 'session_09_search_workshop.py'],
  [10, 'session_10_local_search_genetic.py'], [11, 'session_11_gradient_descent.py'], [12, 'session_12_csp_backtracking.py'],
  [13, 'session_13_csp_scheduling.py'], [14, 'session_14_solutions.py'], [15, 'session_15_minimax_alphabeta.py'],
  [17, 'session_17_logic_expert_system.py'], [18, 'session_18_mdp_value_iteration.py'], [19, 'session_19_q_learning.py'],
  [20, 'session_20_bayes_markov.py'], [21, 'session_21_ml_metrics.py'], [22, 'session_22_sklearn_workshop.ipynb'],
  [22, 'session_22_sklearn_workshop.py'], [23, 'session_23_solutions.py'], [24, 'session_24_nn_from_scratch.py'],
  [25, 'session_25_biosignal_bci.py'], [26, 'session_26_medical_imaging.py'], [27, 'session_27_ethics_fairness.py'],
];
const supplementalCodes = ['python_selfstudy.ipynb'];

export async function generate({ sourceDir = root, outputDir = generated } = {}) {
  await rm(path.join(outputDir, 'course-data.json'), { force: true });
  const names = (await readdir(sourceDir)).filter((name) => /^session_\d{2}_.+\.md$/.test(name)).sort();
  const strays = (await readdir(sourceDir)).filter((name) => /^session_\d/.test(name) && !/^session_\d{2}_.+\.md$/.test(name));
  if (strays.length) throw new Error(`Session files must match session_NN_*.md: ${strays.join(', ')}`);
  if (!names.length) throw new Error('Expected at least one session file, found none');
  const ids = new Set();
  const lessons = [];
  for (const [index, name] of names.entries()) {
    const order = index + 1;
    const number = Number(name.slice(8, 10));
    if (number !== order) throw new Error(`Missing or duplicate session metadata at ${name}`);
    const filenameId = name.replace(/^session_/, '').replace(/\.md$/, '').replaceAll('_', '-');
    const id = `session-${filenameId}`;
    if (ids.has(id)) throw new Error(`Duplicate lecture ID ${id}`);
    ids.add(id);
    const source = await readFile(path.join(sourceDir, name), 'utf8');
    const title = source.match(/^#\s+(.+)$/m)?.[1]?.trim();
    if (!title) throw new Error(`Missing title metadata in ${name}`);
    if (title.includes('?')) throw new Error(`Invalid title metadata in ${name}`);
    const matches = [...source.matchAll(guide)];
    if (order <= 5) {
      if (matches.length) throw new Error(`Unexpected instructor-guide marker in approved student-only ${name}`);
    } else if (matches.length !== 1) {
      throw new Error(`Expected exactly one instructor-guide heading in ${name}; found ${matches.length}`);
    }
    const content = order <= 5 ? source : source.slice(0, matches[0].index).trimEnd();
    lessons.push({ id, title, order, durationMinutes: 0, objectives: [], status: 'published', content, sourcePath: name, codes: [] });
  }
  const codes = [];
  for (const [session, file] of codeMappings) {
    if (session > lessons.length) continue; // future session: file may not exist yet
    const fullPath = path.join(sourceDir, 'code', file);
    try { await readFile(fullPath); } catch { throw new Error(`Invalid code mapping: code/${file} does not exist`); }
    const code = { path: `code/${file}`, name: file, session, type: file.endsWith('.ipynb') ? 'notebook' : 'python', githubUrl: `https://github.com/DaneshJoy/ai_bme_intro/blob/main/code/${encodeURIComponent(file)}` };
    codes.push(code);
    lessons[session - 1].codes.push(code);
  }
  for (const file of supplementalCodes) {
    try { await readFile(path.join(sourceDir, 'code', file)); } catch { throw new Error(`Invalid supplemental code mapping: code/${file} does not exist`); }
    codes.push({ path: `code/${file}`, name: file, type: 'notebook', githubUrl: `https://github.com/DaneshJoy/ai_bme_intro/blob/main/code/${encodeURIComponent(file)}`, supplemental: true });
  }
  const manifestPath = path.join(sourceDir, 'course.json');
  const manifest = JSON.parse(await readFile(manifestPath, 'utf8'));
  if (manifest.id !== 'ai-bme-intro' || manifest.lectures.length < lessons.length) throw new Error('Course manifest lecture metadata is missing or invalid');
  for (let i = 0; i < lessons.length; i++) {
    for (const key of ['id', 'title', 'order']) if (manifest.lectures[i][key] !== lessons[i][key]) throw new Error(`Manifest ${key} mismatch for ${lessons[i].sourcePath}`);
  }
  await mkdir(outputDir, { recursive: true });
  await writeFile(path.join(outputDir, 'course-data.json'), JSON.stringify({ manifest, lessons, codes }));
  return { manifest, lessons, codes };
}

if (process.argv.includes('--validate')) {
  const validationOutput = path.join(root, 'generated-validation');
  await rm(validationOutput, { recursive: true, force: true });
  try {
    const result = await generate({ outputDir: validationOutput });
    console.log(`Validated ${result.lessons.length} lessons, instructor boundaries, manifest metadata, and code mappings.`);
  }
  finally { await rm(validationOutput, { recursive: true, force: true }); }
} else {
  const result = await generate();
  console.log(`Wrote ${result.lessons.length} lessons to generated/course-data.json`);
}

