"""Tạo công cụ chấm nhãn cục bộ (labeling/label_tool.html) với nhãn gợi ý từ Sentinel-2 + SAR.

Mỗi mẫu = pixel 20 m, hiển thị cửa sổ 41x41 px (~820 m) ở 3 ảnh: S2 màu thật, S2 màu giả (NIR-R-G), SAR (HH,HV,HH-HV).
Nhãn gợi ý là quy tắc ngưỡng thô, chỉ để người dùng sửa, KHÔNG phải nhãn đúng.
"""
import base64, glob, io, json
from pathlib import Path
import numpy as np, rasterio
from PIL import Image
from pyproj import Transformer
from rasterio.warp import reproject, Resampling
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "labeling"; OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(42)
CLASSES = {1: "Nước", 2: "Thực vật (ruộng/cây trồng xanh, cây thân gỗ, vườn)",
           3: "Đất trống (ruộng đã gặt, đất trống nông nghiệp, bãi bồi)", 4: "Làng / đô thị"}
PER_CLASS, MIN_SEP, HALF = 75, 25, 20

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
B, G, R, N, S = [np.maximum(c[i] / 1e4, 0.005) for i in range(5)]  # sàn 0,005 để chỉ số ổn định
ndvi = (N - R) / (N + R); ndwi = (G - N) / (G + N); mndwi = (G - S) / (G + S); ndbi = (S - N) / (S + N)

lab = np.zeros(ref.shape, np.uint8)
water = (mndwi > 0.1) & (ndvi < 0.2)
urban = (ndvi < 0.35) & (ndbi > 0) & (hh > -4) & ~water
bare = (ndvi < 0.2) & (hh < -9) & ~water & ~urban
harv = (ndvi >= 0.15) & (ndvi < 0.5) & ~water & ~urban & ~bare
woody = (ndvi >= 0.65) & (hv >= -12.5) & ~water & ~urban
green = (ndvi >= 0.5) & ~woody & ~water & ~urban
for k, m in [(2, green | woody), (3, harv | bare), (4, urban), (1, water)]: lab[m] = k
near = np.zeros(ref.shape, bool)
for th in (0.2, 0.35, 0.5): near |= np.abs(ndvi - th) < 0.05  # gần ngưỡng giữa thực vật và đất trống / đô thị
lowconf = near

ok5 = ndi.binary_erosion(valid, np.ones((5, 5), bool)) & ndi.binary_erosion(aoi, np.ones((HALF * 2 + 1,) * 2, bool))
ok5[:HALF] = ok5[-HALF:] = False; ok5[:, :HALF] = ok5[:, -HALF:] = False
sd = np.sqrt(np.maximum(ndi.uniform_filter(ndvi ** 2, 3) - ndi.uniform_filter(ndvi, 3) ** 2, 0))
print("pixel hợp lệ %.1f%% AOI" % (valid.sum() / aoi.sum() * 100))
for k, nm in CLASSES.items(): print(f"  gợi ý lớp {k} {nm}: {((lab==k)&valid).sum()*400/1e6:.0f} km2")

samples, taken = [], np.zeros(ref.shape, bool)
tr = Transformer.from_crs(32648, 4326, always_xy=True)
for k in CLASSES:
    cand = np.argwhere(ok5 & (lab == k))
    if len(cand) == 0: continue
    cand = cand[sd[cand[:, 0], cand[:, 1]] <= np.percentile(sd[cand[:, 0], cand[:, 1]], 60)]  # ít lẫn pixel
    rng.shuffle(cand); n = 0
    for r, cc in cand:
        if taken[max(0, r - MIN_SEP):r + MIN_SEP, max(0, cc - MIN_SEP):cc + MIN_SEP].any(): continue
        taken[r, cc] = True; n += 1; samples.append((int(r), int(cc), k))
        if n >= PER_CLASS: break
    print(f"  mẫu lớp {k}: {n}")
rng.shuffle(samples)

def png(a):
    im = Image.fromarray(a).resize((a.shape[1] * 5, a.shape[0] * 5), Image.NEAREST); b = io.BytesIO(); im.save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
def stretch(x, lo, hi, g=0.8): return (np.clip((x - lo) / (hi - lo), 0, 1) ** g * 255).astype(np.uint8)
items = []
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
with open(OUT / "samples_suggested.csv", "w") as f:
    f.write("id,row,col,lon,lat,suggested,low_confidence\n")
    for it in items: f.write(f"{it['id']},{it['row']},{it['col']},{it['lon']},{it['lat']},{it['sug']},{int(it['low'])}\n")

