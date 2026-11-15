"""Dựng dữ liệu cho web (data/web/, không commit; đồng bộ lên server bằng deploy/sync.sh).

Ra:
  tiles/<lớp>/{z}/{x}/{y}.(webp|png)   tile XYZ WebMercator (gdal raster tile)
  pixel_stack.tif                       COG int16 nhiều băng cho API tra cứu điểm (/api/pixel)
  aoi.geojson, change_patches.geojson, labels.geojson (EPSG:4326)
  meta.json                             thông tin lớp, chú giải, thống kê
Cần chạy trước: change_detection.py, train_classifier.py, experiments.py (lớp đồng thuận, AOA), postprocess_landcover.py.
Chạy: /Users/ninhhaidang/miniconda3/envs/dwts/bin/python -I scripts/build_web.py [--only sar,landcover,...] [--skip-tiles]
"""
import argparse, glob, json, shutil, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I bỏ thư mục script khỏi sys.path
import numpy as np, rasterio, geopandas as gpd, pandas as pd
from rasterio.features import shapes
from scipy import ndimage as ndi
from shapely.geometry import shape
from pyproj import Transformer
from sar_dataset import ROOT, DATES, reference, features

OUT, TMP = ROOT / "data/web", ROOT / "data/tmp/web"
GDAL = str(Path(sys.executable).parent / "gdal")
DER = ROOT / "data/derived"
LC = {1: ("Water", "Nước", "#2b6cb0"), 2: ("Vegetation", "Thực vật", "#68a03f"),
      3: ("Bare soil", "Đất trống", "#d6b370"), 4: ("Built-up", "Đô thị/làng", "#c0392b")}
CHG = {1: ("No significant change", "Không đổi đáng kể", None),
       2: ("New water / flattening (HH & HV down, HH ends < −15 dB)", "Nước mới / mặt phẳng hóa (HH, HV giảm, HH cuối < −15 dB)", "#1f4ed8"),
       3: ("HH & HV decrease (other)", "HH, HV giảm (khác)", "#f59e0b"),
       4: ("HH & HV increase", "HH, HV tăng", "#dc2626"),
       5: ("HV-only decrease", "Chỉ HV giảm", "#7c3aed"),
       6: ("HV-only increase", "Chỉ HV tăng", "#10b981")}
# Lớp phân loại (ô 20 m, nearest) cắt tới z16 (~2,4 m/px): cắt ở z13 (~18 m/px, sát độ phân giải gốc) thì phép chiếu UTM → WebMercator
# làm ô bị nhân đôi/mất không đều, phóng to trên web thấy bậc thang vỡ. Cùng giá trị CAT_MAXZ ở web/src/components/map/MapApp.tsx.
CAT_MAXZ = 16
# Sentinel-2 (bilinear, WEBP): cắt ở z14 thì phóng to bị nhòe, bạc màu (WEBP giảm độ phân giải màu một nửa). z15 giữ được ô 10 m.
IMG_MAXZ = 15
# SAR: hiển thị nearest (mỗi ô 20 m/10 m là một ô vuông đúng giá trị gốc, như QGIS), overview lấy trung bình.
# Phải cắt tới z16 (~2,4 m/px) để các ô đều nhau, như CAT_MAXZ. Cùng giá trị ở MapApp.tsx.
SAR_MAXZ = 16
DLABEL = {"20261022": "2026-10-22", "20261027": "2026-10-27", "20261103": "2026-11-03"}


def hexrgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def write_rgba(path, rgba, ref):
    prof = ref.profile.copy()
    prof.update(driver="GTiff", count=4, dtype="uint8", nodata=None, compress="deflate", tiled=True, blockxsize=256, blockysize=256)
    with rasterio.open(path, "w", **prof) as d:
        d.write(rgba)
        d.colorinterp = [rasterio.enums.ColorInterp.red, rasterio.enums.ColorInterp.green, rasterio.enums.ColorInterp.blue, rasterio.enums.ColorInterp.alpha]


def palette_rgba(cls, colors):
    rgba = np.zeros((4,) + cls.shape, np.uint8)
    for k, h in colors.items():
        if h is None: continue
        m = cls == k; r, g, b = hexrgb(h)
        rgba[0][m], rgba[1][m], rgba[2][m], rgba[3][m] = r, g, b, 255
    return rgba


def stretch(x, lo, hi, gamma=1.0):
    y = np.clip((x - lo) / (hi - lo), 0, 1) ** gamma
    return np.nan_to_num(y * 255).astype(np.uint8)


