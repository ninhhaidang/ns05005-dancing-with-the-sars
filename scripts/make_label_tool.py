"""Tạo công cụ chấm nhãn cục bộ với nhãn gợi ý từ Sentinel-2 + SAR.

Vòng 1 (mặc định):  python -I scripts/make_label_tool.py
Vòng 2 (mù, nhiều thực vật, zoom hẹp):  python -I scripts/make_label_tool.py --round 2

Mỗi mẫu = pixel 20 m, hiển thị 3 ảnh: S2 màu thật, S2 màu giả (NIR-R-G), SAR (HH,HV,HH-HV).
Nhãn gợi ý là quy tắc ngưỡng thô, KHÔNG phải nhãn đúng; vòng 2 ẩn gợi ý để nhãn độc lập.
"""
import argparse, base64, csv, glob, io, json
from pathlib import Path
import numpy as np, rasterio
from PIL import Image
from pyproj import Transformer
from rasterio.warp import reproject, Resampling
from scipy import ndimage as ndi

ap = argparse.ArgumentParser(); ap.add_argument("--round", type=int, default=1); A = ap.parse_args()
R2 = A.round == 2
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "labeling"; OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(42 if not R2 else 7)
CLASSES = {1: "Nước", 2: "Thực vật (ruộng/cây trồng xanh, cây thân gỗ, vườn)",
           3: "Đất trống (ruộng đã gặt, đất trống nông nghiệp, bãi bồi)", 4: "Làng / đô thị"}
MIN_SEP = 25
HALF = 12 if R2 else 20          # vòng 2: cửa sổ 25x25 px (~500 m), zoom to hơn
SCALE = 16 if R2 else 5          # hệ số phóng ảnh PNG
BLIND = R2                       # vòng 2 ẩn nhãn gợi ý
# vòng 1: mỗi lớp 75. Vòng 2: (nhóm, số mẫu); 'band' = NDVI 0,3-0,5 (quy tắc cho là đất trống, nghi là thực vật)
QUOTA = {1: 75, 2: 75, 3: 75, 4: 75}
Q2 = [("veg", 35), ("band", 45), ("bare", 25), ("water", 15), ("urban", 20)]

ref = rasterio.open(glob.glob(str(ROOT / "data/nisar/gcov/*20261022T*frequencyA__HHHH.tif"))[0])
aoi = np.isfinite(ref.read(1))
def sar(d, p):
    s = rasterio.open(glob.glob(str(ROOT / f"data/nisar/gcov/*_{d}T*__frequencyA__{p}.tif"))[0])
    if s.res == ref.res: return s.read(1)
    o = np.full(ref.shape, np.nan, np.float32)
    reproject(s.read(1), o, src_transform=s.transform, src_crs=s.crs, dst_transform=ref.transform, dst_crs=ref.crs,
              resampling=Resampling.average, src_nodata=np.nan, dst_nodata=np.nan)
    return o
D = ["20261022", "20261027", "20261103"]
hh = ndi.uniform_filter(np.nan_to_num(10 * np.log10(np.nanmean([sar(d, "HHHH") for d in D], 0)), nan=-30), 3)
hv = ndi.uniform_filter(np.nan_to_num(10 * np.log10(np.nanmean([sar(d, "HVHV") for d in D], 0)), nan=-40), 3)

c = rasterio.open(ROOT / "data/s2/composite_20m.tif").read().astype(np.float32)
valid = aoi & (c[5] > 0)
B, G, R, N, S = [np.maximum(c[i] / 1e4, 0.005) for i in range(5)]  # phản xạ = DN*1e-4 (offset đã áp), sàn 0,005
ndvi = (N - R) / (N + R); mndwi = (G - S) / (G + S); ndbi = (S - N) / (S + N)

lab = np.zeros(ref.shape, np.uint8)
water = (mndwi > 0.1) & (ndvi < 0.2)
urban = (ndvi < 0.35) & (ndbi > 0) & (hh > -4) & ~water
bare = (ndvi < 0.2) & (hh < -9) & ~water & ~urban
harv = (ndvi >= 0.15) & (ndvi < 0.5) & ~water & ~urban & ~bare
woody = (ndvi >= 0.65) & (hv >= -12.5) & ~water & ~urban
green = (ndvi >= 0.5) & ~woody & ~water & ~urban
for k, m in [(2, green | woody), (3, harv | bare), (4, urban), (1, water)]: lab[m] = k
near = np.zeros(ref.shape, bool)
for th in (0.2, 0.35, 0.5): near |= np.abs(ndvi - th) < 0.05
lowconf = near

