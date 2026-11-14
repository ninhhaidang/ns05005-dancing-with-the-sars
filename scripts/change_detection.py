"""Phát hiện thay đổi có kiểm định thống kê, cặp cùng track 22/10 -> 3/11 (20 m).

Mô hình: cường độ multilook ~ Gamma(L). Log tỷ số hai ảnh độc lập có phương sai 2*trigamma(L).
L hiệu dụng = tổng numberOfLooks trong cửa sổ K x K; hiệu chỉnh hệ số tương quan speckle
bằng độ lệch tuyệt đối trung vị (MAD) trên toàn ảnh, rồi đặt ngưỡng |z| > Z.
"""
import glob
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.special import polygamma
from pyproj import Transformer

ROOT = Path(__file__).resolve().parent.parent
K, Z, MIN_PX = 5, 5.0, 125  # cửa sổ, ngưỡng z, diện tích tối thiểu 125 px = 0,05 km2
D0, D1 = "20261022", "20261103"
def path(d, p): return glob.glob(str(ROOT / f"data/nisar/gcov/*_{d}T*__frequencyA__{p}.tif"))[0]
def rd(d, p): return rasterio.open(path(d, p)).read(1).astype(np.float64)
ref = rasterio.open(path(D0, "HHHH"))

I = {(d, p): rd(d, p) for d in (D0, D1) for p in ("HHHH", "HVHV")}
L = rd(D0, "numberOfLooks") + rd(D1, "numberOfLooks")  # chỉ dùng để lấy mức looks trung bình
L0, L1 = rd(D0, "numberOfLooks"), rd(D1, "numberOfLooks")
ok = np.isfinite(I[(D0, "HHHH")]) & np.isfinite(I[(D1, "HHHH")]) & (L0 > 0) & (L1 > 0)
w = ndi.uniform_filter(ok.astype(float), K)
def mean(x): return np.where(ok, ndi.uniform_filter(np.where(ok, x, 0), K) / np.maximum(w, 1e-9), np.nan)
Leff0 = mean(L0) * w * K * K; Leff1 = mean(L1) * w * K * K  # tổng looks trong cửa sổ

res = {}
for p in ("HHHH", "HVHV"):
    a, b = mean(I[(D0, p)]), mean(I[(D1, p)])
    z = np.log(b / a)
    sd = np.sqrt(polygamma(1, Leff0) + polygamma(1, Leff1))
    f = 1.4826 * np.nanmedian(np.abs(z[ok] - np.nanmedian(z[ok]))) / np.nanmedian(sd[ok])
    res[p] = dict(z=z / (f * sd), d=10 * np.log10(b / a), f=f, a=10 * np.log10(a), b=10 * np.log10(b))
    print(f"{p}: hệ số tương quan speckle f={f:.2f} (1 = độc lập)")

zh, zv = res["HHHH"]["z"], res["HVHV"]["z"]
sig_dn = (zh < -Z) & (zv < -Z); sig_up = (zh > Z) & (zv > Z)
sig_hv = (np.abs(zv) > Z) & ~(np.abs(zh) > Z)
bh = res["HHHH"]["b"]
cls = np.zeros(ref.shape, np.uint8)
cls[ok] = 1                                                    # không đổi đáng kể
cls[sig_dn & (bh < -15)] = 2                                   # nước mới / mặt phẳng hóa
cls[sig_dn & (bh >= -15)] = 3                                  # giảm cả HH, HV (khác)
cls[sig_up] = 4                                                # tăng cả HH, HV
cls[sig_hv & (zv < 0)] = 5                                     # chỉ HV giảm
cls[sig_hv & (zv > 0)] = 6                                     # chỉ HV tăng
# bỏ mảng nhỏ hơn MIN_PX
for c in (2, 3, 4, 5, 6):
    lab, n = ndi.label(cls == c); sz = ndi.sum(lab > 0, lab, range(1, n + 1))
    small = np.isin(lab, np.where(np.array(sz) < MIN_PX)[0] + 1); cls[small & (cls == c)] = 1
names = {1: "không đổi đáng kể", 2: "nước mới/mặt phẳng hóa (HH,HV giảm, HH cuối<-15 dB)", 3: "giảm HH,HV (khác)", 4: "tăng HH,HV", 5: "chỉ HV giảm", 6: "chỉ HV tăng"}
tot = ok.sum(); tr = Transformer.from_crs(32648, 4326, always_xy=True)
rows = []
for c in range(1, 7):
    m = cls == c; print(f"  lớp {c} {names[c]}: {m.sum()*400/1e6:.1f} km2 ({m.sum()/tot*100:.2f}%)")
    if c == 1: continue
    lab, n = ndi.label(m)
    for i in range(1, n + 1):
        rg = lab == i; r, cc = ndi.center_of_mass(rg); x, y = ref.xy(r, cc); lon, lat = tr.transform(x, y)
        rows.append((c, rg.sum() * 400 / 1e6, lon, lat, np.nanmean(res["HHHH"]["a"][rg]), np.nanmean(res["HHHH"]["b"][rg])))
rows.sort(key=lambda t: -t[1])
(ROOT / "outputs").mkdir(exist_ok=True)
with open(ROOT / "outputs/change_patches.csv", "w") as f:
    f.write("class,area_km2,lon,lat,HH_22oct_dB,HH_3nov_dB\n")
    for t in rows: f.write("%d,%.3f,%.4f,%.4f,%.1f,%.1f\n" % t)
print("số mảng:", len(rows), "| 8 mảng lớn nhất (lớp, km2, lon, lat, HH22/10, HH3/11):")
for t in rows[:8]: print("  %d  %.2f  %.4fE %.4fN  %.1f -> %.1f dB" % (t[0], t[1], t[2], t[3], t[4], t[5]))
out = ROOT / "data/derived"; out.mkdir(parents=True, exist_ok=True)
prof = ref.profile; prof.update(dtype="uint8", nodata=0, compress="deflate", predictor=2)
with rasterio.open(out / "change_class_22oct_3nov.tif", "w", **prof) as dst: dst.write(cls, 1)
fig, ax = plt.subplots(figsize=(8, 9))
ax.imshow(np.where(cls > 0, cls, np.nan)[::2, ::2], cmap=ListedColormap(["#e5e5e5", "#1f4ed8", "#f59e0b", "#dc2626", "#7c3aed", "#10b981"]), vmin=1, vmax=6, interpolation="nearest")
ax.set_title("Thay đổi có ý nghĩa thống kê 22/10 → 3/11 (z>%.0f, ≥0,05 km²)" % Z); ax.axis("off")
fig.savefig(ROOT / "outputs/change_detection.png", dpi=80, bbox_inches="tight")
