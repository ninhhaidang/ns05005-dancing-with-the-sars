"""Bộ phân loại lớp phủ chỉ dùng SAR (áp dụng được cả vùng Sentinel-2 bị mây), huấn luyện từ nhãn POLYGON.

Nhãn: labeling/labels_polygon.gpkg (tạo bằng scripts/merge_label_polygons.py): 1 Nước, 2 Thực vật, 3 Đất trống, 4 Đô thị.
Mẫu: ô SAR 20 m có >= PURE (mặc định 80%) diện tích thuộc một lớp (siêu lấy mẫu 8x8 mỗi ô; với 4x4 ngưỡng 80% bị làm tròn thành 100%), tối đa CAP ô mỗi polygon
(để polygon nước lớn không áp đảo). Mỗi mẫu giữ poly_id và khối 5 km để chia kiểm tra không rò rỉ.
Đánh giá: (a) CV theo khối không gian 5 km (chính, nghiêm hơn); (b) CV theo polygon (tham khảo, lạc quan hơn).
Chạy: /Users/ninhhaidang/miniconda3/envs/dwts/bin/python -I scripts/train_classifier.py
"""
import glob
from pathlib import Path
import numpy as np, rasterio, pyogrio
from rasterio.features import rasterize
from rasterio.transform import Affine
from rasterio.warp import reproject, Resampling
from scipy import ndimage as ndi
from shapely import wkb
from shapely.geometry import mapping
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parent.parent
NAMES = {1: "Nước", 2: "Thực vật", 3: "Đất trống", 4: "Đô thị"}
PURE, CAP, SS = 0.8, 20, 8         # ngưỡng độ thuần, số ô tối đa/polygon, siêu lấy mẫu mỗi chiều
ref = rasterio.open(glob.glob(str(ROOT / "data/nisar/gcov/*20261022T*frequencyA__HHHH.tif"))[0])
assert ref.transform.a == 20 and ref.transform.e == -20
aoi = np.isfinite(ref.read(1))

# ---- đặc trưng SAR (12 đặc trưng, như bản cũ) ----
def sar(d, p):
    s = rasterio.open(glob.glob(str(ROOT / f"data/nisar/gcov/*_{d}T*__frequencyA__{p}.tif"))[0])
    if s.res == ref.res: return s.read(1)
    o = np.full(ref.shape, np.nan, np.float32)
    reproject(s.read(1), o, src_transform=s.transform, src_crs=s.crs, dst_transform=ref.transform, dst_crs=ref.crs,
              resampling=Resampling.average, src_nodata=np.nan, dst_nodata=np.nan)
    return o
D = ["20261022", "20261027", "20261103"]
def db(x): return 10 * np.log10(np.where(x > 0, x, np.nan))
HH = [sar(d, "HHHH") for d in D]; HV = [sar(d, "HVHV") for d in D]
sm = lambda a: ndi.uniform_filter(np.nan_to_num(a, nan=np.nanmedian(a)), 3)
hh_db = [sm(db(x)) for x in HH]; hv_db = [sm(db(x)) for x in HV]
hhm, hvm = np.mean(hh_db, 0), np.mean(hv_db, 0)
tex = np.sqrt(np.maximum(ndi.uniform_filter(hhm ** 2, 7) - ndi.uniform_filter(hhm, 7) ** 2, 0))  # kết cấu
feats = hh_db + hv_db + [hhm, hvm, hvm - hhm, np.std(hh_db, 0), np.std(hv_db, 0), tex]
fnames = [f"HH_{d[4:]}" for d in D] + [f"HV_{d[4:]}" for d in D] + ["HH_tb", "HV_tb", "HV-HH", "std_HH", "std_HV", "texture"]
X = np.stack(feats, -1).astype(np.float32)

# ---- nhãn polygon -> độ phủ từng lớp trên lưới 20 m ----
meta, fid, gw, fl = pyogrio.raw.read(ROOT / "labeling/labels_polygon.gpkg")
fields = dict(zip(meta["fields"], fl))
pid_all, cls_all = np.array(fields["poly_id"]), np.array(fields["class_id"])
H, W = ref.shape; tr0 = ref.transform
cov = np.zeros((4, H, W), np.float32); best = np.zeros((H, W), np.float32); bpid = np.zeros((H, W), np.int32)
for w, pid, c in zip(gw, pid_all, cls_all):
    g = wkb.loads(bytes(w)); x0, y0, x1, y1 = g.bounds
    c0, c1 = max(int(np.floor((x0 - tr0.c) / 20)), 0), min(int(np.ceil((x1 - tr0.c) / 20)), W)
    r0, r1 = max(int(np.floor((tr0.f - y1) / 20)), 0), min(int(np.ceil((tr0.f - y0) / 20)), H)
    if r1 <= r0 or c1 <= c0: continue
    t = Affine(20 / SS, 0, tr0.c + c0 * 20, 0, -20 / SS, tr0.f - r0 * 20)
    m = rasterize([mapping(g)], out_shape=((r1 - r0) * SS, (c1 - c0) * SS), transform=t, fill=0, default_value=1, dtype="uint8")
    f = m.reshape(r1 - r0, SS, c1 - c0, SS).mean((1, 3)).astype(np.float32)
    cov[c - 1, r0:r1, c0:c1] += f
    upd = f > best[r0:r1, c0:c1]
    best[r0:r1, c0:c1][upd] = f[upd]; bpid[r0:r1, c0:c1][upd] = pid
