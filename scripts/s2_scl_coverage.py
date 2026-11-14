"""Độ phủ pixel không mây của Sentinel-2 L2A trên AOI (lưới SAR 20 m), từ lớp SCL, 22/10-3/11/2026."""
import glob, json, collections
from pathlib import Path
import numpy as np, rasterio, requests
from rasterio.warp import reproject, Resampling

ROOT = Path(__file__).resolve().parent.parent
ref = rasterio.open(glob.glob(str(ROOT / "data/nisar/gcov/*20261022T*frequencyA__HHHH.tif"))[0])
aoi = np.isfinite(ref.read(1))
CLEAR = [4, 5, 6]  # thực vật, đất trống, nước
r = requests.post("https://earth-search.aws.element84.com/v1/search", json={
    "collections": ["sentinel-2-l2a"], "bbox": [105.8935, 20.249, 106.6595, 21.007],
    "datetime": "2026-10-22T00:00:00Z/2026-11-03T23:59:59Z", "limit": 100}, timeout=60).json()
by = collections.defaultdict(list)
for f in r["features"]: by[f["properties"]["datetime"][:10]].append(f)
res = {}
for d in sorted(by):
    scl = np.zeros(ref.shape, np.uint8); has = np.zeros(ref.shape, bool)
    for f in by[d]:
        with rasterio.open(f["assets"]["scl"]["href"]) as s:
            out = np.zeros(ref.shape, np.uint8)
            reproject(rasterio.band(s, 1), out, dst_transform=ref.transform, dst_crs=ref.crs, resampling=Resampling.nearest)
        take = (out != 0) & ~has; scl[take] = out[take]; has |= take
    clear = np.isin(scl, CLEAR)
    res[d] = clear
    rasterio.open(ROOT / f"data/s2/scl_{d}.tif", "w", driver="GTiff", height=ref.height, width=ref.width, count=1, dtype="uint8",
                  crs=ref.crs, transform=ref.transform, nodata=0, compress="deflate").write(scl, 1)
    print(d, f"{len(by[d])} cảnh | có dữ liệu {has[aoi].mean()*100:.0f}% | không mây {clear[aoi].mean()*100:.0f}% AOI", flush=True)
allc = np.stack(list(res.values())); n = allc.sum(0)
print("Hợp nhất mọi ngày: ít nhất 1 ngày sạch %.0f%% AOI; >=2 ngày %.0f%%" % ((n[aoi] >= 1).mean() * 100, (n[aoi] >= 2).mean() * 100))
ch = rasterio.open(ROOT / "data/derived/change_class_22oct_3nov.tif").read(1)
for c, nm in [(2, "cụm nước mới"), (3, "giảm khác"), (4, "tăng")]:
    m = ch == c
    print(f"{nm}: " + ", ".join(f"{d[5:]}:{res[d][m].mean()*100:.0f}%" for d in res) + f" | ít nhất 1 ngày sạch {(n[m]>=1).mean()*100:.0f}%")
