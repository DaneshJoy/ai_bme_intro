import Ajv from 'ajv';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const schema = JSON.parse(await readFile(path.join(root, 'schemas/course-manifest.schema.json'), 'utf8'));
const manifestPath = path.resolve(process.argv[2] ?? path.join(root, 'course.json'));
const manifest = JSON.parse(await readFile(manifestPath, 'utf8'));
const ajv = new Ajv({ allErrors: true });
ajv.addFormat('bcp47', /^[a-z]{2,3}(?:-[a-z0-9]{2,8})*$/i);
ajv.addFormat('iso-date', (value) => /^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))?$/.test(value) && !Number.isNaN(Date.parse(value)));
const validate = ajv.compile(schema);
if (!validate(manifest)) {
  console.error(validate.errors);
  process.exitCode = 1;
} else {
  console.log(`manifest valid: ${manifest.id} (${manifest.lectures.length} lectures)`);
}
