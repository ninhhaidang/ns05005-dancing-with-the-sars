---
title: How to reproduce
description: Step-by-step instructions to rebuild every dataset, map, experiment and figure of the project from the public NISAR data.
sidebar:
  order: 3
---

Everything in this project can be rebuilt from public data with the scripts in the repository. The `data/` folder (about 1 GB) is **not** stored in git; the code, labels (`labeling/*.gpkg`), result tables and figures (`outputs/`) are.

:::note[AOI boundary file]
The province boundary `data/ref/aoi.geojson` (merged Hưng Yên, one MultiPolygon feature in EPSG:4326) is provided by the team and sits inside the git-ignored `data/` folder. Place it there before running any script. See [AOI](/data/aoi/).
:::

## Requirements for reproducing

- **Python environment:** conda environment named `dwts` from conda-forge (Python 3.12). `environment.yml` lists the base packages (rasterio, numpy, h5py, scipy, scikit-learn, matplotlib, pyproj, requests, earthengine-api). The classification and experiments also need **pandas, geopandas, pyogrio, shapely, statsmodels, seaborn, xgboost, lightgbm and catboost** from conda-forge. Versions used: scikit-learn 1.9.1, numpy 2.5.4, XGBoost 3.4.2, LightGBM 4.7.0, CatBoost 1.2.10 (CatBoost 1.2.5 fails with numpy 2.5).
- **No pip in the environment:** install extra packages with `conda install -c conda-forge <package>`.
- **Earthdata Login account** (free, NASA) to download NISAR from ASF.
- **Optional:** a Google Earth Engine account to rebuild the Sentinel-2 composite used for drawing labels.

```bash
conda env create -f environment.yml
conda activate dwts
conda install -c conda-forge pandas geopandas pyogrio shapely statsmodels seaborn xgboost lightgbm catboost
```

## Running conventions

- **Always run Python with `-I`** (isolated mode), from the repository root, for example `python -I scripts/change_detection.py`. Isolated mode ignores user site-packages and the current directory; the scripts add their own folder to `sys.path` themselves so they can import `sar_dataset.py`.
- **Do not run Python from inside the data folders.**
- **Random seeds are fixed (0)**; results can differ very slightly between runs because Random Forest runs in parallel (for example, 1 cell out of 6.4 million in the main map).

## Step 1: download NISAR GCOV from ASF

1. Create an Earthdata Login token and save it in a file `.earthdata_token` at the repository root. **This file is git-ignored; never commit, print or share the token.**
2. Download the three granules listed in `data/manifest.json` (field `url`; the 22 October, 27 October and 3 November 2026 VALIDATED products, CRID P05036) into `data/tmp/`, sending the header `Authorization: Bearer <token>`:

```bash
mkdir -p data/tmp
curl -L -H "Authorization: Bearer $(cat .earthdata_token)" -o data/tmp/<granule>.h5 "<url from manifest.json>"
```

3. Optionally check the SHA-256 of each file against `raw_sha256` in the manifest.

Only the 22 October–3 November 2026 window and VALIDATED products are used. The 29 October granule (track 076) is not needed (it covers 4% of the AOI).

## Step 2: clip to the AOI

```bash
python -I scripts/crop_gcov.py data/tmp/*.h5
```

Reads frequency A of each HDF5, clips it to `data/ref/aoi.geojson` (projected to UTM 48N), writes six GeoTIFF layers per date to `data/nisar/gcov/` and rewrites `data/manifest.json`. The HDF5 files can be deleted afterwards. See [Preprocessing](/methods/preprocessing/).

## Step 3: quick looks and change detection

```bash
python -I scripts/quicklook.py          # outputs/quicklook.png, outputs/change_22oct_3nov.png
python -I scripts/change_detection.py   # data/derived/change_class_22oct_3nov.tif, outputs/change_patches.csv
```

`change_detection.py` prints the speckle-correlation factor f for HH and HV, the area of each change class and the largest patches. See [Change detection](/methods/change-detection/). `scripts/sar_analysis.py` is an earlier exploratory analysis (hotspot and rough thresholds) and is not needed for the final results.

## Step 4: labels (only if you redraw them)

The merged labels `labeling/labels_polygon.gpkg` are in git, so this step is optional.

```bash
python -I scripts/merge_label_polygons.py "<folder with water.shp, vegetation.shp, bareland.shp, building.shp>"
```

The Sentinel-2 background used for drawing comes from `scripts/gee_s2_composite.js` (Earth Engine Code Editor, export to Drive), placed in `data/s2/gee_10m/` and clipped with `python -I scripts/clip_gee_s2.py`. The blind test cells come from `python -I scripts/make_blind_test.py` (refuses to overwrite an existing file).

## Step 5: train the land-cover classifier

```bash
python -I scripts/train_classifier.py
```

Builds the 12 features and the pure-cell samples, prints cross-validation results (5 km blocks and by polygon) and writes `data/derived/landcover_sar_20m.tif`, `data/derived/samples_polygon_20m.csv` and `outputs/landcover_sar.png`. See [Classification](/methods/classification/).

## Step 6: run the experiments and draw the figures

```bash
python -I scripts/experiments.py            # E0–E8, about 35 minutes on an 8-core machine
python -I scripts/experiments.py --only E1,E4   # a subset
python -I scripts/plot_experiments.py       # all figures in vi/ and en/, English tables in en/tables/ (about 1 minute)
```

Outputs: CSV tables and `log.txt` in `outputs/experiments/`, figures and reports in `outputs/experiments/vi/` and `outputs/experiments/en/`, plus `data/derived/landcover_model_mode.tif`, `landcover_model_agreement.tif` and `aoa_dissimilarity.tif`. E8 needs the Sentinel-2 composite in `data/s2/gee_10m/` (to split clear and cloudy areas).

## Step 7 (optional): evaluate on the blind test set

After filling the `label` column of `labeling/blind_test_cells.gpkg` (1 Water, 2 Vegetation, 3 Bare land, 4 Built-up, 0 mixed/unclear):

```bash
python -I scripts/eval_blind.py
```

This has **not** been done in the project; see [Validation](/methods/validation/).

## Script reference

| Group | Script | What it does |
|---|---|---|
| SAR | `crop_gcov.py` | Clip GCOV HDF5 frequency A to the AOI, write GeoTIFF layers and the manifest |
| SAR | `quicklook.py` | Quick-look images in dB and raw 22 Oct → 3 Nov difference |
| SAR | `sar_analysis.py` | Early exploratory analysis (hotspot, rough thresholds) |
| SAR | `change_detection.py` | Statistical change detection 22 Oct → 3 Nov |
| Sentinel-2 | `gee_s2_composite.js` | Earth Engine median composite with Cloud Score+ |
| Sentinel-2 | `check_gee_s2.py`, `clip_gee_s2.py` | Check and clip the Earth Engine composite |
| Sentinel-2 | `s2_scl_coverage.py`, `s2_composite.py` | Older AWS-based coverage check and composite (superseded) |
| Labels | `merge_label_polygons.py` | Merge the four class shapefiles into one GeoPackage |
| Labels | `make_blind_test.py`, `eval_blind.py` | Create and evaluate the blind test set |
| Classification | `sar_dataset.py` | Shared module: features and samples |
| Classification | `train_classifier.py` | Main Random Forest model and map |
| Classification | `experiments.py` | Experiments E0–E8 (tables only) |
| Classification | `plot_experiments.py` | Bilingual figures and English tables |
