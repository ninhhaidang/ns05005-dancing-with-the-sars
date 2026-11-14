"""Cắt tần số A của GCOV HDF5 theo AOI, ghi GeoTIFF + manifest.

Dùng:  python -I scripts/crop_gcov.py data/tmp/*.h5
- Cửa sổ = bbox của AOI (UTM 48N); pixel ngoài AOI được gán nodata.
- Không xóa file HDF5 gốc.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

import h5py
import numpy as np
import rasterio
import rasterio.features as rf
from pyproj import Transformer
from rasterio.transform import from_origin
from shapely.geometry import shape
from shapely import transform as shp_transform

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "nisar" / "gcov"
AOI = ROOT / "data" / "ref" / "aoi.geojson"
MANIFEST = ROOT / "data" / "manifest.json"
BASE = "https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GCOV_V1"
LAYERS = {  # tên lớp -> (dtype, nodata)
    "HHHH": (np.float32, np.nan),
    "HVHV": (np.float32, np.nan),
    "numberOfLooks": (np.float32, np.nan),
    "rtcGammaToSigmaFactor": (np.float32, np.nan),
    "mask": (np.uint8, 255),
    "inputDataExceptionMask": (np.uint16, 65535),
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def main(files):
    geom = shape(json.load(open(AOI))["features"][0]["geometry"])
    to_utm = Transformer.from_crs(4326, 32648, always_xy=True)
    aoi = shp_transform(geom, lambda c: np.column_stack(to_utm.transform(c[:, 0], c[:, 1])))
    x0, y0, x1, y1 = aoi.bounds
    OUT.mkdir(parents=True, exist_ok=True)
    items = []
    for f in map(Path, files):
        gid = f.stem
        date = re.search(r"_(\d{8})T\d{6}_\d{8}T", gid).group(1)
        date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
        digest = sha256(f)
        with h5py.File(f, "r") as h:
            a = h["science/LSAR/GCOV/grids/frequencyA"]
            assert int(a["projection"][()]) == 32648
            x, y = a["xCoordinates"][:], a["yCoordinates"][:]
            dx, dy = float(a["xCoordinateSpacing"][()]), abs(float(a["yCoordinateSpacing"][()]))
            left, top = x[0] - dx / 2, y[0] + dy / 2
            c0, c1 = max(0, int((x0 - left) // dx)), min(len(x), int(np.ceil((x1 - left) / dx)))
            r0, r1 = max(0, int((top - y1) // dy)), min(len(y), int(np.ceil((top - y0) / dy)))
            tr = from_origin(left + c0 * dx, top - r0 * dy, dx, dy)
            inside = rf.geometry_mask([aoi], out_shape=(r1 - r0, c1 - c0), transform=tr, invert=True)
            print(f"{date} {gid[-60:]} {r1-r0}x{c1-c0} px {dx:g} m, AOI px {inside.sum()}", flush=True)
            for name, (dtype, nodata) in LAYERS.items():
                arr = a[name][r0:r1, c0:c1].astype(dtype)
                arr[~inside] = nodata
                path = OUT / f"{gid}__frequencyA__{name}.tif"
                with rasterio.open(path, "w", driver="GTiff", height=arr.shape[0], width=arr.shape[1],
                                   count=1, dtype=arr.dtype, crs="EPSG:32648", transform=tr,
                                   nodata=nodata, compress="deflate", tiled=True,
                                   predictor=3 if dtype == np.float32 else 2) as dst:
                    dst.write(arr, 1)
                    dst.update_tags(source=gid, layer=name, date=date, maturity="VALIDATED", crid="P05036")
                items.append({
                    "id": f"{gid}__GCOV_grids_frequencyA__{name}",
                    "path": str(path.relative_to(ROOT)),
                    "url": f"{BASE}/{gid}/{gid}.h5",
                    "raw_sha256": digest,
                    "note": "AOI cut from the original HDF5 (VALIDATED, CRID P05036); outside-AOI pixels = nodata",
                    "sensor": "sar", "date": date, "source": "ASF", "product": "GCOV",
                    "maturity": "VALIDATED", "pixel_m": dx, "item_id": gid,
                })
    json.dump({"items": items}, open(MANIFEST, "w"), ensure_ascii=False, indent=1)
    print(f"{len(items)} layers -> {OUT}; manifest -> {MANIFEST}")


if __name__ == "__main__":
    main(sys.argv[1:])
