"""Dựng đặc trưng SAR (lưới 20 m) và mẫu huấn luyện từ nhãn polygon. Dùng chung cho train_classifier.py và experiments.py.

Đặc trưng (12): HH, HV (dB, làm trơn 3x3) của 22/10, 27/10, 3/11; HH, HV trung bình; HV-HH; độ lệch chuẩn HH, HV qua 3 ngày;
kết cấu (độ lệch chuẩn cục bộ 7x7 của HH trung bình).
Mẫu: ô 20 m có >= PURE diện tích thuộc một lớp (siêu lấy mẫu 8x8; với 4x4 ngưỡng 80% bị làm tròn thành 100%),
tối đa CAP ô mỗi polygon. Mỗi mẫu có poly_id và chỉ số hàng/cột để chia kiểm tra theo không gian.
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

ROOT = Path(__file__).resolve().parent.parent
NAMES = {1: "Nước", 2: "Thực vật", 3: "Đất trống", 4: "Đô thị"}
DATES = ["20261022", "20261027", "20261103"]
FNAMES = [f"HH_{d[4:]}" for d in DATES] + [f"HV_{d[4:]}" for d in DATES] + ["HH_tb", "HV_tb", "HV-HH", "std_HH", "std_HV", "texture"]


def reference():
    return rasterio.open(glob.glob(str(ROOT / "data/nisar/gcov/*20261022T*frequencyA__HHHH.tif"))[0])


def features(ref):
    """Trả về X (H, W, 12) float32 và mặt nạ AOI."""
    aoi = np.isfinite(ref.read(1))
    def sar(d, p):
        s = rasterio.open(glob.glob(str(ROOT / f"data/nisar/gcov/*_{d}T*__frequencyA__{p}.tif"))[0])
        if s.res == ref.res: return s.read(1)
        o = np.full(ref.shape, np.nan, np.float32)
        reproject(s.read(1), o, src_transform=s.transform, src_crs=s.crs, dst_transform=ref.transform, dst_crs=ref.crs,
                  resampling=Resampling.average, src_nodata=np.nan, dst_nodata=np.nan)
        return o
    db = lambda x: 10 * np.log10(np.where(x > 0, x, np.nan))
    sm = lambda a: ndi.uniform_filter(np.nan_to_num(a, nan=np.nanmedian(a)), 3)
    hh_db = [sm(db(sar(d, "HHHH"))) for d in DATES]; hv_db = [sm(db(sar(d, "HVHV"))) for d in DATES]
    hhm, hvm = np.mean(hh_db, 0), np.mean(hv_db, 0)
    tex = np.sqrt(np.maximum(ndi.uniform_filter(hhm ** 2, 7) - ndi.uniform_filter(hhm, 7) ** 2, 0))
    feats = hh_db + hv_db + [hhm, hvm, hvm - hhm, np.std(hh_db, 0), np.std(hv_db, 0), tex]
    return np.stack(feats, -1).astype(np.float32), aoi


def samples(ref, aoi, pure=0.8, cap=20, ss=8, seed=0, verbose=True):
    """Trả về rows, cols, y, poly_id của các ô mẫu (đã lọc thuần và giới hạn cap ô/polygon)."""
    assert ref.transform.a == 20 and ref.transform.e == -20
    meta, fid, gw, fl = pyogrio.raw.read(ROOT / "labeling/labels_polygon.gpkg")
    f = dict(zip(meta["fields"], fl))
    H, W = ref.shape; t0 = ref.transform
    cov = np.zeros((4, H, W), np.float32); best = np.zeros((H, W), np.float32); bpid = np.zeros((H, W), np.int32)
    for w, pid, c in zip(gw, np.array(f["poly_id"]), np.array(f["class_id"])):
        g = wkb.loads(bytes(w)); x0, y0, x1, y1 = g.bounds
        c0, c1 = max(int(np.floor((x0 - t0.c) / 20)), 0), min(int(np.ceil((x1 - t0.c) / 20)), W)
        r0, r1 = max(int(np.floor((t0.f - y1) / 20)), 0), min(int(np.ceil((t0.f - y0) / 20)), H)
        if r1 <= r0 or c1 <= c0: continue
        t = Affine(20 / ss, 0, t0.c + c0 * 20, 0, -20 / ss, t0.f - r0 * 20)
        m = rasterize([mapping(g)], out_shape=((r1 - r0) * ss, (c1 - c0) * ss), transform=t, fill=0, default_value=1, dtype="uint8")
        fr = m.reshape(r1 - r0, ss, c1 - c0, ss).mean((1, 3)).astype(np.float32)
        cov[c - 1, r0:r1, c0:c1] += fr
        upd = fr > best[r0:r1, c0:c1]
        best[r0:r1, c0:c1][upd] = fr[upd]; bpid[r0:r1, c0:c1][upd] = pid
    cov = np.minimum(cov, 1); dom = cov.argmax(0) + 1; pur = cov.max(0)
    if verbose:
        print(f"polygon: {len(f['poly_id'])} | ô 20 m được polygon chạm tới: {(pur > 0).sum()}")
        print("Số ô 20 m thuần theo ngưỡng (số polygon đóng góp):")
        for k, n in NAMES.items():
            s = f"  {n:10s}"
            for thr in (0.5, 0.8, 1.0):
                mm = (dom == k) & (pur >= thr); s += f" ≥{thr:.1f}: {mm.sum():6d} ({len(np.unique(bpid[mm]))} poly)"
            print(s)
    rng = np.random.default_rng(seed)
    rows, cols = np.where((pur >= pure) & aoi)
    o = rng.permutation(len(rows)); rows, cols = rows[o], cols[o]
    cnt, keep = {}, []
    for i, p in enumerate(bpid[rows, cols]):
        if cnt.get(p, 0) < cap: cnt[p] = cnt.get(p, 0) + 1; keep.append(i)
    rows, cols = rows[keep], cols[keep]
    return rows, cols, dom[rows, cols], bpid[rows, cols]


def load(verbose=True, **kw):
    """Tiện ích: dựng đặc trưng + mẫu, bỏ mẫu có đặc trưng không hữu hạn."""
    ref = reference(); X, aoi = features(ref)
    rows, cols, y, pid = samples(ref, aoi, verbose=verbose, **kw)
    xs = X[rows, cols]; ok = np.isfinite(xs).all(1)
    return dict(ref=ref, X=X, aoi=aoi, xs=xs[ok], y=y[ok], rows=rows[ok], cols=cols[ok], poly=pid[ok])
