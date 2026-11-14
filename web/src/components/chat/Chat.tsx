import { useEffect, useRef, useState } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import './chat.css';

type Lang = 'en' | 'vi';
interface Msg { role: 'user' | 'assistant'; content: string; sources?: { title: string; url: string }[]; tools?: string[]; error?: boolean }

const S = {
	en: {
		title: 'Project assistant', open: 'Ask the assistant', placeholder: 'Ask about the data, methods, results…', send: 'Send',
		thinking: 'Thinking…', clear: 'New chat', sources: 'Sources', expand: 'Open full page',
		disclaimer: 'AI answers can be wrong. Check the linked documentation.',
		hello: 'Hi! I can answer questions about this NISAR SAR project in Hưng Yên: data, methods, experiments, results and limitations. I can also read map values at any coordinates.',
		suggestions: ['What is the new water patch and is its cause known?', 'How accurate is the land cover map, really?', 'Why use SAR instead of Sentinel-2?', 'Which land cover class is least reliable and why?'],
		tool: { get_point_info: 'reading map values', list_change_patches: 'listing change patches', get_project_stats: 'reading statistics', search_docs: 'searching docs' } as Record<string, string>,
		rate: (s: number) => `Too many questions — please wait ${s} s.`, fail: 'The assistant is unavailable right now. Please try again later.',
	},
	vi: {
		title: 'Trợ lý dự án', open: 'Hỏi trợ lý AI', placeholder: 'Hỏi về dữ liệu, phương pháp, kết quả…', send: 'Gửi',
		thinking: 'Đang suy nghĩ…', clear: 'Cuộc trò chuyện mới', sources: 'Nguồn', expand: 'Mở trang đầy đủ',
		disclaimer: 'Câu trả lời của AI có thể sai. Hãy kiểm tra tài liệu được dẫn.',
		hello: 'Xin chào! Tôi trả lời các câu hỏi về dự án SAR NISAR ở Hưng Yên: dữ liệu, phương pháp, thí nghiệm, kết quả và giới hạn. Tôi cũng đọc được giá trị bản đồ tại bất kỳ tọa độ nào.',
		suggestions: ['Cụm nước mới là gì, đã biết nguyên nhân chưa?', 'Bản đồ lớp phủ thực sự chính xác đến đâu?', 'Sao dùng SAR mà không dùng Sentinel-2?', 'Lớp nào kém tin cậy nhất, vì sao?'],
		tool: { get_point_info: 'đang đọc giá trị bản đồ', list_change_patches: 'đang liệt kê mảng thay đổi', get_project_stats: 'đang đọc thống kê', search_docs: 'đang tìm tài liệu' } as Record<string, string>,
		rate: (s: number) => `Hỏi nhanh quá, vui lòng đợi ${s} giây.`, fail: 'Trợ lý đang không khả dụng. Vui lòng thử lại sau.',
	},
};

const KEY = 'dwts-chat-v1';
const load = (): Msg[] => { try { return JSON.parse(sessionStorage.getItem(KEY) ?? '[]'); } catch { return []; } };
const save = (m: Msg[]) => { try { sessionStorage.setItem(KEY, JSON.stringify(m.slice(-30))); } catch { /* ignore */ } };
const md = (s: string) => DOMPurify.sanitize(marked.parse(s, { async: false, breaks: true }) as string);

