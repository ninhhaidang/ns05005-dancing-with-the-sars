import { resolve } from 'node:path';

const env = (k: string, d = '') => process.env[k] ?? d;

export const config = {
	dataDir: env('DATA_DIR', resolve(process.cwd(), '../data/web')),
	cacheDir: env('CACHE_DIR', resolve(process.cwd(), '.cache')),
	llm: {
		baseURL: env('LLM_BASE_URL', 'http://omniroute:20128/v1'),
		apiKey: env('LLM_API_KEY'),
		model: env('LLM_MODEL', 'gemini-3.8-flash'),
		embedModel: env('EMBED_MODEL'),
		maxTokens: parseInt(env('LLM_MAX_TOKENS', '1800')),
		temperature: parseFloat(env('LLM_TEMPERATURE', '0.3')),
	},
	rateLimitPerMin: parseInt(env('CHAT_RATE_PER_MIN', '8')),
	rateLimitPerDay: parseInt(env('CHAT_RATE_PER_DAY', '150')),
};
