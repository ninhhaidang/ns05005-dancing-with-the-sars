// In-memory per-IP limits (single container; resets on restart).
const hits = new Map<string, number[]>();

export function allow(ip: string, perMin: number, perDay: number): { ok: boolean; retryAfter?: number } {
	const now = Date.now();
	const arr = (hits.get(ip) ?? []).filter((t) => now - t < 86_400_000);
	const lastMin = arr.filter((t) => now - t < 60_000);
	if (lastMin.length >= perMin) return { ok: false, retryAfter: Math.ceil((60_000 - (now - lastMin[0])) / 1000) };
	if (arr.length >= perDay) return { ok: false, retryAfter: Math.ceil((86_400_000 - (now - arr[0])) / 1000) };
	arr.push(now);
	hits.set(ip, arr);
	if (hits.size > 50_000) hits.clear();
	return { ok: true };
}
