import OpenAI from 'openai';
import { config } from './config';

let client: OpenAI | null = null;
export function llm() {
	client ??= new OpenAI({ baseURL: config.llm.baseURL, apiKey: config.llm.apiKey || 'missing', timeout: 90_000, maxRetries: 1 });
	return client;
}
