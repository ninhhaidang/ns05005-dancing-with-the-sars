// Tools the chat model can call: point lookup, change patches, project statistics, extra doc search.
import type OpenAI from 'openai';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { config } from './config';
import { samplePixel } from './pixel';
import { retrieve, formatContext } from './rag';

export const TOOLS: OpenAI.Chat.Completions.ChatCompletionTool[] = [
	{
		type: 'function',
		function: {
			name: 'get_point_info',
			description:
				'Look up the project rasters at a WGS84 point inside Hưng Yên province: SAR-only land cover class, number of 10 models agreeing, whether inside the area of applicability, change class 22 Oct→3 Nov 2026, and HH/HV backscatter (dB) on 2026-10-22, 2026-10-27 and 2026-11-03.',
			parameters: {
				type: 'object',
				properties: { lat: { type: 'number', description: 'latitude, degrees north' }, lon: { type: 'number', description: 'longitude, degrees east' } },
				required: ['lat', 'lon'],
			},
		},
	},
	{
		type: 'function',
		function: {
			name: 'list_change_patches',
			description: 'List the statistically significant change patches (22 Oct → 3 Nov 2026) with class, area, centroid and mean HH/HV dB per date, largest first.',
			parameters: { type: 'object', properties: { limit: { type: 'integer', description: 'max patches (default 10)' } } },
		},
	},
	{
		type: 'function',
		function: {
			name: 'get_project_stats',
			description: 'Map-level statistics: land cover areas/shares (after 3x3 majority filter), change class areas, area-of-applicability fraction, SAR acquisitions, map bounds.',
			parameters: { type: 'object', properties: {} },
		},
	},
	{
		type: 'function',
		function: {
			name: 'search_docs',
			description: 'Search the project documentation, result tables and script descriptions for more context. Use when the provided context is not enough.',
			parameters: { type: 'object', properties: { query: { type: 'string' } }, required: ['query'] },
		},
	},
];

const readJson = (f: string) => JSON.parse(readFileSync(join(config.dataDir, f), 'utf8'));

export async function runTool(name: string, args: Record<string, unknown>, lang: 'en' | 'vi') {
	switch (name) {
		case 'get_point_info': {
			const lat = Number(args.lat), lon = Number(args.lon);
			if (!isFinite(lat) || !isFinite(lon)) return { error: 'lat and lon must be numbers' };
			return samplePixel(lat, lon);
		}
		case 'list_change_patches': {
			const limit = Math.min(Math.max(Number(args.limit) || 10, 1), 50);
			const g = readJson('change_patches.geojson');
			return g.features.slice(0, limit).map((f: { properties: Record<string, unknown> }) => f.properties);
		}
		case 'get_project_stats': {
			const m = readJson('meta.json');
			const { pixel_bands, agreement_ramp, ...rest } = m;
			return rest;
		}
		case 'search_docs':
			return formatContext(await retrieve(String(args.query ?? ''), lang, 5));
		default:
			return { error: `unknown tool ${name}` };
	}
}
