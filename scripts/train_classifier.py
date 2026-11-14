"""Bộ phân loại lớp phủ chỉ dùng SAR (áp dụng được cả vùng Sentinel-2 bị mây), huấn luyện từ nhãn POLYGON.

Nhãn: labeling/labels_polygon.gpkg (tạo bằng scripts/merge_label_polygons.py): 1 Nước, 2 Thực vật, 3 Đất trống, 4 Đô thị.
Đặc trưng và mẫu: scripts/sar_dataset.py (ô 20 m thuần >= 80%, tối đa 20 ô/polygon).
Đánh giá: (a) CV theo khối không gian 5 km (chính, nghiêm hơn); (b) CV theo polygon (tham khảo, lạc quan hơn).
So sánh nhiều mô hình / đặc trưng / cách kiểm chứng: scripts/experiments.py.
Chạy: /Users/ninhhaidang/miniconda3/envs/dwts/bin/python -I scripts/train_classifier.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I bỏ thư mục script khỏi sys.path
import numpy as np, rasterio
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import GroupKFold
from sar_dataset import ROOT, NAMES, FNAMES, load

PURE, CAP = 0.8, 20
d = load(pure=PURE, cap=CAP)
ref, X, aoi, xs, y, rows, cols, grp_poly = d["ref"], d["X"], d["aoi"], d["xs"], d["y"], d["rows"], d["cols"], d["poly"]
grp_blk = (rows // 250) * 100 + cols // 250   # khối 5 km
print(f"\nMẫu dùng (độ thuần ≥ {PURE:.0%}, tối đa {CAP} ô/polygon): {len(y)} | " +
      ", ".join(f"{n} {int((y == k).sum())}" for k, n in NAMES.items()) + f" | khối 5 km: {len(np.unique(grp_blk))}")
(ROOT / "data/derived").mkdir(parents=True, exist_ok=True)
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
imp = sorted(zip(final.feature_importances_, FNAMES), reverse=True)[:6]; print("\nĐặc trưng quan trọng:", ", ".join(f"{n} {v:.2f}" for v, n in imp))
idx = np.where(aoi); out = np.zeros(ref.shape, np.uint8)
for s in range(0, len(idx[0]), 1_000_000):
    r, c = idx[0][s:s + 1_000_000], idx[1][s:s + 1_000_000]; out[r, c] = final.predict(X[r, c])
prof = ref.profile; prof.update(dtype="uint8", nodata=0, compress="deflate", predictor=2)
with rasterio.open(ROOT / "data/derived/landcover_sar_20m.tif", "w", **prof) as o: o.write(out, 1)
tot = aoi.sum(); print("\nDiện tích dự đoán toàn AOI (chưa hiệu chỉnh; mẫu huấn luyện chỉ nằm ở vùng ảnh S2 sạch):")
for k, n in NAMES.items(): print(f"  {n}: {(out==k).sum()*400/1e6:.0f} km2 ({(out==k).sum()/tot*100:.1f}%)")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
fig, ax = plt.subplots(figsize=(8, 9)); ax.imshow(np.where(out > 0, out, np.nan)[::2, ::2], cmap=ListedColormap(["#2b6cb0", "#68a03f", "#d6b370", "#c0392b"]), vmin=1, vmax=4, interpolation="nearest")
ax.axis("off"); ax.set_title("Lớp phủ dự đoán từ SAR (nước / thực vật / đất trống / đô thị)")
(ROOT / "outputs").mkdir(exist_ok=True); fig.savefig(ROOT / "outputs/landcover_sar.png", dpi=80, bbox_inches="tight")
