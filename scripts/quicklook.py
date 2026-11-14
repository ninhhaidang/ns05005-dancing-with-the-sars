"""Ảnh xem nhanh GCOV VALIDATED (dB) và thay đổi 22/10 -> 3/11."""
import glob
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.enums import Resampling

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data/nisar/gcov"
S = 4  # giảm mẫu để vẽ nhanh


def load(date, pol, ds=S, shape=None):
    f = glob.glob(str(D / f"*_{date}T*__frequencyA__{pol}.tif"))[0]
    with rasterio.open(f) as s:
        shp = shape or (s.height // ds, s.width // ds)
        a = s.read(1, out_shape=shp, resampling=Resampling.average)
    return 10 * np.log10(np.where(a > 0, a, np.nan))

dates = ["20261022", "20261027", "20261103"]
fig, ax = plt.subplots(2, 3, figsize=(15, 10))
for j, d in enumerate(dates):
    for i, (pol, lim) in enumerate([("HHHH", (-20, 0)), ("HVHV", (-28, -8))]):
        im = ax[i, j].imshow(load(d, pol, 4 if d != "20261027" else 8), cmap="gray", vmin=lim[0], vmax=lim[1])
        ax[i, j].set_title(f"{d[6:]}/{d[4:6]} {pol[:2]} (dB)"); ax[i, j].axis("off")
fig.tight_layout(); fig.savefig(ROOT / "outputs/quicklook.png", dpi=80)

a, b = load("20261022", "HHHH", 1), load("20261103", "HHHH", 1)
ah, bh = load("20261022", "HVHV", 1), load("20261103", "HVHV", 1)
dhh, dhv = b - a, bh - ah
ok = np.isfinite(dhh)
print("pixel hợp lệ", ok.sum())
for n, d in [("HH", dhh), ("HV", dhv)]:
    v = d[ok & np.isfinite(d)]
    print(n, "Δ dB: mean %.2f median %.2f p5 %.2f p95 %.2f std %.2f; |Δ|>3dB: %.1f%%" % (v.mean(), np.median(v), *np.percentile(v, [5, 95]), v.std(), (abs(v) > 3).mean() * 100))
fig, ax = plt.subplots(1, 2, figsize=(14, 7))
for k, (n, d) in enumerate([("HH", dhh), ("HV", dhv)]):
    im = ax[k].imshow(d[::2, ::2], cmap="RdBu", vmin=-6, vmax=6); ax[k].set_title(f"{n}: 3/11 − 22/10 (dB)"); ax[k].axis("off")
fig.colorbar(im, ax=ax, shrink=0.6); fig.savefig(ROOT / "outputs/change_22oct_3nov.png", dpi=80)
