// Build the chatbot knowledge index: split docs pages (by heading), result tables and script docstrings into chunks.
// Output: src/generated/rag-index.json (gitignored). Runs before `astro build` (npm prebuild).
import { readFileSync, readdirSync, statSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { join, dirname, relative, basename } from 'node:path';
import { fileURLToPath } from 'node:url';
import GithubSlugger from 'github-slugger';

const web = join(dirname(fileURLToPath(import.meta.url)), '..');
const repo = join(web, '..');
const docsDir = join(web, 'src', 'content', 'docs');
const GITHUB = 'https://github.com/ninhhaidang/ns05005-dancing-with-the-sars/blob/main';
const MAX = 1800; // characters per chunk

const walk = (d) => readdirSync(d).flatMap((f) => (statSync(join(d, f)).isDirectory() ? walk(join(d, f)) : [join(d, f)]));
const chunks = [];
const push = (c) => { if (c.text.trim().length > 40) chunks.push({ id: chunks.length, ...c, text: c.text.trim() }); };

function splitLong(text) {
	if (text.length <= MAX) return [text];
	const out = []; let cur = '';
	for (const para of text.split(/\n{2,}/)) {
		if (cur && cur.length + para.length > MAX) { out.push(cur); cur = ''; }
		cur += (cur ? '\n\n' : '') + para;
	}
	if (cur) out.push(cur);
	return out;
}

// 1. Docs pages
for (const file of walk(docsDir).filter((f) => /\.mdx?$/.test(f))) {
	const rel = relative(docsDir, file).replace(/\\/g, '/');
	const lang = rel.startsWith('vi/') ? 'vi' : 'en';
	let slug = rel.replace(/\.mdx?$/, '').replace(/(^|\/)index$/, '');
	const url = '/' + (slug ? slug + '/' : '');
	let src = readFileSync(file, 'utf8');
	let title = slug;
	const fm = src.match(/^---\n([\s\S]*?)\n---\n/);
	if (fm) {
		title = (fm[1].match(/^title:\s*['"]?(.+?)['"]?\s*$/m) || [])[1] || slug;
		src = src.slice(fm[0].length);
	}
	src = src.replace(/^import .*$/gm, '').replace(/<[A-Z][^>]*\/>/g, '');
	const sections = src.split(/^(?=#{2,3} )/m);
	const slugger = new GithubSlugger();
	for (const sec of sections) {
		const h = (sec.match(/^#{2,3} (.+)$/m) || [])[1];
		const anchor = h ? '#' + slugger.slug(h.replace(/[`*_]/g, '')) : '';
		for (const part of splitLong(sec)) push({ kind: 'doc', lang, title, heading: h || '', url: url + anchor, text: part });
	}
}

// 2. Result tables (English) and change patches
const tablesDir = join(repo, 'outputs', 'experiments', 'en', 'tables');
if (existsSync(tablesDir)) {
	for (const f of readdirSync(tablesDir).filter((f) => f.endsWith('.csv'))) {
		const csv = readFileSync(join(tablesDir, f), 'utf8');
		const exp = f.match(/^E(\d)/)?.[1];
		const lines = csv.trim().split('\n');
		const head = lines[0];
		for (let i = 1; i < lines.length; i += 40) {
			push({ kind: 'table', lang: 'any', title: `Result table ${f}`, heading: head.slice(0, 120), url: exp ? `/experiments/` : '/experiments/',
				text: `Table ${f} (rows ${i}-${Math.min(i + 39, lines.length - 1)} of ${lines.length - 1}):\n${head}\n${lines.slice(i, i + 40).join('\n')}` });
		}
	}
}
const patches = join(repo, 'outputs', 'change_patches.csv');
if (existsSync(patches)) push({ kind: 'table', lang: 'any', title: 'Change patches 22 Oct → 3 Nov 2026', heading: 'outputs/change_patches.csv', url: '/results/change/',
	text: 'All statistically significant change patches (class codes: 2 new water/flattening, 3 HH&HV decrease other, 4 HH&HV increase, 5 HV-only decrease, 6 HV-only increase):\n' + readFileSync(patches, 'utf8') });

// 3. Script docstrings
for (const f of readdirSync(join(repo, 'scripts')).filter((f) => /\.(py|js)$/.test(f))) {
	const src = readFileSync(join(repo, 'scripts', f), 'utf8');
	const doc = (src.match(/^"""([\s\S]*?)"""/) || src.match(/^\/\*([\s\S]*?)\*\//) || src.match(/^((?:\/\/.*\n)+)/) || [])[1];
	if (doc) push({ kind: 'code', lang: 'any', title: `Script scripts/${f}`, heading: basename(f), url: `${GITHUB}/scripts/${f}`, text: `scripts/${f} — module description:\n${doc}` });
}

mkdirSync(join(web, 'src', 'generated'), { recursive: true });
writeFileSync(join(web, 'src', 'generated', 'rag-index.json'), JSON.stringify({ built: new Date().toISOString(), chunks }));
const by = chunks.reduce((a, c) => ((a[c.kind + ':' + c.lang] = (a[c.kind + ':' + c.lang] || 0) + 1), a), {});
console.log(`rag-index: ${chunks.length} chunks`, by);
