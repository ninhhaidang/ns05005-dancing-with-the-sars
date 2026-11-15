import { useEffect, useMemo, useRef, useState } from 'react';
import * as maplibregl from 'maplibre-gl';
import type { Map as MLMap, StyleSpecification } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?url';
import './map.css';
import { T, type Lang } from './strings';
import Intro from './Intro';

maplibregl.setWorkerUrl(workerUrl);

const DATA = '/webdata';
const DATES = ['2026-10-22', '2026-10-27', '2026-11-03'] as const;
type DateKey = (typeof DATES)[number];
const SAR_ID = (d: DateKey) => `sar_${d.replaceAll('-', '')}`;
// Sentinel-2 is tiled to z15 (bilinear); SAR to z16 and drawn nearest so each 20 m / 10 m cell stays a sharp square
// (scripts/build_web.py IMG_MAXZ, SAR_MAXZ).
const IMG_MAXZ = 15;
const SAR_MAXZ = 16;
// Classified layers are tiled to z16 (scripts/build_web.py CAT_MAXZ); z13 tiles looked jagged when zoomed in.
const CAT_MAXZ = 16;
const CLUSTER: [number, number] = [106.484, 20.463];
const INTRO_KEY = 'dwts-intro-seen-v1';

interface Meta {
	bounds: [number, number, number, number];
	landcover: Record<string, { en: string; vi: string; color: string; area_km2: number; pct: number }>;
	change: { classes: Record<string, { en: string; vi: string; color: string | null; area_km2: number; pct: number }> };
	agreement_ramp: Record<string, string>;
	aoa: { threshold: number; outside_fraction: number };
	sar_stretch_db: { HH: number[]; HV: number[]; ratio: number[] };
}

type Base = DateKey | 's2' | null; // opaque image layer, one at a time
type Theme = 'landcover' | 'agreement' | null; // classified result, one at a time
type View = 'overview' | 'change' | 'landcover' | 'confidence' | 'sar';
const VIEWS: View[] = ['overview', 'change', 'landcover', 'confidence', 'sar'];

interface LayerState {
	base: Base;
	theme: Theme;
	aoa: boolean;
	change: boolean;
	labels: boolean;
	opacity: number;
	compare: boolean;
	left: DateKey;
	right: DateKey;
}

const PRESETS: Record<View, Partial<LayerState> & { center?: [number, number]; zoom?: number }> = {
	overview: { base: null, theme: 'landcover', change: true },
	sar: { base: '2026-10-22', theme: null },
	change: { base: '2026-11-03', change: true, theme: null, compare: true, left: '2026-10-22', right: '2026-11-03', center: CLUSTER, zoom: 13 },
	landcover: { base: null, theme: 'landcover' },
	confidence: { base: null, theme: 'agreement', aoa: true },
};

const DEFAULT: LayerState = {
	base: null, theme: 'landcover', aoa: false, change: true, labels: false,
	opacity: 0.85, compare: false, left: '2026-10-22', right: '2026-11-03',
};

// Basemap: Esri World Imagery only.
function baseStyle(): StyleSpecification {
	return {
		version: 8,
		sources: {
			base: {
				type: 'raster', tileSize: 256, maxzoom: 19,
				tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],
				attribution: 'Imagery © Esri, Maxar, Earthstar Geographics, and the GIS User Community',
			},
		},
		layers: [{ id: 'base', type: 'raster', source: 'base' }],
	} as StyleSpecification;
}

function addRaster(map: MLMap, id: string, ext: string, maxzoom: number, bounds: Meta['bounds'], nearest: boolean) {
	if (map.getSource(id)) return;
	map.addSource(id, { type: 'raster', tiles: [`${DATA}/tiles/${id}/{z}/{x}/{y}.${ext}`], tileSize: 256, minzoom: 8, maxzoom, bounds });
	map.addLayer({ id, type: 'raster', source: id, layout: { visibility: 'none' }, paint: { 'raster-resampling': nearest ? 'nearest' : 'linear', 'raster-fade-duration': 0 } });
}

