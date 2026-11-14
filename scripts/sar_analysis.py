"""Phân tích SAR: hotspot, mảng thay đổi, phân loại lớp phủ thô (3 ngày VALIDATED, lưới 20 m)."""
import glob
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from scipy import ndimage as ndi
from pyproj import Transformer

ROOT = Path(__file__).resolve().parent.parent
def fn(d, p): return glob.glob(str(ROOT / f"data/nisar/gcov/*_{d}T*__frequencyA__{p}.tif"))[0]

ref = rasterio.open(fn("20261022", "HHHH"))
def get(d, p):
    s = rasterio.open(fn(d, p))
    if s.res == ref.res: return s.read(1)
    out = np.full(ref.shape, np.nan, np.float32)
    reproject(s.read(1), out, src_transform=s.transform, src_crs=s.crs, dst_transform=ref.transform,
              dst_crs=ref.crs, resampling=Resampling.average, src_nodata=np.nan, dst_nodata=np.nan)
    return out
D = ["20261022", "20261027", "20261103"]
HH = {d: get(d, "HHHH") for d in D}; HV = {d: get(d, "HVHV") for d in D}
ok = np.isfinite(HH[D[0]]) & np.isfinite(HH[D[1]]) & np.isfinite(HH[D[2]])
db = lambda x: 10 * np.log10(x)
def sm(x, k=7):
    w = ndi.uniform_filter(ok.astype(float), k); return np.where(ok, ndi.uniform_filter(np.where(ok, x, 0), k) / np.maximum(w, 1e-6), np.nan)

# 1. hotspot
dh = db(sm(HH[D[2]]) / sm(HH[D[0]])); dv = db(sm(HV[D[2]]) / sm(HV[D[0]]))
lab, n = ndi.label((dh < -4) & (dv < -4)); sz = ndi.sum(lab > 0, lab, range(1, n + 1)); k = int(np.argmax(sz)) + 1; rg = lab == k
print("HOTSPOT trung bình theo ngày (dB):")
for d in D: print(" ", d, "HH %.1f  HV %.1f" % (db(np.nanmean(HH[d][rg])), db(np.nanmean(HV[d][rg]))))
rr, cc = np.where(rg); r0, r1, c0, c1 = rr.min() - 60, rr.max() + 60, cc.min() - 60, cc.max() + 60
# 2. các mảng thay đổi >0.1 km2
for name, m in [("GIẢM", (dh < -3) & (dv < -3)), ("TĂNG", (dh > 3) & (dv > 3))]:
    l, nn = ndi.label(m); s = ndi.sum(m, l, range(1, nn + 1)) * 400 / 1e6
    big = np.sort(s)[::-1]; print(f"{name} >3dB cả HH,HV: tổng {s.sum():.2f} km2, {int((s > 0.1).sum())} mảng >0.1 km2, lớn nhất {big[:5].round(2)} km2")
# 3. lớp phủ thô từ trung bình 3 ngày (giảm speckle)
mh = db(sm(np.nanmean([HH[d] for d in D], 0), 5)); mv = db(sm(np.nanmean([HV[d] for d in D], 0), 5))
print("phân vị HH dB", np.nanpercentile(mh[ok], [1, 5, 25, 50, 75, 95, 99]).round(1), "HV", np.nanpercentile(mv[ok], [1, 5, 25, 50, 75, 95, 99]).round(1))
cls = np.zeros(ref.shape, np.uint8)  # 0 ngoài AOI
cls[ok] = 3                                   # thực vật/ruộng
cls[ok & (mh < -15)] = 1                      # nước/mặt phẳng
cls[ok & (mh > -3)] = 2                       # đô thị/ vật thể cứng (tán xạ góc)
tot = ok.sum()
for v, nme in [(1, "nước (HH<-15 dB)"), (2, "đô thị (HH>-3 dB)"), (3, "ruộng/thực vật")]:
    print(f"  {nme}: {(cls==v).sum()*400/1e6:.0f} km2 ({(cls==v).sum()/tot*100:.1f}%)")
rvi_like = mv - mh
print("HV-HH trung vị theo lớp ruộng: %.1f dB" % np.nanmedian(rvi_like[cls == 3]))
fig, ax = plt.subplots(1, 3, figsize=(18, 6))
from matplotlib.colors import ListedColormap
ax[0].imshow(np.where(ok, cls, np.nan)[::2, ::2], cmap=ListedColormap(["#2b6cb0", "#e53e3e", "#68a03f"]), vmin=1, vmax=3, interpolation="nearest")
ax[0].set_title("Phân loại thô từ SAR (nước / đô thị / ruộng)"); ax[0].axis("off")
ax[1].imshow(np.where(ok, mh - mv, np.nan)[::2, ::2], cmap="viridis", vmin=3, vmax=12); ax[1].set_title("HH − HV (dB), TB 3 ngày"); ax[1].axis("off")
z = np.hstack([db(sm(HH[d], 3))[r0:r1, c0:c1] for d in D])
ax[2].imshow(z, cmap="gray", vmin=-22, vmax=0); ax[2].set_title("Hotspot HH: 22/10 | 27/10 | 3/11"); ax[2].axis("off")
fig.tight_layout(); fig.savefig(ROOT / "outputs/sar_analysis.png", dpi=75)
