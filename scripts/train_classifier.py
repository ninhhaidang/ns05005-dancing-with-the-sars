"""Bộ phân loại lớp phủ chỉ dùng SAR (áp dụng được cả vùng Sentinel-2 bị mây).

Nhãn: vòng 1 (labeling/labels.csv, nhãn gần như trùng gợi ý) và vòng 2 (labeling/labels_r2.csv, nhãn mù).
Đánh giá: (a) huấn luyện vòng 1 -> kiểm tra vòng 2 (độc lập); (b) CV theo khối không gian 5 km trên vòng 1+2.
"""
import csv, glob
from pathlib import Path
import numpy as np, rasterio
from rasterio.warp import reproject, Resampling
from scipy import ndimage as ndi
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parent.parent
NAMES = {1: "Nước", 2: "Thực vật", 3: "Đất trống", 4: "Đô thị"}
ref = rasterio.open(glob.glob(str(ROOT / "data/nisar/gcov/*20261022T*frequencyA__HHHH.tif"))[0])
aoi = np.isfinite(ref.read(1))
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

def load(f):
    rows = list(csv.DictReader(open(ROOT / "labeling" / f)))
    return np.array([[int(r["row"]), int(r["col"]), int(r["label"])] for r in rows])
L1, L2 = load("labels.csv"), load("labels_r2.csv")
def xy(L): return X[L[:, 0], L[:, 1]], L[:, 2]
rf = lambda: RandomForestClassifier(300, min_samples_leaf=2, class_weight="balanced", random_state=0, n_jobs=-1)
print(f"mẫu vòng 1: {len(L1)}, vòng 2 (mù): {len(L2)}")

def report(y, p, tag):
    print(f"\n{tag}: độ chính xác {accuracy_score(y, p)*100:.1f}% | F1 macro {f1_score(y, p, average='macro')*100:.1f}% (n={len(y)})")
    cm = confusion_matrix(y, p, labels=[1, 2, 3, 4]); print("      " + " ".join(f"{NAMES[k]:>9}" for k in NAMES))
    for i, k in enumerate(NAMES): print(f"{NAMES[k]:>9}" + " ".join(f"{cm[i, j]:>9}" for j in range(4)))
x1, y1 = xy(L1); x2, y2 = xy(L2)
m = rf().fit(x1, y1); report(y2, m.predict(x2), "(a) Huấn luyện vòng 1 -> kiểm tra nhãn MÙ vòng 2")
base = np.full(len(y2), np.bincount(y2).argmax()); print(f"    (mốc so sánh: luôn đoán lớp đông nhất = {accuracy_score(y2, base)*100:.1f}%)")
Lall = np.vstack([L1, L2]); xa, ya = xy(Lall); groups = (Lall[:, 0] // 250) * 100 + Lall[:, 1] // 250  # khối 5 km
pred = np.zeros(len(ya), int)
for tr_i, te_i in GroupKFold(5).split(xa, ya, groups): pred[te_i] = rf().fit(xa[tr_i], ya[tr_i]).predict(xa[te_i])
report(ya, pred, "(b) CV theo khối không gian 5 km trên vòng 1+2")
mask2 = np.r_[np.zeros(len(L1), bool), np.ones(len(L2), bool)]
print(f"    riêng phần nhãn mù (vòng 2) trong CV: {accuracy_score(ya[mask2], pred[mask2])*100:.1f}%")
final = rf().fit(xa, ya)
imp = sorted(zip(final.feature_importances_, fnames), reverse=True)[:6]; print("\nĐặc trưng quan trọng:", ", ".join(f"{n} {v:.2f}" for v, n in imp))
idx = np.where(aoi); out = np.zeros(ref.shape, np.uint8)
for s in range(0, len(idx[0]), 1_000_000):
    r, c = idx[0][s:s + 1_000_000], idx[1][s:s + 1_000_000]; out[r, c] = final.predict(X[r, c])
(ROOT / "data/derived").mkdir(parents=True, exist_ok=True)
prof = ref.profile; prof.update(dtype="uint8", nodata=0, compress="deflate", predictor=2)
with rasterio.open(ROOT / "data/derived/landcover_sar_20m.tif", "w", **prof) as o: o.write(out, 1)
tot = aoi.sum(); print("\nDiện tích dự đoán toàn AOI:")
for k, n in NAMES.items(): print(f"  {n}: {(out==k).sum()*400/1e6:.0f} km2 ({(out==k).sum()/tot*100:.1f}%)")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
fig, ax = plt.subplots(figsize=(8, 9)); ax.imshow(np.where(out > 0, out, np.nan)[::2, ::2], cmap=ListedColormap(["#2b6cb0", "#68a03f", "#d6b370", "#c0392b"]), vmin=1, vmax=4, interpolation="nearest")
ax.axis("off"); ax.set_title("Lớp phủ dự đoán từ SAR (nước / thực vật / đất trống / đô thị)")
(ROOT / "outputs").mkdir(exist_ok=True); fig.savefig(ROOT / "outputs/landcover_sar.png", dpi=80, bbox_inches="tight")