cov = np.minimum(cov, 1)
dom = cov.argmax(0) + 1; pur = cov.max(0)
print(f"polygon: {len(pid_all)} | ô 20 m được polygon chạm tới: {(pur > 0).sum()}")
print("Số ô 20 m thuần theo ngưỡng (số polygon đóng góp):")
for k, n in NAMES.items():
    s = f"  {n:10s}"
    for thr in (0.5, 0.8, 1.0):
        m = (dom == k) & (pur >= thr); s += f" ≥{thr:.1f}: {m.sum():6d} ({len(np.unique(bpid[m]))} poly)"
    print(s)

rng = np.random.default_rng(0)
rows, cols = np.where((pur >= PURE) & aoi)
order = rng.permutation(len(rows)); rows, cols = rows[order], cols[order]
cnt, keep = {}, []
for i, (r, c) in enumerate(zip(rows, cols)):
    p = bpid[r, c]
    if cnt.get(p, 0) < CAP: cnt[p] = cnt.get(p, 0) + 1; keep.append(i)
rows, cols = rows[keep], cols[keep]
y = dom[rows, cols]; grp_poly = bpid[rows, cols]; grp_blk = (rows // 250) * 100 + cols // 250   # khối 5 km
xs = X[rows, cols]; ok = np.isfinite(xs).all(1)
xs, y, grp_poly, grp_blk, rows, cols = xs[ok], y[ok], grp_poly[ok], grp_blk[ok], rows[ok], cols[ok]
print(f"\nMẫu dùng (độ thuần ≥ {PURE:.0%}, tối đa {CAP} ô/polygon): {len(y)} | " +
      ", ".join(f"{n} {int((y == k).sum())}" for k, n in NAMES.items()) + f" | khối 5 km: {len(np.unique(grp_blk))}")
np.savetxt(ROOT / "data/derived/samples_polygon_20m.csv", np.c_[rows, cols, y, grp_poly], fmt="%d", delimiter=",", header="row,col,class,poly_id", comments="")

rf = lambda: RandomForestClassifier(300, min_samples_leaf=2, class_weight="balanced", random_state=0, n_jobs=-1)
def report(y, p, tag):
    print(f"\n{tag}: độ chính xác {accuracy_score(y, p)*100:.1f}% | cân bằng lớp {balanced_accuracy_score(y, p)*100:.1f}% | "
          f"F1 macro {f1_score(y, p, average='macro')*100:.1f}% (n={len(y)})")
    cm = confusion_matrix(y, p, labels=[1, 2, 3, 4]); print("  hàng = nhãn thật, cột = dự đoán")
    print("            " + " ".join(f"{NAMES[k]:>9}" for k in NAMES) + "   recall")
    for i, k in enumerate(NAMES): print(f"{NAMES[k]:>10}  " + " ".join(f"{cm[i, j]:>9}" for j in range(4)) + f"   {cm[i, i]/max(cm[i].sum(), 1)*100:5.1f}%")
def cv(groups):
    pred = np.zeros(len(y), int)
    for a, b in GroupKFold(5).split(xs, y, groups): pred[b] = rf().fit(xs[a], y[a]).predict(xs[b])
    return pred
base = np.bincount(y).argmax()
print(f"\nMốc so sánh: luôn đoán lớp đông nhất ({NAMES[base]}) = {accuracy_score(y, np.full(len(y), base))*100:.1f}% (cân bằng lớp 25%)")
report(y, cv(grp_blk), "(a) CV theo khối không gian 5 km  [chỉ số chính]")
report(y, cv(grp_poly), "(b) CV theo polygon  [lạc quan hơn: polygon láng giềng có thể ở hai phía]")

final = rf().fit(xs, y)
imp = sorted(zip(final.feature_importances_, fnames), reverse=True)[:6]; print("\nĐặc trưng quan trọng:", ", ".join(f"{n} {v:.2f}" for v, n in imp))
idx = np.where(aoi); out = np.zeros(ref.shape, np.uint8)
for s in range(0, len(idx[0]), 1_000_000):
    r, c = idx[0][s:s + 1_000_000], idx[1][s:s + 1_000_000]; out[r, c] = final.predict(X[r, c])
(ROOT / "data/derived").mkdir(parents=True, exist_ok=True)
prof = ref.profile; prof.update(dtype="uint8", nodata=0, compress="deflate", predictor=2)
with rasterio.open(ROOT / "data/derived/landcover_sar_20m.tif", "w", **prof) as o: o.write(out, 1)
tot = aoi.sum(); print("\nDiện tích dự đoán toàn AOI (chưa hiệu chỉnh; mẫu huấn luyện chỉ nằm ở vùng ảnh S2 sạch):")
for k, n in NAMES.items(): print(f"  {n}: {(out==k).sum()*400/1e6:.0f} km2 ({(out==k).sum()/tot*100:.1f}%)")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
fig, ax = plt.subplots(figsize=(8, 9)); ax.imshow(np.where(out > 0, out, np.nan)[::2, ::2], cmap=ListedColormap(["#2b6cb0", "#68a03f", "#d6b370", "#c0392b"]), vmin=1, vmax=4, interpolation="nearest")
ax.axis("off"); ax.set_title("Lớp phủ dự đoán từ SAR (nước / thực vật / đất trống / đô thị)")
(ROOT / "outputs").mkdir(exist_ok=True); fig.savefig(ROOT / "outputs/landcover_sar.png", dpi=80, bbox_inches="tight")
