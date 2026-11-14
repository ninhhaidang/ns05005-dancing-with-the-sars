import type { APIRoute } from 'astro';
import { samplePixel } from '../../lib/server/pixel';

export const prerender = false;

export const GET: APIRoute = async ({ url }) => {
	const lat = parseFloat(url.searchParams.get('lat') ?? ''), lon = parseFloat(url.searchParams.get('lon') ?? '');
	if (!isFinite(lat) || !isFinite(lon) || Math.abs(lat) > 90 || Math.abs(lon) > 180)
		return new Response(JSON.stringify({ error: 'lat, lon required' }), { status: 400 });
	try {
		return new Response(JSON.stringify(await samplePixel(lat, lon)), {
			headers: { 'content-type': 'application/json', 'cache-control': 'public, max-age=3600' },
		});
	} catch (e) {
		console.error('pixel', e);
		return new Response(JSON.stringify({ error: 'pixel lookup failed' }), { status: 500 });
	}
};