function addOverlays(map: MLMap, meta: Meta, withData: boolean) {
	if (withData) {
		for (const d of DATES) addRaster(map, SAR_ID(d), 'webp', SAR_MAXZ, meta.bounds, true);
		addRaster(map, 's2_truecolor', 'webp', IMG_MAXZ, meta.bounds, false);
		addRaster(map, 'landcover', 'png', CAT_MAXZ, meta.bounds, true);
		addRaster(map, 'agreement', 'png', CAT_MAXZ, meta.bounds, true);
		addRaster(map, 'aoa', 'png', CAT_MAXZ, meta.bounds, true);
		addRaster(map, 'change', 'png', CAT_MAXZ, meta.bounds, true);
		map.addSource('labels', { type: 'geojson', data: `${DATA}/labels.geojson` });
		map.addLayer({ id: 'labels', type: 'line', source: 'labels', minzoom: 9, layout: { visibility: 'none' }, paint: { 'line-color': ['get', 'color'], 'line-width': 1.5 } });
	}
	map.addSource('patches', { type: 'geojson', data: `${DATA}/change_patches.geojson` });
	map.addLayer({ id: 'patches-fill', type: 'fill', source: 'patches', layout: { visibility: 'none' }, paint: { 'fill-color': ['get', 'color'], 'fill-opacity': 0.05 } });
	map.addLayer({ id: 'patches-line', type: 'line', source: 'patches', layout: { visibility: 'none' }, paint: { 'line-color': ['get', 'color'], 'line-width': ['interpolate', ['linear'], ['zoom'], 9, 1.5, 14, 2.5] } });
	map.addSource('aoi', { type: 'geojson', data: `${DATA}/aoi.geojson` });
	map.addLayer({ id: 'aoi', type: 'line', source: 'aoi', paint: { 'line-color': '#f97316', 'line-width': 1.6, 'line-dasharray': [3, 2] } });
}

function vis(map: MLMap, id: string, on: boolean, opacity?: number) {
	if (!map.getLayer(id)) return;
	map.setLayoutProperty(id, 'visibility', on ? 'visible' : 'none');
	if (opacity !== undefined && map.getLayer(id)?.type === 'raster') map.setPaintProperty(id, 'raster-opacity', opacity);
}

function readUrlState(): { state: LayerState; view: View | null; center?: [number, number]; zoom?: number } {
	const q = new URLSearchParams(window.location.search);
	const v = q.get('view') as View | null;
	const view = v && VIEWS.includes(v) ? v : null;
	const { center, zoom, ...p } = view ? PRESETS[view] : {};
	const state = { ...DEFAULT, ...p };
	const date = q.get('date') as DateKey | null;
	if (date && DATES.includes(date)) state.base = date;
	const lat = parseFloat(q.get('lat') ?? ''), lon = parseFloat(q.get('lon') ?? ''), z = parseFloat(q.get('z') ?? '');
	return { state, view, center: isFinite(lat) && isFinite(lon) ? [lon, lat] : center, zoom: isFinite(z) ? z : zoom };
}

const ddmm = (d: string) => d.slice(5).split('-').reverse().join('/');

interface PixelInfo {
	inside: boolean;
	lat: number;
	lon: number;
	landcover?: { code: number; en: string; vi: string };
	landcover_raw?: number;
	agreement?: number;
	inside_aoa?: boolean;
	aoa_di?: number;
	change?: { code: number; en: string; vi: string };
	hh_db?: Record<string, number | null>;
	hv_db?: Record<string, number | null>;
}

