"""Gộp 4 shapefile nhãn polygon (ArcGIS Pro: water, vegetation, bareland, building) thành 1 GeoPackage.

Dùng: /Users/ninhhaidang/miniconda3/envs/dwts/bin/python -I scripts/merge_label_polygons.py <thư mục chứa .shp> [đầu ra .gpkg]
- Mã lớp theo quy ước dự án: 1 Nước, 2 Thực vật, 3 Đất trống, 4 Đô thị/làng (building).
- Bỏ chiều Z (PolygonZ -> Polygon), gán CRS EPSG:32648 (.prj của ArcGIS là WKT, không có mã EPSG).
- Thêm cột: poly_id (duy nhất, dùng để chia train/test theo polygon), class_id, class_name, source, area_m2.
Không sửa shapefile gốc.
"""
import sys
from pathlib import Path
import numpy as np
import pyogrio
from pyogrio.raw import read as raw_read, write as raw_write
from shapely import wkb, force_2d, to_wkb, make_valid, get_type_id

ROOT = Path(__file__).resolve().parent.parent
src = Path(sys.argv[1])
dst = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "labeling" / "labels_polygon.gpkg"
CLASSES = [("water", 1, "Nuoc"), ("vegetation", 2, "Thuc vat"), ("bareland", 3, "Dat trong"), ("building", 4, "Do thi/lang")]

geoms, pid, cid, cname, source, area = [], [], [], [], [], []
n = 0
for stem, c, _vn in CLASSES:
    meta, fid, gw, fields = raw_read(src / f"{stem}.shp")
    for w in gw:
        geo = wkb.loads(bytes(w))
        geo = force_2d(geo)
        if not geo.is_valid:
            geo = make_valid(geo)
        n += 1
        geoms.append(geo); pid.append(n); cid.append(c); cname.append(stem); source.append(f"{stem}.shp")
        area.append(geo.area)

# mọi hình học phải là (Multi)Polygon; ép về MultiPolygon cho đồng nhất
from shapely.geometry import MultiPolygon
fixed = []
for g in geoms:
    if g.geom_type == "Polygon": g = MultiPolygon([g])
    assert g.geom_type == "MultiPolygon", g.geom_type
    fixed.append(g)

dst.parent.mkdir(parents=True, exist_ok=True)
if dst.exists(): dst.unlink()
raw_write(
    str(dst), geometry=np.array([to_wkb(g) for g in fixed], dtype=object),
    field_data=[np.array(pid, "int32"), np.array(cid, "int16"), np.array(cname, dtype=object),
                np.array(source, dtype=object), np.array(area, "float64")],
    fields=["poly_id", "class_id", "class_name", "source", "area_m2"],
    geometry_type="MultiPolygon", crs="EPSG:32648", driver="GPKG", layer="labels", encoding="UTF-8")
print(f"ghi {dst} ({n} polygon)")
