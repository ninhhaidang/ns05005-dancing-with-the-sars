"""Hậu xử lý bản đồ lớp phủ SAR: lọc đa số 3x3 để giảm nhiễu hạt tiêu.

Vào: data/derived/landcover_sar_20m.tif (train_classifier.py; 0 = ngoài AOI, 1..4 = Nước, Thực vật, Đất trống, Đô thị).
Ra:  data/derived/landcover_sar_20m_smooth.tif.
Quy tắc: mỗi ô nhận lớp xuất hiện nhiều nhất trong cửa sổ 3x3 (chỉ đếm ô trong AOI); hòa phiếu thì giữ lớp cũ.
Lưu ý: chưa đo được tác động lên độ chính xác (không có tập kiểm tra độc lập), chỉ dùng cho hiển thị bản đồ.
Chạy: /Users/ninhhaidang/miniconda3/envs/dwts/bin/python -I scripts/postprocess_landcover.py
"""
from pathlib import Path
import numpy as np, rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parent.parent
NAMES = {1: "Nước", 2: "Thực vật", 3: "Đất trống", 4: "Đô thị"}
SRC, DST = ROOT / "data/derived/landcover_sar_20m.tif", ROOT / "data/derived/landcover_sar_20m_smooth.tif"

with rasterio.open(SRC) as r:
    lc, prof = r.read(1), r.profile
aoi = lc > 0
votes = np.stack([ndi.uniform_filter((lc == k).astype(np.float32), 3, mode="constant") for k in NAMES])  # tỷ lệ phiếu
best = votes.max(0)
cur = np.take_along_axis(votes, np.clip(lc.astype(int) - 1, 0, 3)[None], 0)[0]
out = np.where(aoi & (cur < best - 1e-6), votes.argmax(0) + 1, lc).astype(np.uint8)
out[~aoi] = 0

with rasterio.open(DST, "w", **prof) as d:
    d.write(out, 1)
tot = aoi.sum()
print(f"Ô đổi lớp: {(out != lc).sum():,} ({(out != lc).sum() / tot * 100:.1f}% AOI)")
print("Lớp        trước lọc        sau lọc")
for k, n in NAMES.items():
    a, b = (lc == k).sum(), (out == k).sum()
    print(f"  {n:10s} {a * 400 / 1e6:7.0f} km² {a / tot * 100:5.1f}%   {b * 400 / 1e6:7.0f} km² {b / tot * 100:5.1f}%")
