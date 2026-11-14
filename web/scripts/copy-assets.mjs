// Copy figures from the research outputs (../outputs) into public/figures so docs can reference them.
// public/figures is generated (gitignored); run automatically before dev/build.
import { cpSync, mkdirSync, readdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const web = join(dirname(fileURLToPath(import.meta.url)), '..');
const out = join(web, '..', 'outputs');
const dst = join(web, 'public', 'figures');
const copyPngs = (from, to) => {
	if (!existsSync(from)) return 0;
	mkdirSync(to, { recursive: true });
	let n = 0;
	for (const f of readdirSync(from)) if (f.endsWith('.png')) { cpSync(join(from, f), join(to, f)); n++; }
	return n;
};
const n =
	copyPngs(join(out, 'experiments', 'en'), join(dst, 'en')) +
	copyPngs(join(out, 'experiments', 'vi'), join(dst, 'vi')) +
	copyPngs(out, join(dst, 'common'));
console.log(`copy-assets: ${n} figures -> public/figures`);
