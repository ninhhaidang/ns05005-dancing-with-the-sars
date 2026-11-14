"""Tải mọi cảnh Sentinel-2 L2A trong 22/10-3/11/2026, cắt theo khung bao AOI, giữ độ phân giải gốc.

Ra: data/s2/raw/<ngày>/<id cảnh>/<băng>.tif  (+ item.json) và data/s2/raw/index.csv. Chạy lại được (bỏ qua file đã có).
Băng: visual (TCI 8-bit, 10 m), blue/green/red/nir (10 m), swir16 (20 m), scl (20 m).
Phản xạ = DN * 1e-4 (Earth Search đã áp BOA offset; KHÔNG trừ thêm 0,1).
"""
import os, glob, json, shutil, csv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
os.environ.update(GDAL_HTTP_MULTIPLEX="YES", GDAL_HTTP_VERSION="2", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                  CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif", VSI_CACHE="TRUE", GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES",
                  GDAL_HTTP_TIMEOUT="120")
import numpy as np, rasterio, requests
from rasterio.windows import from_bounds, Window

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/s2/raw"; RAW.mkdir(parents=True, exist_ok=True)
ASSETS = ["visual", "blue", "green", "red", "nir", "swir16", "scl"]
ref = rasterio.open(glob.glob(str(ROOT / "data/nisar/gcov/*20261022T*frequencyA__HHHH.tif"))[0])
M = 200
BOX = (ref.bounds.left - M, ref.bounds.bottom - M, ref.bounds.right + M, ref.bounds.top + M)  # UTM 48N

r = requests.post("https://earth-search.aws.element84.com/v1/search", json={
    "collections": ["sentinel-2-l2a"], "bbox": [105.8935, 20.249, 106.6595, 21.007],
    "datetime": "2026-10-22T00:00:00Z/2026-11-03T23:59:59Z", "limit": 100}, timeout=60).json()
items = sorted(r["features"], key=lambda f: (f["properties"]["datetime"], f["id"]))
tasks = [(f, a) for f in items for a in ASSETS]

def window(src):
    w = from_bounds(*BOX, src.transform).round_offsets().round_lengths()
    try: return w.intersection(Window(0, 0, src.width, src.height))
    except Exception: return None

def one(t):
    f, a = t; d = f["properties"]["datetime"][:10]
    out = RAW / d / f["id"] / f"{a}.tif"
    if out.exists(): return out, 0, "có sẵn"
    try:
        with rasterio.open(f["assets"][a]["href"]) as s:
            w = window(s)
            if w is None or w.width < 2 or w.height < 2: return out, 0, "ngoài AOI"
            data = s.read(window=w)
            if not data.any(): return out, 0, "toàn nodata"
            out.parent.mkdir(parents=True, exist_ok=True); tmp = out.with_suffix(".part")
            prof = dict(driver="GTiff", height=data.shape[1], width=data.shape[2], count=data.shape[0], dtype=data.dtype,
                        crs=s.crs, transform=s.window_transform(w), nodata=0, compress="deflate", tiled=True,
                        predictor=2 if data.dtype.kind in "ui" else 3, blockxsize=512, blockysize=512)
            with rasterio.open(tmp, "w", **prof) as o:
                o.write(data); o.update_tags(item=f["id"], datetime=f["properties"]["datetime"],
                                             cloud_cover=str(f["properties"].get("eo:cloud_cover")), asset=a)
            tmp.rename(out); return out, out.stat().st_size, "ok"
    except Exception as e:
        return out, 0, f"LỖI {type(e).__name__}: {str(e)[:80]}"

free = shutil.disk_usage(ROOT).free / 1e9
print(f"{len(items)} cảnh x {len(ASSETS)} băng = {len(tasks)} file; ổ còn trống {free:.0f} GB", flush=True)
for f in items: (RAW / f["properties"]["datetime"][:10] / f["id"]).mkdir(parents=True, exist_ok=True); \
    json.dump(f, open(RAW / f["properties"]["datetime"][:10] / f["id"] / "item.json", "w"))
tot = 0
with ThreadPoolExecutor(6) as ex:
    for i, (out, sz, st) in enumerate(ex.map(one, tasks), 1):
        tot += sz
        if st != "ok" and st != "có sẵn" and not st.startswith("ngoài") and not st.startswith("toàn"): print("  ", out.parent.name, out.name, st, flush=True)
        if i % 10 == 0 or i == len(tasks): print(f"[{i}/{len(tasks)}] đã ghi {tot/1e9:.2f} GB", flush=True)

with open(RAW / "index.csv", "w") as fh:
    w = csv.writer(fh); w.writerow(["date", "item", "cloud_cover", "files"])
    for f in items:
        d = f["properties"]["datetime"][:10]; fs = sorted(p.stem for p in (RAW / d / f["id"]).glob("*.tif"))
        w.writerow([d, f["id"], f["properties"].get("eo:cloud_cover"), " ".join(fs)])
print(f"xong: {sum(p.stat().st_size for p in RAW.rglob('*.tif'))/1e9:.2f} GB trong {RAW}")
