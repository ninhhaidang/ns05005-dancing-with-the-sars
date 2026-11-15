"""Sinh tập kiểm tra MÙ cho bản đồ lớp phủ SAR: N ô 20 m chọn ngẫu nhiên đơn giản trong vùng có ảnh S2 10 m sạch.

Ràng buộc: ô nằm trong AOI, 4 pixel S2 10 m đều sạch (n_clear>0), cách polygon nhãn huấn luyện >= MIN_TRAIN m,
các ô cách nhau >= MIN_GAP m. KHÔNG chọn theo nhãn dự đoán và KHÔNG ghi dự đoán vào file (chấm mù).
Ra: labeling/blind_test_cells.gpkg (layer 'cells', polygon 20x20 m, EPSG:32648; cột label = -1 nghĩa là chưa chấm).
Mã nhãn: 1 Nước, 2 Thực vật, 3 Đất trống, 4 Đô thị/làng, 0 = ô LẪN lớp (không lớp nào chiếm >= ~80%) hoặc không rõ.
Chạy: python -I scripts/make_blind_test.py [N]
"""
import glob, sys
from pathlib import Path
import numpy as np, rasterio, pyogrio
from rasterio.features import rasterize
from rasterio.warp import reproject, Resampling
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from shapely import wkb, box, to_wkb
from shapely.geometry import mapping

ROOT = Path(__file__).resolve().parent.parent
N = int(sys.argv[1]) if len(sys.argv) > 1 else 250
MIN_TRAIN, MIN_GAP, SEED = 200, 200, 20261114
ref = rasterio.open(glob.glob(str(ROOT / "data/nisar/gcov/*20261022T*frequencyA__HHHH.tif"))[0])
aoi = np.isfinite(ref.read(1)); tr = ref.transform

# vùng S2 sạch (cả 4 pixel 10 m trong ô 20 m)
g = rasterio.open(ROOT / "data/s2/gee_10m/S2_composite_10m_aoi.tif"); G = g.read()
vm = ((G[5] > 0) & (G[:5] != 0).all(0)).astype("f4"); frac = np.zeros(ref.shape, "f4")
reproject(vm, frac, src_transform=g.transform, src_crs=g.crs, dst_transform=tr, dst_crs=ref.crs, resampling=Resampling.average)
clear = frac >= 0.99

# khoảng cách tới polygon nhãn huấn luyện (m)
meta, fid, gw, fl = pyogrio.raw.read(ROOT / "labeling/labels_polygon.gpkg")
train = rasterize([mapping(wkb.loads(bytes(w))) for w in gw], out_shape=ref.shape, transform=tr, fill=0, default_value=1,
                  dtype="uint8", all_touched=True).astype(bool)
far = ndi.distance_transform_edt(~train) * 20 >= MIN_TRAIN

ok = aoi & clear & far
rows, cols = np.where(ok)
print(f"ô 20 m trong AOI: {aoi.sum()} | sạch: {(aoi & clear).sum()} ({(aoi & clear).sum()/aoi.sum()*100:.1f}%) | "
      f"và cách nhãn huấn luyện >= {MIN_TRAIN} m: {ok.sum()} ({ok.sum()*400/1e6:.0f} km2)")
rng = np.random.default_rng(SEED); order = rng.permutation(len(rows))
xy_all = np.c_[tr.c + (cols + 0.5) * 20, tr.f - (rows + 0.5) * 20]
chosen = []; tree_pts = []
for i in order:
    p = xy_all[i]
    if tree_pts and cKDTree(tree_pts).query(p)[0] < MIN_GAP: continue
    chosen.append(i); tree_pts.append(p)
    if len(chosen) == N: break
assert len(chosen) == N, f"chỉ chọn được {len(chosen)}"
sel = np.array(chosen); r, c = rows[sel], cols[sel]
polys = [box(tr.c + cc * 20, tr.f - (rr + 1) * 20, tr.c + (cc + 1) * 20, tr.f - rr * 20) for rr, cc in zip(r, c)]

dst = ROOT / "labeling" / "blind_test_cells.gpkg"
if dst.exists(): raise SystemExit(f"{dst} đã tồn tại (có thể đã chấm nhãn); đổi tên/xóa thủ công nếu muốn tạo lại")
label = np.full(N, -1, dtype="int16")  # -1 = chưa chấm (pyogrio không ghi được số nguyên rỗng; sqlite3 không UPDATE được vì trigger GPKG)
pyogrio.raw.write(str(dst), geometry=np.array([to_wkb(p) for p in polys], dtype=object),
                  field_data=[np.arange(1, N + 1, dtype="int32"), label, np.array([""] * N, dtype=object)],
                  fields=["pt_id", "label", "note"], geometry_type="Polygon", crs="EPSG:32648", driver="GPKG",
                  layer="cells", encoding="UTF-8")
print(f"ghi {dst}: {N} ô 20 m (seed {SEED}); cột label = -1 (chưa chấm); điền 1 Nước, 2 Thực vật, 3 Đất trống, 4 Đô thị/làng, 0 lẫn/không rõ)")
