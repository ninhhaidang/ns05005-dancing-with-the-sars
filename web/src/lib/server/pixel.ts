// Point lookup in data/web/pixel_stack.tif (20 m, EPSG:32648, int16, nodata -32768).
import { fromFile, type GeoTIFFImage } from 'geotiff';
import proj4 from 'proj4';
import { join } from 'node:path';
import { config } from './config';

const UTM48 = '+proj=utm +zone=48 +datum=WGS84 +units=m +no_defs';
export const DATES = ['2026-10-22', '2026-10-27', '2026-11-03'];
export const LANDCOVER: Record<number, { en: string; vi: string }> = {
	1: { en: 'Water', vi: 'Nước' },
	2: { en: 'Vegetation', vi: 'Thực vật' },
	3: { en: 'Bare soil', vi: 'Đất trống' },
	4: { en: 'Built-up (urban/village)', vi: 'Đô thị/làng' },
};
export const CHANGE: Record<number, { en: string; vi: string }> = {
	1: { en: 'No significant change', vi: 'Không đổi đáng kể' },
	2: { en: 'New water / flattening (HH & HV decrease, HH ends below −15 dB)', vi: 'Nước mới / mặt phẳng hóa (HH, HV giảm, HH cuối < −15 dB)' },
	3: { en: 'HH & HV decrease (other)', vi: 'HH, HV giảm (khác)' },
	4: { en: 'HH & HV increase', vi: 'HH, HV tăng' },
	5: { en: 'HV-only decrease', vi: 'Chỉ HV giảm' },
	6: { en: 'HV-only increase', vi: 'Chỉ HV tăng' },
};
const AOA_THRESHOLD = 0.1051;

let img: Promise<{ image: GeoTIFFImage; names: string[] }> | null = null;
function open() {
	img ??= (async () => {
		const tiff = await fromFile(join(config.dataDir, 'pixel_stack.tif'));
		const image = await tiff.getImage();
		const names = ['landcover', 'landcover_raw', 'model_mode', 'agreement', 'change', 'aoa_di_x1000',
			...DATES.map((d) => `HH_${d}`), ...DATES.map((d) => `HV_${d}`)];
		return { image, names };
	})();
	img.catch(() => { img = null; });
	return img;
}

export interface PixelResult {
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
	note?: string;
}

export async function samplePixel(lat: number, lon: number): Promise<PixelResult> {
	const { image } = await open();
	const [x, y] = proj4('EPSG:4326', UTM48, [lon, lat]);
	const [ox, oy] = image.getOrigin();
	const [rx, ry] = image.getResolution();
	const col = Math.floor((x - ox) / rx), row = Math.floor((y - oy) / ry);
	const base = { lat, lon };
	if (col < 0 || row < 0 || col >= image.getWidth() || row >= image.getHeight()) return { ...base, inside: false };
	const r = (await image.readRasters({ window: [col, row, col + 1, row + 1], interleave: true })) as unknown as ArrayLike<number>;
	const v = Array.from(r);
	if (v[0] === -32768 || v[0] === 0) return { ...base, inside: false };
	const db = (i: number) => (v[i] === -32768 ? null : Math.round(v[i]) / 100);
	const di = v[5] === -32768 ? undefined : v[5] / 1000;
	return {
		...base,
		inside: true,
		landcover: { code: v[0], ...LANDCOVER[v[0]] },
		landcover_raw: v[1],
		agreement: v[3],
		aoa_di: di,
		inside_aoa: di !== undefined ? di <= AOA_THRESHOLD : undefined,
		change: v[4] > 0 ? { code: v[4], ...CHANGE[v[4]] } : undefined,
		hh_db: Object.fromEntries(DATES.map((d, i) => [d, db(6 + i)])),
		hv_db: Object.fromEntries(DATES.map((d, i) => [d, db(9 + i)])),
		note: 'Values for the 20 m grid cell containing the point. dB values are 3x3-smoothed model features; landcover is the 3x3 majority-filtered SAR-only Random Forest map; agreement = number of 10 models predicting the same class.',
	};
}