# Mã phiên bản từng lớp tile, ghi vào meta.json["tile_versions"]. Web gắn ?v=<mã> vào URL tile nên cắt lại tile là
# trình duyệt và Cloudflare lấy bản mới ngay (tile được lưu bộ đệm lâu dài, xem deploy/Caddyfile).
TILE_VERSIONS = {}


def tile(name, src, maxz, fmt="PNG", resampling="nearest", overview=None):
    TILE_VERSIONS[name] = time.strftime("%Y%m%d%H%M%S")
    dst = OUT / "tiles" / name
    shutil.rmtree(dst, ignore_errors=True); dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [GDAL, "raster", "tile", "-q", "--of", fmt, "--min-zoom", "8", "--max-zoom", str(maxz), "-r", resampling,
           "--overview-resampling", overview or ("nearest" if resampling == "nearest" else "average"), "--skip-blank", "--webviewer", "none",
           str(src), str(dst)]
    if fmt == "WEBP": cmd[-2:-2] = ["--co", "QUALITY=85"]
    subprocess.run(cmd, check=True)
    n = sum(1 for _ in dst.rglob("*.*") if _.suffix in (".png", ".webp"))
    mb = sum(p.stat().st_size for p in dst.rglob("*") if p.is_file()) / 1e6
    print(f"  tiles/{name}: z8-{maxz}, {n} tile, {mb:.1f} MB")