ok = ndi.binary_erosion(valid, np.ones((5, 5), bool)) & ndi.binary_erosion(aoi, np.ones((HALF * 2 + 1,) * 2, bool))
ok[:HALF] = ok[-HALF:] = False; ok[:, :HALF] = ok[:, -HALF:] = False
sd = np.sqrt(np.maximum(ndi.uniform_filter(ndvi ** 2, 3) - ndi.uniform_filter(ndvi, 3) ** 2, 0))
print("pixel hợp lệ %.1f%% AOI" % (valid.sum() / aoi.sum() * 100))

taken = np.zeros(ref.shape, bool)
if R2:  # tránh trùng vùng với vòng 1
    for r_ in csv.DictReader(open(OUT / "samples_suggested.csv")): taken[int(r_["row"]), int(r_["col"])] = True
def pick(mask, n):
    cand = np.argwhere(ok & mask)
    if len(cand) == 0: return []
    cand = cand[sd[cand[:, 0], cand[:, 1]] <= np.percentile(sd[cand[:, 0], cand[:, 1]], 70)]
    rng.shuffle(cand); out = []
    for r, cc in cand:
        if taken[max(0, r - MIN_SEP):r + MIN_SEP, max(0, cc - MIN_SEP):cc + MIN_SEP].any(): continue
        taken[r, cc] = True; out.append((int(r), int(cc)))
        if len(out) >= n: break
    return out
samples = []
if not R2:
    for k, n in QUOTA.items():
        got = pick(lab == k, n); print(f"  mẫu lớp {k}: {len(got)}"); samples += [(r, cc, k) for r, cc in got]
else:
    strata = {"veg": lab == 2, "band": (ndvi >= 0.3) & (ndvi < 0.5) & (lab == 3), "bare": (lab == 3) & (ndvi < 0.3),
              "water": lab == 1, "urban": lab == 4}
    for name, n in Q2:
        got = pick(strata[name], n); print(f"  nhóm {name}: {len(got)}"); samples += [(r, cc, int(lab[r, cc])) for r, cc in got]
rng.shuffle(samples)

def png(a):
    im = Image.fromarray(a).resize((a.shape[1] * SCALE, a.shape[0] * SCALE), Image.NEAREST); b = io.BytesIO(); im.save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
def stretch(x, lo, hi, g=0.8): return (np.clip((x - lo) / (hi - lo), 0, 1) ** g * 255).astype(np.uint8)
tr = Transformer.from_crs(32648, 4326, always_xy=True); items = []
for i, (r, cc, k) in enumerate(samples):
    s = (slice(r - HALF, r + HALF + 1), slice(cc - HALF, cc + HALF + 1)); v = valid[s]
    def rgb(chs, rng_):
        a = np.dstack([stretch(ch[s], *rg) for ch, rg in zip(chs, rng_)]); a[~v] = 255; return a
    tc = rgb([R, G, B], [(0, .15)] * 3); fc = rgb([N, R, G], [(0.05, .5), (0, .15), (0, .15)])
    sr = np.dstack([stretch(hh[s], -20, 2, 1), stretch(hv[s], -28, -6, 1), stretch(hh[s] - hv[s], 3, 14, 1)])
    x, y = ref.xy(r, cc); lon, lat = tr.transform(x, y)
    items.append(dict(id=i, row=r, col=cc, lon=round(lon, 5), lat=round(lat, 5), sug=int(k), low=bool(lowconf[r, cc]),
                      ndvi=round(float(ndvi[r, cc]), 2), mndwi=round(float(mndwi[r, cc]), 2), hh=round(float(hh[r, cc]), 1),
                      hv=round(float(hv[r, cc]), 1), imgs=[png(tc), png(fc), png(sr)]))
suffix = "r2" if R2 else None
csv_name = f"samples_{suffix}_suggested.csv" if R2 else "samples_suggested.csv"
html_name = f"label_tool_{suffix}.html" if R2 else "label_tool.html"
with open(OUT / csv_name, "w") as f:
    f.write("id,row,col,lon,lat,suggested,low_confidence\n")
    for it in items: f.write(f"{it['id']},{it['row']},{it['col']},{it['lon']},{it['lat']},{it['sug']},{int(it['low'])}\n")

