"""Kiểm tra ảnh Sentinel-2 10 m tải từ Earth Engine: cấu trúc, độ phủ sạch trong AOI, đối chiếu với composite_20m.tif.

Chạy: /Users/ninhhaidang/miniconda3/envs/dwts/bin/python -I scripts/check_gee_s2.py
"""
import json
from pathlib import Path
import numpy as np, rasterio
from rasterio.features import rasterize
from rasterio.warp import transform_geom, reproject, Resampling

ROOT = Path(__file__).resolve().parent.parent
GEE = ROOT / "data/s2/gee_10m/S2_composite_10m_20261022_20261103.tif"
REF = ROOT / "data/s2/composite_20m.tif"
names = ["B2", "B3", "B4", "B8", "B11", "n_clear"]

with rasterio.open(GEE) as s:
    print("GEE:", s.count, "băng", s.crs, s.res, s.shape, s.dtypes[0], "nodata:", s.nodata)
    print("bounds:", s.bounds, "| descriptions:", s.descriptions, "| tags:", s.tags())
    g = s.read()  # (6, H, W) int16
    gt, gcrs = s.transform, s.crs

# AOI trên lưới GEE 10 m
feats = json.load(open(ROOT / "data/ref/aoi.geojson"))["features"]
geoms = [transform_geom("EPSG:4326", gcrs, f["geometry"]) for f in feats]
aoi = rasterize(geoms, out_shape=g.shape[1:], transform=gt, fill=0, default_value=1, dtype="uint8").astype(bool)
print(f"\nAOI: {aoi.sum()*100/1e6:.1f} km2 trên lưới 10 m (chuẩn 2514.81)")

ncl = g[5]
valid = (ncl > 0) & aoi
print(f"\n== Độ phủ sạch trong AOI ==")
print(f"pixel n_clear>0: {valid.sum()/aoi.sum()*100:.1f}% AOI | n_clear=0: {(~(ncl>0) & aoi).sum()/aoi.sum()*100:.1f}%")
vals, cnt = np.unique(ncl[aoi], return_counts=True)
for v, c in zip(vals, cnt): print(f"  n_clear={v:2d}: {c/aoi.sum()*100:5.1f}%")
print(f"ngoài AOI: n_clear>0 {((ncl>0)&~aoi).sum()/(~aoi).sum()*100:.1f}% (GEE có thể không cắt theo AOI)")

# nhất quán: n_clear>0 mà băng = 0, hoặc n_clear=0 mà băng ≠ 0
bad1 = valid & (g[:5] == 0).any(0)
bad2 = (ncl == 0) & aoi & (g[:5] != 0).any(0)
print(f"n_clear>0 nhưng có băng=0: {bad1.sum()} | n_clear=0 nhưng băng≠0: {bad2.sum()}")

print("\n== Phản xạ (×1e4) trên pixel hợp lệ trong AOI: p1/p50/p99, tỷ lệ âm hoặc >15000 ==")
for i in range(5):
    x = g[i][valid]
    print(f"  {names[i]:3s}: {np.percentile(x,1):6.0f} {np.percentile(x,50):6.0f} {np.percentile(x,99):6.0f} | <0: {(x<0).mean()*100:.3f}% >15000: {(x>15000).mean()*100:.3f}%")
b4, b8 = g[2][valid].astype("f4"), g[3][valid].astype("f4")
ndvi = (b8 - b4) / np.maximum(b8 + b4, 1)
print(f"  NDVI: p5 {np.percentile(ndvi,5):.2f} p50 {np.median(ndvi):.2f} p95 {np.percentile(ndvi,95):.2f}")

# Đối chiếu với composite_20m.tif (quy GEE về lưới 20 m, trung bình các pixel hợp lệ)
with rasterio.open(REF) as r:
    ref = r.read().astype("f4")
    rt, rcrs, rshape = r.transform, r.crs, (r.height, r.width)
    print(f"\ncomposite_20m: {ref.shape} {r.descriptions}")
import glob
with rasterio.open(glob.glob(str(ROOT / "data/nisar/gcov/*20261022T*frequencyA__HHHH.tif"))[0]) as n:
    aoi20 = np.isfinite(n.read(1))  # mặt nạ AOI chuẩn trên lưới SAR 20 m
A = aoi20.sum()
print(f"AOI trên lưới 20 m (NISAR): {A*400/1e6:.1f} km2")
src_valid = (ref[5] > 0) & aoi20
print(f"composite_20m (AWS SCL) phủ: {src_valid.sum()/A*100:.1f}% AOI")
agg = np.zeros((5,) + rshape, "f4"); w = np.zeros(rshape, "f4")
vm = (ncl > 0).astype("f4")
reproject(vm, w, src_transform=gt, src_crs=gcrs, dst_transform=rt, dst_crs=rcrs, resampling=Resampling.average)
for i in range(5):
    reproject((g[i] * vm).astype("f4"), agg[i], src_transform=gt, src_crs=gcrs, dst_transform=rt, dst_crs=rcrs,
              resampling=Resampling.average)
    agg[i] = np.where(w > 0, agg[i] / np.maximum(w, 1e-6), np.nan)  # chia lại theo tỷ lệ pixel hợp lệ
gee_ok = (w > 0.9) & aoi20
print(f"GEE (>=90% pixel hợp lệ trong ô 20 m) phủ: {gee_ok.sum()/A*100:.1f}% AOI | hợp hai nguồn: {(gee_ok|src_valid).sum()/A*100:.1f}% AOI")
both = gee_ok & src_valid
print(f"ô 20 m có cả hai nguồn (GEE ≥90% pixel hợp lệ): {both.sum()*400/1e6:.0f} km2")
print("so sánh GEE(median 10 m→20 m) với composite_20m (một ngày gần 27/10): trung vị chênh, tương quan")
for i in range(5):
    a, b = agg[i][both], ref[i][both]
    print(f"  {names[i]:3s}: GEE-ref median {np.median(a-b):7.0f} | |chênh| p90 {np.percentile(np.abs(a-b),90):6.0f} | r={np.corrcoef(a,b)[0,1]:.3f}")
na = (agg[3] - agg[2]) / np.maximum(agg[3] + agg[2], 1); nb = (ref[3] - ref[2]) / np.maximum(ref[3] + ref[2], 1)
print(f"  NDVI: GEE-ref median {np.median((na-nb)[both]):.3f} | r={np.corrcoef(na[both], nb[both])[0,1]:.3f}")
only_gee = gee_ok & ~src_valid
print(f"\nGEE phủ thêm so với composite_20m: {only_gee.sum()*400/1e6:.0f} km2 ({only_gee.sum()/A*100:.1f}% AOI)")