def sar_path(d, p): return glob.glob(str(ROOT / f"data/nisar/gcov/*_{d}T*__frequencyA__{p}.tif"))[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="sar,s2,landcover,agreement,aoa,change,labels,pixel,meta")
    ap.add_argument("--skip-tiles", action="store_true")
    a = ap.parse_args(); only = set(a.only.split(","))
    OUT.mkdir(parents=True, exist_ok=True); TMP.mkdir(parents=True, exist_ok=True)
    ref = reference(); aoi = np.isfinite(ref.read(1))
    to_ll = Transformer.from_crs(ref.crs, 4326, always_xy=True)
    meta_path = OUT / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}

    # --- SAR màu giả: R = HH, G = HV, B = HH − HV (dB), cùng một dải kéo giãn cho cả 3 ngày ---
    if "sar" in only:
        print("SAR màu giả")
        db = lambda x: 10 * np.log10(np.where(x > 0, x, np.nan))
        with rasterio.open(sar_path(DATES[0], "HHHH")) as s: hh0 = db(s.read(1))
        with rasterio.open(sar_path(DATES[0], "HVHV")) as s: hv0 = db(s.read(1))
        rng = {"HH": np.nanpercentile(hh0, [2, 98]).round(1).tolist(), "HV": np.nanpercentile(hv0, [2, 98]).round(1).tolist(),
               "ratio": np.nanpercentile(hh0 - hv0, [2, 98]).round(1).tolist()}
        print("  dải kéo giãn (dB, phân vị 2-98 ngày 22/10):", rng)
        for d in DATES:
            with rasterio.open(sar_path(d, "HHHH")) as s, rasterio.open(sar_path(d, "HVHV")) as v:
                hh, hv, sref = db(s.read(1)), db(v.read(1)), s
                ok = np.isfinite(hh) & np.isfinite(hv)
                rgba = np.stack([stretch(hh, *rng["HH"]), stretch(hv, *rng["HV"]), stretch(hh - hv, *rng["ratio"]),
                                 np.where(ok, 255, 0).astype(np.uint8)])
                rgba[:3, ~ok] = 0
                p = TMP / f"sar_{d}.tif"; write_rgba(p, rgba, sref)
            if not a.skip_tiles: tile(f"sar_{d}", p, SAR_MAXZ, "WEBP", "nearest", "average")
        meta["sar_stretch_db"] = rng

    # --- Sentinel-2 màu thật (GEE, chỉ để tham khảo; phản xạ = DN × 1e-4, không trừ 0,1) ---
    if "s2" in only:
        print("Sentinel-2 màu thật")
        with rasterio.open(ROOT / "data/s2/gee_10m/S2_composite_10m_aoi.tif") as s:
            b = s.read().astype(np.float32); sref = s
            ok = b[5] > 0
            rgb = [stretch(b[i] * 1e-4, 0.0, 0.25, 0.8) for i in (2, 1, 0)]
            rgba = np.stack(rgb + [np.where(ok, 255, 0).astype(np.uint8)])
            p = TMP / "s2_truecolor.tif"; write_rgba(p, rgba, sref)
        if not a.skip_tiles: tile("s2_truecolor", p, IMG_MAXZ, "WEBP", "bilinear")
        meta["s2_clear_fraction"] = round(float(ok.sum() / np.isfinite(rasterio.open(sar_path(DATES[1], "HHHH")).read(1)).sum()), 3)

    # --- Lớp phủ (đã lọc đa số) ---
    if "landcover" in only:
        print("Lớp phủ")
        lc = rasterio.open(DER / "landcover_sar_20m_smooth.tif").read(1)
        p = TMP / "landcover.tif"; write_rgba(p, palette_rgba(lc, {k: v[2] for k, v in LC.items()}), ref)
        if not a.skip_tiles: tile("landcover", p, CAT_MAXZ)

    # --- Mức đồng thuận giữa 10 mô hình (E7) ---
    if "agreement" in only:
        print("Mức đồng thuận")
        ag = rasterio.open(DER / "landcover_model_agreement.tif").read(1)
        ramp = {3: "#b2182b", 4: "#b2182b", 5: "#d6604d", 6: "#f4a582", 7: "#fddbc7", 8: "#92c5de", 9: "#4393c3", 10: "#2166ac"}
        p = TMP / "agreement.tif"; write_rgba(p, palette_rgba(ag, ramp), ref)
        if not a.skip_tiles: tile("agreement", p, CAT_MAXZ)
        meta["agreement_ramp"] = ramp

    # --- Ngoài vùng áp dụng (E8): tô gạch chéo xám ---
    if "aoa" in only:
        print("Vùng áp dụng")
        with rasterio.open(DER / "aoa_dissimilarity.tif") as s:
            di, thr = s.read(1), float(s.tags()["aoa_threshold"])
        out = np.isfinite(di) & (di > thr)
        rr, cc = np.indices(di.shape); hatch = ((rr + cc) % 6) < 2
        rgba = np.zeros((4,) + di.shape, np.uint8)
        rgba[0][out], rgba[1][out], rgba[2][out] = 40, 40, 40
        rgba[3][out] = np.where(hatch[out], 200, 70)
        p = TMP / "aoa.tif"; write_rgba(p, rgba, ref)
        if not a.skip_tiles: tile("aoa", p, CAT_MAXZ)
        meta["aoa"] = {"threshold": round(thr, 4), "outside_fraction": round(float(out.sum() / aoi.sum()), 4)}

    # --- Thay đổi 22/10 → 3/11: tile + polygon có thuộc tính ---
    if "change" in only:
        print("Thay đổi")
        ch = rasterio.open(DER / "change_class_22oct_3nov.tif").read(1)
        p = TMP / "change.tif"; write_rgba(p, palette_rgba(ch, {k: v[2] for k, v in CHG.items()}), ref)
        if not a.skip_tiles: tile("change", p, CAT_MAXZ)
        X, _ = features(ref)
        recs = []
        for c in range(2, 7):
            lab, n = ndi.label(ch == c)
            for i in range(1, n + 1):
                m = lab == i
                geom = [shape(g) for g, v in shapes(m.astype(np.uint8), mask=m, transform=ref.transform) if v == 1]
                poly = gpd.GeoSeries(geom, crs=ref.crs).union_all()
                r, cc = ndi.center_of_mass(m); x, y = ref.xy(r, cc); lon, lat = to_ll.transform(x, y)
                rec = dict(cls=c, name_en=CHG[c][0], name_vi=CHG[c][1], color=CHG[c][2], area_km2=round(m.sum() * 400 / 1e6, 3),
                           lon=round(lon, 5), lat=round(lat, 5), geometry=poly)
                for j, d in enumerate(DATES):
                    rec[f"HH_{DLABEL[d]}"] = round(float(np.nanmean(X[..., j][m])), 2)
                    rec[f"HV_{DLABEL[d]}"] = round(float(np.nanmean(X[..., 3 + j][m])), 2)
                recs.append(rec)
        g = gpd.GeoDataFrame(recs, crs=ref.crs).sort_values("area_km2", ascending=False).reset_index(drop=True)
        g.insert(0, "id", np.arange(1, len(g) + 1))
        g = g.to_crs(4326); g["geometry"] = g.geometry.simplify(0.00005)
        (OUT / "change_patches.geojson").write_text(g.to_json(drop_id=True))
        tot = aoi.sum()
        meta["change"] = {"classes": {str(k): {"en": v[0], "vi": v[1], "color": v[2], "area_km2": round(float((ch == k).sum() * 400 / 1e6), 2),
                                               "pct": round(float((ch == k).sum() / tot * 100), 3)} for k, v in CHG.items()},
                          "patches": len(g), "test": "z > 5 on HH and HV log-ratio, 5x5 window, patches >= 0.05 km2"}
        print(f"  {len(g)} mảng thay đổi")

    # --- Nhãn polygon và AOI ---
    if "labels" in only:
        print("Nhãn và AOI")
        lab = gpd.read_file(ROOT / "labeling/labels_polygon.gpkg").to_crs(4326)
        lab["color"] = lab["class_id"].map(lambda k: LC[int(k)][2])
        lab[["poly_id", "class_id", "class_name", "color", "geometry"]].to_file(OUT / "labels.geojson", driver="GeoJSON")
        gpd.read_file(ROOT / "data/ref/aoi.geojson").to_crs(4326).to_file(OUT / "aoi.geojson", driver="GeoJSON")

    # --- Chồng băng tra cứu điểm (int16, 20 m) ---
    if "pixel" in only:
        print("pixel_stack.tif")
        X, _ = features(ref)
        lc_s = rasterio.open(DER / "landcover_sar_20m_smooth.tif").read(1)
        lc_r = rasterio.open(DER / "landcover_sar_20m.tif").read(1)
        ag = rasterio.open(DER / "landcover_model_agreement.tif").read(1)
        md = rasterio.open(DER / "landcover_model_mode.tif").read(1)
        ch = rasterio.open(DER / "change_class_22oct_3nov.tif").read(1)
        di = rasterio.open(DER / "aoa_dissimilarity.tif").read(1)
        nd = -32768
        q = lambda x, s: np.where(aoi & np.isfinite(x), np.round(x * s), nd).astype(np.int16)
        bands = [("landcover", q(lc_s.astype(float), 1)), ("landcover_raw", q(lc_r.astype(float), 1)), ("model_mode", q(md.astype(float), 1)),
                 ("agreement", q(ag.astype(float), 1)), ("change", q(ch.astype(float), 1)), ("aoa_di_x1000", q(di, 1000))]
        bands += [(f"HH_{DLABEL[d]}_dBx100", q(X[..., j], 100)) for j, d in enumerate(DATES)]
        bands += [(f"HV_{DLABEL[d]}_dBx100", q(X[..., 3 + j], 100)) for j, d in enumerate(DATES)]
        prof = ref.profile.copy()
        prof.update(driver="GTiff", count=len(bands), dtype="int16", nodata=nd, compress="deflate", predictor=2, tiled=True,
                    blockxsize=256, blockysize=256, interleave="pixel")
        with rasterio.open(OUT / "pixel_stack.tif", "w", **prof) as d:
            for i, (n, b) in enumerate(bands, 1): d.write(b, i); d.set_band_description(i, n)
        meta["pixel_bands"] = [n for n, _ in bands]
        print(f"  {(OUT / 'pixel_stack.tif').stat().st_size / 1e6:.0f} MB")

    if "meta" in only:
        b = ref.bounds; xs, ys = to_ll.transform([b.left, b.right, b.left, b.right], [b.bottom, b.bottom, b.top, b.top])
        lc_s = rasterio.open(DER / "landcover_sar_20m_smooth.tif").read(1); tot = aoi.sum()
        meta.update({
            "bounds": [round(min(xs), 4), round(min(ys), 4), round(max(xs), 4), round(max(ys), 4)],
            "dates": [DLABEL[d] for d in DATES],
            "sar": {DLABEL[d]: {"track": t, "res_m": r, "pass": ps} for d, t, r, ps in
                    [("20261022", 148, 20, "descending"), ("20261027", 54, 10, "ascending"), ("20261103", 148, 20, "descending")]},
            "landcover": {str(k): {"en": v[0], "vi": v[1], "color": v[2], "area_km2": round(float((lc_s == k).sum() * 400 / 1e6), 1),
                                   "pct": round(float((lc_s == k).sum() / tot * 100), 1)} for k, v in LC.items()},
            "aoi_km2_grid": round(float(tot * 400 / 1e6), 1),
            "new_water_cluster": {"lon": 106.484, "lat": 20.463, "area_km2": 1.6},
        })

    # Luôn ghi meta.json (kể cả khi chỉ chạy --only sar,...) để mã phiên bản tile mới tới được web.
    meta.setdefault("tile_versions", {}).update(TILE_VERSIONS)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    print("meta.json xong")


if __name__ == "__main__":
    main()