export default function MapApp({ lang = 'en', intro = false }: { lang?: Lang; intro?: boolean }) {
	const t = T[lang];
	const el = useRef<HTMLDivElement>(null);
	const el2 = useRef<HTMLDivElement>(null);
	const map = useRef<MLMap | null>(null);
	const map2 = useRef<MLMap | null>(null);
	const [meta, setMeta] = useState<Meta | null>(null);
	const [ready, setReady] = useState(0);
	const init = useMemo(() => (typeof window === 'undefined' ? { state: DEFAULT, view: null } : readUrlState()), []);
	const [s, setS] = useState<LayerState>(init.state);
	const [view, setView] = useState<View | null>(init.view); // highlighted guided view; cleared by any manual change
	const [split, setSplit] = useState(0.5);
	const [panelOpen, setPanelOpen] = useState(true);
	const [info, setInfo] = useState<{ px?: PixelInfo; patch?: Record<string, any>; loading?: boolean; err?: string } | null>(null);
	const set = (p: Partial<LayerState>) => { setView(null); setS((o) => ({ ...o, ...p })); };
	// Picking an image hides the result layer that would otherwise cover it.
	const setBase = (base: Base) => set(base ? { base, theme: null } : { base });
	const [showIntro, setShowIntro] = useState(false);
	const prefix = lang === 'vi' ? '/vi' : '';

	useEffect(() => {
		fetch(`${DATA}/meta.json`).then((r) => r.json()).then(setMeta).catch(() => setMeta(null));
		if (window.innerWidth < 720) setPanelOpen(false);
		// Intro modal: on the landing page, first visit, unless a specific view was linked.
		let seen = false;
		try { seen = localStorage.getItem(INTRO_KEY) === '1'; } catch { /* storage blocked */ }
		if (intro && !seen && !new URLSearchParams(location.search).has('view')) setShowIntro(true);
	}, []);

	function closeIntro() {
		setShowIntro(false);
		try { localStorage.setItem(INTRO_KEY, '1'); } catch { /* ignore */ }
	}

	// main map
	useEffect(() => {
		if (!meta || !el.current) return;
		const b = meta.bounds;
		const m = new maplibregl.Map({
			container: el.current,
			style: baseStyle(),
			bounds: init.center ? undefined : [[b[0], b[1]], [b[2], b[3]]],
			center: init.center,
			zoom: init.zoom,
			fitBoundsOptions: { padding: 30 },
			maxBounds: [[b[0] - 1.5, b[1] - 1.2], [b[2] + 1.5, b[3] + 1.2]],
			minZoom: 7,
			maxZoom: 17,
			attributionControl: { compact: true, customAttribution: 'NISAR GCOV © NASA/ISRO, ASF DAAC · Sentinel-2 © ESA/Copernicus' },
		});
		m.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');
		m.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-left');
		m.on('style.load', () => { addOverlays(m, meta, true); setReady((r) => r + 1); });
		// Start with the (long) attribution collapsed to its ⓘ button.
		m.once('load', () => el.current?.querySelector('.maplibregl-compact-show')?.classList.remove('maplibregl-compact-show'));
		m.on('click', (e) => onClick(m, e.lngLat.lng, e.lngLat.lat, e.point));
		m.on('mousemove', (e) => {
			const f = m.getLayer('patches-fill') ? m.queryRenderedFeatures(e.point, { layers: ['patches-fill'] }) : [];
			m.getCanvas().style.cursor = f.length ? 'pointer' : 'crosshair';
		});
		map.current = m;
		return () => { m.remove(); map.current = null; };
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [meta]);

	// compare (swipe) map
	useEffect(() => {
		if (!s.compare || !meta || !el2.current || !map.current) return;
		const m0 = map.current;
		const m = new maplibregl.Map({
			container: el2.current, style: baseStyle(), center: m0.getCenter(), zoom: m0.getZoom(), interactive: false, attributionControl: false,
		});
		m.on('style.load', () => {
			addRaster(m, SAR_ID(s.right), 'webp', SAR_MAXZ, meta.bounds, true);
			addOverlays(m, meta, false);
			setReady((r) => r + 1);
		});
		const sync = () => m.jumpTo({ center: m0.getCenter(), zoom: m0.getZoom(), bearing: m0.getBearing(), pitch: m0.getPitch() });
		m0.on('move', sync);
		map2.current = m;
		return () => { m0.off('move', sync); m.remove(); map2.current = null; };
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [s.compare, s.right, meta]);

	// apply layer state
	useEffect(() => {
		const m = map.current;
		if (!m || !m.getLayer('aoi')) return;
		const sarOn = s.compare ? s.left : s.base;
		for (const d of DATES) vis(m, SAR_ID(d), sarOn === d, 1);
		vis(m, 's2_truecolor', s.base === 's2' && !s.compare, 1);
		vis(m, 'landcover', s.theme === 'landcover' && !s.compare, s.opacity);
		vis(m, 'agreement', s.theme === 'agreement' && !s.compare, s.opacity);
		vis(m, 'aoa', s.aoa && !s.compare, 1);
		vis(m, 'change', s.change && !s.compare, 0.9);
		vis(m, 'patches-fill', s.change);
		vis(m, 'patches-line', s.change);
		vis(m, 'labels', s.labels);
		const m2 = map2.current;
		if (m2?.getLayer('aoi')) {
			vis(m2, SAR_ID(s.right), true, 1);
			vis(m2, 'patches-line', s.change);
		}
		// Keep the URL shareable: a guided view (plus SAR date), or nothing once the user has customised.
		const url = new URL(window.location.href);
		if (view) url.searchParams.set('view', view); else url.searchParams.delete('view');
		if (view && !s.compare && s.base && s.base !== 's2') url.searchParams.set('date', s.base); else url.searchParams.delete('date');
		history.replaceState(null, '', url);
	}, [s, view, ready]);

	// swipe clip
	useEffect(() => {
		if (!el2.current || !el.current) return;
		el2.current.style.clipPath = `inset(0 0 0 ${split * 100}%)`;
	}, [split, s.compare]);

	async function onClick(m: MLMap, lon: number, lat: number, point: maplibregl.Point) {
		const feats = m.getLayer('patches-fill') && m.getLayoutProperty('patches-fill', 'visibility') === 'visible'
			? m.queryRenderedFeatures(point, { layers: ['patches-fill'] }) : [];
		const patch = feats[0]?.properties;
		setInfo({ loading: true, patch });
		try {
			const r = await fetch(`/api/pixel?lat=${lat.toFixed(6)}&lon=${lon.toFixed(6)}`);
			if (!r.ok) throw new Error(String(r.status));
			setInfo({ px: await r.json(), patch });
		} catch (e) {
			setInfo({ err: t.pixelError, patch });
		}
	}

	function flyTo(v: View) {
		const { center, zoom, ...rest } = PRESETS[v];
		setS({ ...DEFAULT, ...rest });
		setView(v);
		const m = map.current;
		if (!m || !meta) return;
		if (center) m.flyTo({ center, zoom: zoom ?? 12 });
		else m.fitBounds([[meta.bounds[0], meta.bounds[1]], [meta.bounds[2], meta.bounds[3]]], { padding: 30 });
	}

	function ask(text: string) {
		window.dispatchEvent(new CustomEvent('dwts:ask', { detail: { text } }));
	}

	const startDrag = (e: React.PointerEvent) => {
		const box = el.current!.getBoundingClientRect();
		const move = (ev: PointerEvent) => setSplit(Math.min(0.97, Math.max(0.03, (ev.clientX - box.left) / box.width)));
		const up = () => { window.removeEventListener('pointermove', move); window.removeEventListener('pointerup', up); };
		window.addEventListener('pointermove', move); window.addEventListener('pointerup', up);
		e.preventDefault();
	};

	const L = (o: { en: string; vi: string }) => o[lang];
	const opacityCtl = (
		<label className="dwts-range">{t.opacity}
			<input type="range" min={0.2} max={1} step={0.05} value={s.opacity} onChange={(e) => set({ opacity: +e.target.value })} />
		</label>
	);
	const sw = (c: string | null) => <span className="dwts-sw" style={{ background: c ?? 'transparent' }} />;
	const fmt = (v: number | null | undefined) => (v == null ? '–' : v.toFixed(1));

	return (
		<div className="dwts-map not-content">
			<div ref={el} className="dwts-map-canvas" />
			{s.compare && (
				<>
					<div ref={el2} className="dwts-map-canvas dwts-map-overlay" />
					<div className="dwts-swipe" style={{ left: `${split * 100}%` }} onPointerDown={startDrag}>
						<span className="dwts-swipe-handle">⇔</span>
					</div>
					<div className="dwts-swipe-label left" style={{ right: `calc(${(1 - split) * 100}% + 10px)` }}>{ddmm(s.left)}</div>
					<div className="dwts-swipe-label right" style={{ left: `calc(${split * 100}% + 10px)` }}>{ddmm(s.right)}</div>
				</>
			)}
			{!meta && <div className="dwts-map-loading">{t.loading}</div>}

			{panelOpen ? (
				<aside className="dwts-panel" aria-label={t.panelTitle}>
					<div className="dwts-panel-head">
						<strong>{t.panelTitle}</strong>
						<button className="dwts-icon-btn" onClick={() => setPanelOpen(false)} aria-label={t.collapse} title={t.collapse}>✕</button>
					</div>
					<div className="dwts-panel-body">
						<h2>{t.stories}</h2>
						<div className="dwts-presets">
							{VIEWS.map((v) => (
								<button key={v} className={view === v ? 'on' : ''} aria-pressed={view === v} onClick={() => flyTo(v)}>{t.preset[v]}</button>
							))}
						</div>

						<h2>{t.baseTitle}</h2>
						{s.compare ? (
							<div className="dwts-compare">
								<div className="dwts-row">
									<label>{t.compareLeft}
										<select value={s.left} onChange={(e) => set({ left: e.target.value as DateKey })}>{DATES.map((d) => <option key={d} value={d}>{ddmm(d)}</option>)}</select>
									</label>
									<span aria-hidden>⇔</span>
									<label>{t.compareRight}
										<select value={s.right} onChange={(e) => set({ right: e.target.value as DateKey })}>{DATES.map((d) => <option key={d} value={d}>{ddmm(d)}</option>)}</select>
									</label>
								</div>
								<p className="dwts-hint">{t.compareNote}</p>
								<button className="dwts-btn" onClick={() => set({ compare: false })}>✕ {t.exitCompare}</button>
							</div>
						) : (
							<div role="radiogroup" aria-label={t.baseTitle}>
								<Opt name="base" on={s.base === null} onPick={() => setBase(null)} label={t.baseNone} />
								{DATES.map((d) => (
									<Opt key={d} name="base" on={s.base === d} onPick={() => setBase(d)} label={t.sarDate(ddmm(d))} note={t.sarPass[d]} />
								))}
								<Opt name="base" on={s.base === 's2'} onPick={() => setBase('s2')} label={t.s2} note={t.s2Note} />
								<button className="dwts-btn" onClick={() => set({ compare: true })}>⇔ {t.compare}</button>
							</div>
						)}
						{meta && (s.compare || (s.base && s.base !== 's2')) && <p className="dwts-hint dwts-inline-legend">{t.sarLegend(meta.sar_stretch_db)}</p>}

						<fieldset disabled={s.compare} className="dwts-fs">
							<h2>{t.themeTitle}</h2>
							<div role="radiogroup" aria-label={t.themeTitle}>
								<Opt name="theme" on={s.theme === null} onPick={() => set({ theme: null })} label={t.themeNone} />
								<Opt name="theme" on={s.theme === 'landcover'} onPick={() => set({ theme: 'landcover' })} label={t.landcover}>
									{meta && (
										<div className="dwts-inline-legend">
											{Object.entries(meta.landcover).map(([k, v]) => <div key={k}>{sw(v.color)}{L(v)} <span className="dwts-dim">{v.pct}%</span></div>)}
											<p className="dwts-hint">{t.lcNote}</p>
										</div>
									)}
									{opacityCtl}
								</Opt>
								<Opt name="theme" on={s.theme === 'agreement'} onPick={() => set({ theme: 'agreement' })} label={t.agreement}>
									{meta && (
										<div className="dwts-inline-legend dwts-ramp">
											{Object.entries(meta.agreement_ramp).filter(([k]) => +k >= 4).map(([k, c]) => <span key={k} style={{ background: c }}>{k}</span>)}
										</div>
									)}
									{opacityCtl}
								</Opt>
							</div>
						</fieldset>

						<h2>{t.overlays}</h2>
						<Chk on={s.change} onToggle={(v) => set({ change: v })} label={t.change}>
							{meta && (
								<div className="dwts-inline-legend">
									{Object.entries(meta.change.classes).filter(([k]) => k !== '1').map(([k, v]) => (
										<div key={k}>{sw(v.color)}{L(v)} <span className="dwts-dim">{v.area_km2} km²</span></div>
									))}
								</div>
							)}
						</Chk>
						<Chk on={s.aoa} disabled={s.compare} onToggle={(v) => set({ aoa: v })} label={t.aoa}>
							{meta && <p className="dwts-hint dwts-inline-legend"><span className="dwts-sw dwts-hatch" />{t.aoaLegend((meta.aoa.outside_fraction * 100).toFixed(1))}</p>}
						</Chk>
						<Chk on={s.labels} onToggle={(v) => set({ labels: v })} label={t.labels} />
						<div className="dwts-aoi-key"><span className="dwts-sw dwts-aoi" />{t.aoi}</div>
						<p className="dwts-hint">{t.clickHint}</p>
					</div>
				</aside>
			) : (
				<button className="dwts-panel-toggle" onClick={() => setPanelOpen(true)} aria-expanded={false}>☰ {t.panelTitle}</button>
			)}

			<button className="dwts-about-fab" onClick={() => setShowIntro(true)} aria-label={t.about}>ⓘ <span>{t.about}</span></button>
			{showIntro && (
				<Intro
					lang={lang}
					onClose={closeIntro}
					onView={(v) => { closeIntro(); flyTo(v as View); }}
					onChat={() => { closeIntro(); window.dispatchEvent(new CustomEvent('dwts:open-chat')); }}
				/>
			)}

			{info && (
				<div className="dwts-info">
					<button className="dwts-close" onClick={() => setInfo(null)} aria-label="close">✕</button>
					{info.patch && (
						<div className="dwts-patch">
							<h3>{t.patch} #{info.patch.id}</h3>
							<p><span className="dwts-sw" style={{ background: info.patch.color }} />{lang === 'vi' ? info.patch.name_vi : info.patch.name_en}</p>
							<p>{t.area}: <b>{info.patch.area_km2} km²</b></p>
							<SeriesTable lang={lang} hh={DATES.map((d) => info.patch![`HH_${d}`])} hv={DATES.map((d) => info.patch![`HV_${d}`])} />
						</div>
					)}
					{info.loading && <p>{t.loading}</p>}
					{info.err && <p>{info.err}</p>}
					{info.px && !info.px.inside && <p>{t.outside}</p>}
					{info.px?.inside && (
						<div>
							<h3>{t.point} {info.px.lat.toFixed(4)}°N, {info.px.lon.toFixed(4)}°E</h3>
							<table className="dwts-kv"><tbody>
								<tr><th>{t.landcover}</th><td>{info.px.landcover ? L(info.px.landcover) : '–'}</td></tr>
								<tr><th>{t.agreementShort}</th><td>{info.px.agreement ?? '–'}/10</td></tr>
								<tr><th>{t.aoaShort}</th><td>{info.px.inside_aoa ? t.yes : t.noOut} (DI {info.px.aoa_di?.toFixed(3)})</td></tr>
								<tr><th>{t.changeShort}</th><td>{info.px.change ? L(info.px.change) : '–'}</td></tr>
							</tbody></table>
							<SeriesTable lang={lang} hh={DATES.map((d) => info.px!.hh_db?.[d] ?? null)} hv={DATES.map((d) => info.px!.hv_db?.[d] ?? null)} />
							<button className="dwts-ask" onClick={() => ask(t.askPoint(info.px!.lat, info.px!.lon))}>💬 {t.askAI}</button>
						</div>
					)}
				</div>
			)}
		</div>
	);

	function SeriesTable({ hh, hv }: { lang: Lang; hh: (number | null)[]; hv: (number | null)[] }) {
		return (
			<table className="dwts-series"><thead><tr><th>dB</th>{DATES.map((d) => <th key={d}>{ddmm(d)}</th>)}</tr></thead>
				<tbody>
					<tr><th>HH</th>{hh.map((v, i) => <td key={i}>{fmt(v)}</td>)}</tr>
					<tr><th>HV</th>{hv.map((v, i) => <td key={i}>{fmt(v)}</td>)}</tr>
				</tbody></table>
		);
	}
}

// One radio row; its legend (children) shows only while it is selected.
function Opt({ name, on, onPick, label, note, children }: { name: string; on: boolean; onPick: () => void; label: string; note?: string; children?: React.ReactNode }) {
	return (
		<div className={'dwts-opt' + (on ? ' on' : '')}>
			<label>
				<input type="radio" name={name} checked={on} onChange={onPick} />
				<span>{label}{note && <small> · {note}</small>}</span>
			</label>
			{on && children}
		</div>
	);
}

function Chk({ on, onToggle, label, disabled, children }: { on: boolean; onToggle: (v: boolean) => void; label: string; disabled?: boolean; children?: React.ReactNode }) {
	return (
		<div className={'dwts-opt' + (on && !disabled ? ' on' : '') + (disabled ? ' off' : '')}>
			<label>
				<input type="checkbox" checked={on} disabled={disabled} onChange={(e) => onToggle(e.target.checked)} />
				<span>{label}</span>
			</label>
			{on && !disabled && children}
		</div>
	);
}