HTML = """<!doctype html><html lang="vi"><meta charset="utf-8"><title>Chấm nhãn</title>
<style>body{font:15px system-ui;margin:16px;max-width:900px}img{image-rendering:pixelated;width:260px;height:260px;border:1px solid #888}
.w{position:relative;display:inline-block;margin-right:8px}.w b{position:absolute;left:50%;top:50%;width:15px;height:15px;margin:-8px;border:2px solid #f0f;box-sizing:border-box;pointer-events:none}
button{font-size:15px;padding:6px 10px;margin:3px}.on{background:#2563eb;color:#fff}.s{outline:2px dashed #16a34a}
#info{color:#444}</style><h2>Chấm nhãn lớp phủ</h2><div id="top"></div><div id="imgs"></div><p id="info"></p><div id="btns"></div>
<p>Phím: 1-4 chọn lớp · 0 bỏ qua · Space chấp nhận gợi ý · ←/→ chuyển mẫu · ô vuông tím = pixel cần gán nhãn (ảnh trắng = chưa có dữ liệu).</p>
<button onclick="exp()">Tải CSV nhãn</button> <button onclick="nextUn()">Tới mẫu chưa chấm</button>
<script>
const C=__C__, S=__S__; let i=0, L=JSON.parse(localStorage.getItem('labels')||'{}');
const names=["Ảnh màu thật","Màu giả (NIR-R-G): thực vật đỏ","SAR (R=HH, G=HV, B=HH-HV)"];
function show(){const s=S[i];document.getElementById('top').innerHTML=`Mẫu ${i+1}/${S.length} · đã chấm ${Object.keys(L).length} · `+(L[s.id]!==undefined?`<b>nhãn: ${L[s.id]==0?'bỏ qua':C[L[s.id]]}</b>`:'chưa chấm');
document.getElementById('imgs').innerHTML=s.imgs.map((m,k)=>`<div class="w"><div>${names[k]}</div><img src="${m}"><b></b></div>`).join('');
document.getElementById('info').innerHTML=`Gợi ý: <b>${C[s.sug]}</b>${s.low?' (độ tin cậy thấp)':''} · NDVI ${s.ndvi} · MNDWI ${s.mndwi} · HH ${s.hh} dB · HV ${s.hv} dB · ${s.lat}, ${s.lon}`;
document.getElementById('btns').innerHTML=Object.keys(C).map(k=>`<button class="${L[s.id]==k?'on':''} ${s.sug==k?'s':''}" onclick="set(${k})">${k}. ${C[k]}</button>`).join('')+`<button class="${L[s.id]===0?'on':''}" onclick="set(0)">0. Bỏ qua</button>`}
function set(k){L[S[i].id]=k;localStorage.setItem('labels',JSON.stringify(L));if(i<S.length-1)i++;show()}
function nextUn(){for(let j=1;j<=S.length;j++){const t=(i+j)%S.length;if(L[S[t].id]===undefined){i=t;break}}show()}
function exp(){let t='id,row,col,lon,lat,suggested,label,corrected\\n';S.forEach(s=>{if(L[s.id]!==undefined&&L[s.id]!=0)t+=`${s.id},${s.row},${s.col},${s.lon},${s.lat},${s.sug},${L[s.id]},${L[s.id]!=s.sug?1:0}\\n`});
const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([t],{type:'text/csv'}));a.download='labels.csv';a.click()}
document.onkeydown=e=>{if(e.key>='0'&&e.key<='4')set(+e.key);else if(e.key==' '){e.preventDefault();set(S[i].sug)}else if(e.key=='ArrowRight'&&i<S.length-1){i++;show()}else if(e.key=='ArrowLeft'&&i>0){i--;show()}};
show();
</script></html>"""
(OUT / "label_tool.html").write_text(HTML.replace("__C__", json.dumps({str(k): v for k, v in CLASSES.items()}, ensure_ascii=False))
                                    .replace("__S__", json.dumps(items)), encoding="utf-8")
print(f"{len(items)} mẫu -> labeling/label_tool.html ({(OUT/'label_tool.html').stat().st_size/1e6:.1f} MB)")
