---
title: Preprocessing
description: How the NISAR GCOV HDF5 files are downloaded, clipped to the AOI, converted to dB, resampled to a common 20 m grid and smoothed.
sidebar:
  order: 1
---

Preprocessing turns three large NISAR GCOV HDF5 files into small, aligned GeoTIFF layers on one 20 m grid covering exactly the Hưng Yên AOI. It is deliberately minimal: no extra calibration, no speckle filter other than simple averaging, and no use of optical data.

## Step 1: download NISAR GCOV from ASF

- **Source:** the Alaska Satellite Facility (ASF) DAAC, `https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GCOV_V1/<granule>/<granule>.h5`.
- **Authentication:** an Earthdata Login token sent as an HTTP header `Authorization: Bearer <token>`. The token is stored locally in `.earthdata_token`, which is git-ignored and never committed or printed.
- **Products:** three VALIDATED granules (CRID P05036): 22 October, 27 October and 3 November 2026. The exact URLs and SHA-256 checksums are in `data/manifest.json`. See [NISAR data](/data/nisar/).

## Step 2: clip frequency A to the AOI (`scripts/crop_gcov.py`)

Usage: `python -I scripts/crop_gcov.py data/tmp/*.h5`

1. **Project the AOI:** the AOI polygon (EPSG:4326) is transformed to UTM 48N (EPSG:32648), the projection of the GCOV grid (the script asserts that the HDF5 projection is 32648).
2. **Window:** from the HDF5 coordinate arrays (`xCoordinates`, `yCoordinates`, pixel spacing) the script computes the pixel window covering the AOI bounding box, so only that window is read.
3. **Mask outside the AOI:** pixels outside the polygon are set to nodata (NaN for float layers, 255 for `mask`, 65535 for `inputDataExceptionMask`).
4. **Write GeoTIFF:** six layers per date from `science/LSAR/GCOV/grids/frequencyA`: `HHHH`, `HVHV`, `numberOfLooks`, `rtcGammaToSigmaFactor`, `mask`, `inputDataExceptionMask`. Files are tiled and deflate-compressed, and tagged with source granule, layer, date, maturity VALIDATED and CRID P05036.
5. **Manifest:** `data/manifest.json` records, for every layer, the output path, source URL, SHA-256 of the original HDF5, date, product, maturity and pixel size.

- **Output folder:** `data/nisar/gcov/` (about 391 MB for the three dates).
- **Original HDF5 files** are not deleted by the script; in this project they were removed manually afterwards to save space and can be downloaded again.

## Step 3: convert NISAR backscatter to decibels

- GCOV stores backscatter as **linear power** (terrain-corrected γ⁰). The project converts to decibels with **dB = 10 · log10(power)**, setting values ≤ 0 to NaN first.
- The γ⁰ → σ⁰ conversion factor (`rtcGammaToSigmaFactor`) is **not** applied; all analysis uses γ⁰ as delivered.
- **Where averaging happens in linear power:** the 10 m → 20 m resampling and the change-detection windows average linear power (averaging dB values would bias the mean downward). The 3 × 3 smoothing of classification features (Step 5) is applied to dB values.

## Step 4: put all dates on one 20 m grid

- **Reference grid:** the 22 October HH layer: 4,001 × 4,174 pixels of 20 m, UTM 48N.
- **22 October and 3 November** are already on this grid (same track, same grid) and need no resampling.
- **27 October (10 m, ascending)** is resampled to the reference grid with `rasterio.warp.reproject` using **average** resampling on linear power, so each 20 m cell is the mean of four 10 m pixels.
- **AOI mask:** cells where the 22 October HH value is finite define the AOI (6,429,330 cells = 2,571.7 km²).

## Step 5: speckle reduction by smoothing (for classification)

- **For land-cover features** (`scripts/sar_dataset.py`): each dB layer is smoothed with a **3 × 3 mean filter** (60 m × 60 m). Before filtering, NaN cells are temporarily filled with the image median so the filter does not spread NaN into the AOI edge; cells outside the AOI are later excluded by the AOI mask.
- **For change detection** (`scripts/change_detection.py`): linear power is averaged in **5 × 5 windows** (100 m × 100 m), counting only valid cells, and the number of looks is tracked so that the remaining speckle can be modelled statistically (see [Change detection](/methods/change-detection/)).
- **No advanced speckle filter** (Lee, Refined Lee, etc.) is used. Simple averaging keeps the speckle statistics tractable for the change test (the number of looks in a window is known). No comparison with advanced filters was made.

## Step 6: optical data for labelling only

Sentinel-2 is processed separately (Earth Engine median composite, clipped by `scripts/clip_gee_s2.py`) and is only used as a background image for drawing labels. It never enters the model. See [Sentinel-2](/data/sentinel2/).

## Practical notes on running preprocessing

- Run Python with the conda environment `dwts` and the `-I` (isolated) flag; scripts in `scripts/` add their own folder to `sys.path` because `-I` removes it.
- Do not run Python from inside the data folders.
- `data/` is not stored in git. The NISAR layers and all derived rasters can be regenerated from public data; the AOI boundary `data/ref/aoi.geojson` is a team-provided file that also lives in `data/` and must be obtained separately. See [Reproduce](/reproduce/).
