"""Đánh giá bản đồ lớp phủ SAR bằng tập kiểm tra mù (labeling/blind_test_cells.gpkg, tạo bởi make_blind_test.py).

label: 1 Nước, 2 Thực vật, 3 Đất trống, 4 Đô thị/làng, 0 = ô lẫn/không rõ, -1 = chưa chấm (bị bỏ qua).
Báo: độ chính xác trên ô thuần (1-4) kèm khoảng tin cậy Wilson 95%, ma trận nhầm, recall/precision từng lớp,
tỷ lệ ô lẫn, và so tỷ lệ lớp mẫu thật với tỷ lệ bản đồ dự đoán trên chính các ô này.
Chạy: /Users/ninhhaidang/miniconda3/envs/dwts/bin/python -I scripts/eval_blind.py [file.gpkg]
"""
import sys
from pathlib import Path
import numpy as np, rasterio, pyogrio
from shapely import wkb
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, f1_score

ROOT = Path(__file__).resolve().parent.parent
P = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "labeling/blind_test_cells.gpkg"
NAMES = {1: "Nước", 2: "Thực vật", 3: "Đất trống", 4: "Đô thị"}
def wilson(k, n, z=1.96):
    if n == 0: return (np.nan, np.nan)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - h) / d, (c + h) / d

meta, fid, gw, fl = pyogrio.raw.read(P)
f = dict(zip(meta["fields"], fl)); lab = np.array(f["label"]).astype(int)
mp = rasterio.open(ROOT / "data/derived/landcover_sar_20m.tif"); M = mp.read(1)
cx = np.array([wkb.loads(bytes(w)).centroid.coords[0] for w in gw])
rr, cc = rasterio.transform.rowcol(mp.transform, cx[:, 0], cx[:, 1]); pred = M[rr, cc].astype(int)

n_all = len(lab); n_un = int((lab == -1).sum()); n_mix = int((lab == 0).sum())
bad = ~np.isin(lab, [-1, 0, 1, 2, 3, 4]); assert not bad.any(), f"nhãn ngoài 0-4/-1: {np.unique(lab[bad])}"
print(f"tổng {n_all} ô | chưa chấm {n_un} | lẫn/không rõ (0) {n_mix} | thuần (1-4) {n_all - n_un - n_mix}")
if n_all - n_un == 0: raise SystemExit("chưa có nhãn nào")
lo, hi = wilson(n_mix, n_all - n_un)
print(f"tỷ lệ ô lẫn trong ô đã chấm: {n_mix/(n_all-n_un)*100:.0f}% (95%: {lo*100:.0f}-{hi*100:.0f}%) -> bản đồ 4 lớp không mô tả được phần này")
m = np.isin(lab, [1, 2, 3, 4]); y, p = lab[m], pred[m]
if (p == 0).any(): print(f"cảnh báo: {(p==0).sum()} ô thuần rơi ngoài vùng dự đoán (bản đồ = 0)")
acc_k = int((y == p).sum()); lo, hi = wilson(acc_k, len(y))
print(f"\nĐỘ CHÍNH XÁC trên ô thuần: {acc_k/len(y)*100:.1f}% ({acc_k}/{len(y)}), khoảng tin cậy 95% Wilson {lo*100:.1f}-{hi*100:.1f}%")
print(f"cân bằng lớp {balanced_accuracy_score(y, p)*100:.1f}% | F1 macro {f1_score(y, p, average='macro', labels=[1,2,3,4], zero_division=0)*100:.1f}%"
      f" | mốc luôn đoán lớp đông nhất ({NAMES[np.bincount(y).argmax()]}): {(y == np.bincount(y).argmax()).mean()*100:.1f}%")
cm = confusion_matrix(y, p, labels=[1, 2, 3, 4]); print("hàng = nhãn thật, cột = dự đoán")
print("            " + " ".join(f"{NAMES[k]:>9}" for k in NAMES) + "   recall  precision")
for i, k in enumerate(NAMES):
    rec = cm[i, i] / max(cm[i].sum(), 1) * 100; pr = cm[i, i] / max(cm[:, i].sum(), 1) * 100
    print(f"{NAMES[k]:>10}  " + " ".join(f"{cm[i, j]:>9}" for j in range(4)) + f"   {rec:5.1f}%   {pr:5.1f}%  (n thật={cm[i].sum()})")
print("\nTỷ lệ lớp trên các ô thuần: mẫu thật vs bản đồ dự đoán (cùng các ô; n nhỏ nên khoảng tin cậy rộng):")
for k, n in NAMES.items():
    t, q = (y == k).sum(), (p == k).sum(); lo, hi = wilson(int(t), len(y))
    print(f"  {n:10s} thật {t/len(y)*100:5.1f}% (95%: {lo*100:4.1f}-{hi*100:4.1f}%) | dự đoán {q/len(y)*100:5.1f}%")
if len(y) < 100: print(f"\nLƯU Ý: chỉ {len(y)} ô thuần, sai số lớn; lớp hiếm (ít hơn ~20 ô thật) thì recall/precision rất thiếu tin cậy.")
