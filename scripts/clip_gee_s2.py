"""Cắt ảnh Sentinel-2 10 m từ GEE theo AOI (UTM 48N), pixel ngoài AOI = 0 (nodata). Không sửa file gốc.

Cũng ghi bản AOI ở EPSG:32648 (data/ref/aoi_32648.geojson) để mở trong QGIS; aoi.geojson gốc (EPSG:4326) giữ nguyên.
Chạy: /Users/ninhhaidang/miniconda3/envs/dwts/bin/python -I scripts/clip_gee_s2.py
"""
import json
from pathlib import Path
import numpy as np, rasterio
import rasterio.features as rf
from rasterio.windows import Window
from rasterio.warp import transform_geom

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data/s2/gee_10m/S2_composite_10m_20261022_20261103.tif"
DST = ROOT / "data/s2/gee_10m/S2_composite_10m_aoi.tif"
GJ = ROOT / "data/ref/aoi.geojson"

geom4326 = json.load(open(GJ))["features"][0]["geometry"]  # file chỉ có 1 feature (đã kiểm)
geom = transform_geom("EPSG:4326", "EPSG:32648", geom4326)

with rasterio.open(SRC) as s:
    assert s.crs.to_epsg() == 32648 and s.res == (10.0, 10.0)
    inv = ~s.transform
    xs = [p[0] for poly in geom["coordinates"] for ring in poly for p in ring]
    ys = [p[1] for poly in geom["coordinates"] for ring in poly for p in ring]
    c0 = int(np.floor(inv * (min(xs), max(ys)))[0]); r0 = int(np.floor((inv * (min(xs), max(ys)))[1]))
    c1 = int(np.ceil((inv * (max(xs), min(ys)))[0])); r1 = int(np.ceil((inv * (max(xs), min(ys)))[1]))
    c0, r0, c1, r1 = max(c0, 0), max(r0, 0), min(c1, s.width), min(r1, s.height)
    win = Window(c0, r0, c1 - c0, r1 - r0)
    tr = s.window_transform(win)
    inside = rf.geometry_mask([geom], out_shape=(win.height, win.width), transform=tr, invert=True)
    print(f"cửa sổ {win.width}x{win.height} (gốc {s.width}x{s.height}); pixel trong AOI {inside.sum()} = {inside.sum()*100/1e6:.1f} km2")
    prof = s.profile | dict(width=win.width, height=win.height, transform=tr, compress="deflate", predictor=2,
                            tiled=True, blockxsize=512, blockysize=512, nodata=0)
    prof.pop("photometric", None)
    with rasterio.open(DST, "w", **prof) as o:
        for i in range(1, s.count + 1):
            a = s.read(i, window=win)
            a[~inside] = 0
            o.write(a, i)
        o.descriptions = s.descriptions
        o.update_tags(note="GEE S2 10 m (median, Cloud Score+ 0.789) cắt theo AOI; ngoài AOI = 0; n_clear=0 là không có quan sát sạch")

# AOI ở EPSG:32648 (file riêng)
from rasterio.enums import Resampling
with rasterio.Env(COMPRESS_OVERVIEW="DEFLATE", GDAL_TIFF_OVR_BLOCKSIZE="512"):
    with rasterio.open(DST, "r+") as o:  # overview nén trong file (giúp QGIS thu phóng nhanh hơn)
        o.build_overviews([2, 4, 8, 16, 32], Resampling.average)

# GeoJSON có khai báo CRS (không theo RFC 7946 nhưng GDAL/QGIS đều đọc được); máy không có fiona/osgeo để ghi gpkg
fc = {"type": "FeatureCollection", "name": "aoi_32648",
      "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::32648"}},
      "features": [{"type": "Feature", "properties": {}, "geometry": geom}]}
json.dump(fc, open(ROOT / "data/ref/aoi_32648.geojson", "w"))
print("ghi data/ref/aoi_32648.geojson")