HTML = """<!doctype html><html lang="vi"><meta charset="utf-8"><title>Chấm nhãn __T__</title>
<style>body{font:16px system-ui;margin:14px 20px}.row{display:flex;gap:10px;flex-wrap:nowrap}
.w{position:relative;flex:1 1 0;min-width:0}.w img{display:block;width:100%;aspect-ratio:1;image-rendering:pixelated;border:1px solid #888}
.box{position:relative}.w i{position:absolute;left:50%;top:50%;width:9px;height:9px;margin:-6px 0 0 -6px;border:2px solid #f0f;border-radius:50%;pointer-events:none;box-shadow:0 0 0 1px #fff}
button{font-size:16px;padding:7px 12px;margin:3px}.on{background:#2563eb;color:#fff}.s{outline:2px dashed #16a34a}#info,.hint{color:#444}.cap{font-size:14px;color:#333}</style>
<h3>Chấm nhãn lớp phủ — __T__</h3><div id="top"></div><div class="row" id="imgs"></div><p id="info"></p><div id="btns"></div>
<p class="hint">Phím: 1-4 chọn lớp · 0 bỏ qua · ←/→ chuyển mẫu__H__ · chấm hồng = pixel cần gán nhãn (ảnh trắng = chưa có dữ liệu).</p>
<button onclick="exp()">Tải CSV nhãn</button> <button onclick="nextUn()">Tới mẫu chưa chấm</button>
<script>
const C=__C__, S=__S__, BLIND=__B__, KEY='labels___R__'; let i=0, L=JSON.parse(localStorage.getItem(KEY)||'{}');
const names=["Ảnh màu thật","Màu giả (NIR-R-G): thực vật đỏ","SAR (R=HH, G=HV, B=HH-HV)"];
function show(){const s=S[i];document.getElementById('top').innerHTML=`Mẫu ${i+1}/${S.length} · đã chấm ${Object.keys(L).length} · `+(L[s.id]!==undefined?`<b>nhãn: ${L[s.id]==0?'bỏ qua':C[L[s.id]]}</b>`:'chưa chấm');
document.getElementById('imgs').innerHTML=s.imgs.map((m,k)=>`<div class="w"><div class="cap">${names[k]}</div><div class="box"><img src="${m}"><i></i></div></div>`).join('');
document.getElementById('info').innerHTML=(BLIND?'':`Gợi ý: <b>${C[s.sug]}</b>${s.low?' (độ tin cậy thấp)':''} · NDVI ${s.ndvi} · MNDWI ${s.mndwi} · HH ${s.hh} dB · HV ${s.hv} dB · `)+`${s.lat}, ${s.lon}`;
document.getElementById('btns').innerHTML=Object.keys(C).map(k=>`<button class="${L[s.id]==k?'on':''} ${(!BLIND&&s.sug==k)?'s':''}" onclick="set(${k})">${k}. ${C[k]}</button>`).join('')+`<button class="${L[s.id]===0?'on':''}" onclick="set(0)">0. Bỏ qua</button>`}
function set(k){L[S[i].id]=k;localStorage.setItem(KEY,JSON.stringify(L));if(i<S.length-1)i++;show()}
function nextUn(){for(let j=1;j<=S.length;j++){const t=(i+j)%S.length;if(L[S[t].id]===undefined){i=t;break}}show()}
function exp(){let t='id,row,col,lon,lat,suggested,label,corrected\\n';S.forEach(s=>{if(L[s.id]!==undefined&&L[s.id]!=0)t+=`${s.id},${s.row},${s.col},${s.lon},${s.lat},${s.sug},${L[s.id]},${L[s.id]!=s.sug?1:0}\\n`});
const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([t],{type:'text/csv'}));a.download='labels___R__.csv';a.click()}
document.onkeydown=e=>{if(e.key>='0'&&e.key<='4')set(+e.key);else if(e.key==' '&&!BLIND){e.preventDefault();set(S[i].sug)}else if(e.key=='ArrowRight'&&i<S.length-1){i++;show()}else if(e.key=='ArrowLeft'&&i>0){i--;show()}};
show();
</script></html>"""
html = (HTML.replace("__C__", json.dumps({str(k): v for k, v in CLASSES.items()}, ensure_ascii=False))
        .replace("__S__", json.dumps(items)).replace("__B__", "true" if BLIND else "false")
        .replace("__R__", "r2" if R2 else "r1").replace("__T__", "vòng 2 (mù)" if R2 else "vòng 1")
        .replace("__H__", "" if BLIND else " · Space chấp nhận gợi ý"))
(OUT / html_name).write_text(html, encoding="utf-8")
print(f"{len(items)} mẫu -> labeling/{html_name} ({(OUT/html_name).stat().st_size/1e6:.1f} MB)")
