"""Tổ hợp pixel sạch Sentinel-2 L2A trên lưới SAR 20 m (22/10-3/11/2026).

Mỗi pixel lấy từ ngày sạch gần 27/10 nhất (ưu tiên theo |ngày - 27/10|). Băng: blue, green, red, nir, swir16
(phản xạ x10000, uint16) + chỉ số ngày nguồn. Kiểu int16; pixel hợp lệ khi source_date_idx > 0.
"""
import glob, collections, datetime as dt
from pathlib import Path
import os
os.environ.update(GDAL_HTTP_MULTIPLEX="YES", GDAL_HTTP_VERSION="2", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                  CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif", VSI_CACHE="TRUE", GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES",
                  GDAL_HTTP_TIMEOUT="60")
from concurrent.futures import ThreadPoolExecutor
import numpy as np, rasterio, requests
from rasterio.enums import Resampling
from rasterio.windows import from_bounds

ROOT = Path(__file__).resolve().parent.parent
ref = rasterio.open(glob.glob(str(ROOT / "data/nisar/gcov/*20261022T*frequencyA__HHHH.tif"))[0])
aoi = np.isfinite(ref.read(1))
BANDS = ["blue", "green", "red", "nir", "swir16"]
r = requests.post("https://earth-search.aws.element84.com/v1/search", json={
    "collections": ["sentinel-2-l2a"], "bbox": [105.8935, 20.249, 106.6595, 21.007],
    "datetime": "2026-10-22T00:00:00Z/2026-11-03T23:59:59Z", "limit": 100}, timeout=60).json()
by = collections.defaultdict(list)
for f in r["features"]: by[f["properties"]["datetime"][:10]].append(f)
center = dt.date(2026, 10, 27)
dates = sorted(by, key=lambda d: abs((dt.date.fromisoformat(d) - center).days))
print("thứ tự ưu tiên:", dates, flush=True)

def warp(src_path, dtype, resampling):
    """Đọc cửa sổ AOI trực tiếp ở 20 m (dùng overview của COG); tất cả ô cùng UTM 48N."""
    with rasterio.open(src_path) as s:
        assert s.crs == ref.crs
        w = from_bounds(*ref.bounds, s.transform)
        return s.read(1, window=w, out_shape=ref.shape, resampling=resampling, boundless=True, fill_value=0).astype(dtype)

comp = np.zeros((len(BANDS),) + ref.shape, np.int16); src = np.zeros(ref.shape, np.uint8); filled = ~aoi
for k, d in enumerate(dates, 1):
    for f in by[d]:
        scl = warp(f["assets"]["scl"]["href"], np.uint8, Resampling.nearest)
        take = np.isin(scl, [4, 5, 6]) & ~filled
        if not take.any(): continue
        with ThreadPoolExecutor(len(BANDS)) as ex:
            dns = list(ex.map(lambda b: warp(f["assets"][b]["href"], np.uint16, Resampling.average), BANDS))
        for i, b in enumerate(BANDS):
            # Earth Search đã áp BOA offset (earthsearch:boa_offset_applied=True): phản xạ = DN * 1e-4, KHÔNG trừ 0,1
            # (trường raster:bands.offset = -0.1 gây trừ hai lần: thực vật ra phản xạ âm).
            comp[i][take] = np.clip(dns[i][take], 0, 30000).astype(np.int16)
        src[take] = k; filled |= take
        print(f"{d} {f['id'][:25]}: +{take.sum()*400/1e6:.0f} km2, tổng phủ {filled[aoi].mean()*100:.1f}% AOI", flush=True)
prof = dict(driver="GTiff", height=ref.height, width=ref.width, count=len(BANDS) + 1, dtype="int16", crs=ref.crs,
            transform=ref.transform, compress="deflate", predictor=2)
with rasterio.open(ROOT / "data/s2/composite_20m.tif", "w", **prof) as o:
    o.write(np.concatenate([comp, src[None].astype(np.int16)]))
    o.descriptions = tuple(BANDS + ["source_date_idx"])
    o.update_tags(dates=",".join(dates), scale="reflectance*10000")
print("xong. nguồn:", {i + 1: d for i, d in enumerate(dates)})