export default function Chat({ lang = 'en', mode = 'widget' }: { lang?: Lang; mode?: 'widget' | 'page' }) {
	const t = S[lang];
	const [open, setOpen] = useState(mode === 'page');
	const [msgs, setMsgs] = useState<Msg[]>([]);
	const [input, setInput] = useState('');
	const [busy, setBusy] = useState(false);
	const [status, setStatus] = useState('');
	const list = useRef<HTMLDivElement>(null);
	const abort = useRef<AbortController | null>(null);
	const inputRef = useRef<HTMLTextAreaElement>(null);

	useEffect(() => { setMsgs(load()); }, []);
	useEffect(() => { save(msgs); list.current?.scrollTo({ top: list.current.scrollHeight }); }, [msgs]);
	useEffect(() => {
		const h = (e: Event) => { const text = (e as CustomEvent).detail?.text; if (text) { setOpen(true); void send(text); } };
		window.addEventListener('dwts:ask', h);
		return () => window.removeEventListener('dwts:ask', h);
	});
	useEffect(() => { if (open) inputRef.current?.focus(); }, [open]);

	async function send(text: string) {
		const q = text.trim();
		if (!q || busy) return;
		const history: Msg[] = [...msgs.filter((m) => !m.error), { role: 'user', content: q }];
		setMsgs([...history, { role: 'assistant', content: '' }]);
		setInput(''); setBusy(true); setStatus(t.thinking);
		const ac = new AbortController(); abort.current = ac;
		const patch = (f: (m: Msg) => Msg) => setMsgs((ms) => [...ms.slice(0, -1), f(ms[ms.length - 1])]);
		try {
			const r = await fetch('/api/chat', {
				method: 'POST', headers: { 'content-type': 'application/json' }, signal: ac.signal,
				body: JSON.stringify({ lang, messages: history.map(({ role, content }) => ({ role, content })) }),
			});
			if (r.status === 429) { const j = await r.json(); patch((m) => ({ ...m, content: t.rate(j.retryAfter ?? 60), error: true })); return; }
			if (!r.ok || !r.body) throw new Error(String(r.status));
			const reader = r.body.getReader(); const dec = new TextDecoder(); let buf = '';
			for (;;) {
				const { value, done } = await reader.read();
				if (done) break;
				buf += dec.decode(value, { stream: true });
				let i;
				while ((i = buf.indexOf('\n\n')) >= 0) {
					const line = buf.slice(0, i).replace(/^data: /, ''); buf = buf.slice(i + 2);
					if (!line) continue;
					const ev = JSON.parse(line);
					if (ev.type === 'delta') { setStatus(''); patch((m) => ({ ...m, content: m.content + ev.text })); }
					else if (ev.type === 'sources') patch((m) => ({ ...m, sources: ev.items }));
					else if (ev.type === 'tool') { setStatus((t.tool[ev.name] ?? ev.name) + '…'); patch((m) => ({ ...m, tools: [...(m.tools ?? []), ev.name] })); }
					else if (ev.type === 'error') patch((m) => ({ ...m, content: m.content + (m.content ? '\n\n' : '') + ev.message, error: true }));
				}
			}
		} catch (e) {
			if ((e as Error).name !== 'AbortError') patch((m) => ({ ...m, content: t.fail, error: true }));
		} finally {
			setBusy(false); setStatus(''); abort.current = null;
		}
	}

	const prefix = lang === 'vi' ? '/vi' : '';
	const fixUrl = (u: string) => (u.startsWith('/') && lang === 'vi' && !u.startsWith('/vi/') ? prefix + u : u);

	const panel = (
		<div className={`dwts-chat ${mode}`} role="dialog" aria-label={t.title}>
			<header>
				<strong>💬 {t.title}</strong>
				<div>
					{msgs.length > 0 && <button onClick={() => { abort.current?.abort(); setMsgs([]); }} title={t.clear}>↺</button>}
					{mode === 'widget' && <a href={`${prefix}/chat/`} title={t.expand}>⤢</a>}
					{mode === 'widget' && <button onClick={() => setOpen(false)} aria-label="close">✕</button>}
				</div>
			</header>
			<div className="dwts-chat-list" ref={list}>
				{msgs.length === 0 && (
					<div className="dwts-chat-empty">
						<p>{t.hello}</p>
						<div className="dwts-chat-sugg">{t.suggestions.map((s) => <button key={s} onClick={() => send(s)}>{s}</button>)}</div>
					</div>
				)}
				{msgs.map((m, i) => (
					<div key={i} className={`dwts-msg ${m.role}${m.error ? ' err' : ''}`}>
						{m.role === 'assistant'
							? <div className="dwts-md" dangerouslySetInnerHTML={{ __html: md(m.content || (busy && i === msgs.length - 1 ? '' : '…')) }} />
							: <div>{m.content}</div>}
						{m.role === 'assistant' && busy && i === msgs.length - 1 && status && <div className="dwts-status">{status}</div>}
						{m.role === 'assistant' && m.sources && m.sources.length > 0 && m.content && !(busy && i === msgs.length - 1) && (
							<details className="dwts-src"><summary>{t.sources} ({m.sources.length})</summary>
								<ul>{m.sources.map((s) => <li key={s.url}><a href={fixUrl(s.url)}>{s.title}</a></li>)}</ul>
							</details>
						)}
					</div>
				))}
			</div>
			<form onSubmit={(e) => { e.preventDefault(); void send(input); }}>
				<textarea
					ref={inputRef} rows={2} value={input} maxLength={2000} placeholder={t.placeholder}
					onChange={(e) => setInput(e.target.value)}
					onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); void send(input); } }}
				/>
				{busy ? <button type="button" onClick={() => abort.current?.abort()}>■</button> : <button type="submit" disabled={!input.trim()}>{t.send}</button>}
			</form>
			<p className="dwts-chat-note">{t.disclaimer}</p>
		</div>
	);

	if (mode === 'page') return panel;
	return (
		<>
			{open && panel}
			{!open && <button className="dwts-chat-fab" onClick={() => setOpen(true)} aria-label={t.open}>💬 <span>{t.open}</span></button>}
		</>
	);
}
