// Retrieval over the docs/tables/script index: BM25 (MiniSearch) always, plus embeddings when EMBED_MODEL is set.
import MiniSearch from 'minisearch';
import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import index from '../../generated/rag-index.json';
import { config } from './config';
import { llm } from './llm';

export interface Chunk { id: number; kind: 'doc' | 'table' | 'code'; lang: string; title: string; heading: string; url: string; text: string }
const CHUNKS = (index as { chunks: Chunk[] }).chunks;

const fold = (s: string) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd');
const ms = new MiniSearch<Chunk>({
	fields: ['title', 'heading', 'text'],
	storeFields: ['id'],
	processTerm: (t) => { const f = fold(t); return f.length > 1 ? f : null; },
	searchOptions: { boost: { title: 2, heading: 2 }, fuzzy: 0.15, prefix: true, combineWith: 'OR' },
});
ms.addAll(CHUNKS);

// ---- embeddings (optional) ----
let vecs: Promise<Float32Array[] | null> | null = null;
const norm = (v: number[]) => { const n = Math.hypot(...v) || 1; return Float32Array.from(v, (x) => x / n); };
async function embed(texts: string[]): Promise<Float32Array[]> {
	const out: Float32Array[] = [];
	for (let i = 0; i < texts.length; i += 64) {
		const r = await llm().embeddings.create({ model: config.llm.embedModel, input: texts.slice(i, i + 64) });
		for (const d of r.data.sort((a, b) => a.index - b.index)) out.push(norm(d.embedding as number[]));
	}
	return out;
}
function chunkVectors() {
	if (!config.llm.embedModel) return Promise.resolve(null);
	vecs ??= (async () => {
		const texts = CHUNKS.map((c) => `${c.title} — ${c.heading}\n${c.text}`);
		const key = createHash('sha1').update(config.llm.embedModel + JSON.stringify(texts)).digest('hex').slice(0, 16);
		const file = join(config.cacheDir, `emb-${key}.json`);
		if (existsSync(file)) return (JSON.parse(readFileSync(file, 'utf8')) as number[][]).map((v) => Float32Array.from(v));
		const v = await embed(texts);
		mkdirSync(config.cacheDir, { recursive: true });
		writeFileSync(file, JSON.stringify(v.map((x) => Array.from(x, (n) => Math.round(n * 1e5) / 1e5))));
		console.log(`rag: embedded ${v.length} chunks with ${config.llm.embedModel}`);
		return v;
	})().catch((e) => { console.error('rag: embeddings disabled:', e?.message ?? e); vecs = null; return null; });
	return vecs;
}
export function warmup() { void chunkVectors(); }

export async function retrieve(query: string, lang: 'en' | 'vi', k = 8): Promise<Chunk[]> {
	const scores = new Map<number, number>();
	const add = (ids: number[]) => ids.forEach((id, r) => scores.set(id, (scores.get(id) ?? 0) + 1 / (60 + r)));
	add(ms.search(query).slice(0, 40).map((r) => r.id as number));
	try {
		const V = await chunkVectors();
		if (V) {
			const [q] = await embed([query]);
			const sims = V.map((v, i) => { let s = 0; for (let j = 0; j < v.length; j++) s += v[j] * q[j]; return [i, s] as const; });
			add(sims.sort((a, b) => b[1] - a[1]).slice(0, 40).map(([i]) => CHUNKS[i].id));
		}
	} catch (e) {
		console.error('rag: query embedding failed', (e as Error)?.message);
	}
	// Prefer the reader's language for doc pages; tables/code are language-neutral.
	const ranked = [...scores.entries()]
		.map(([id, s]) => [CHUNKS[id], s * (CHUNKS[id].lang === lang || CHUNKS[id].lang === 'any' ? 1 : 0.6)] as const)
		.sort((a, b) => b[1] - a[1]);
	const out: Chunk[] = []; const seen = new Set<string>();
	for (const [c] of ranked) {
		const key = c.url.replace(/^\/vi\//, '/') + c.heading.slice(0, 20);
		if (c.kind === 'doc' && seen.has(key)) continue; // same section in the other language
		seen.add(key); out.push(c);
		if (out.length >= k) break;
	}
	return out;
}

export const formatContext = (cs: Chunk[]) =>
	cs.map((c, i) => `[${i + 1}] ${c.title}${c.heading ? ' › ' + c.heading : ''} (${c.url})\n${c.text}`).join('\n\n---\n\n');
