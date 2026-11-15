---
title: Sentinel-2 optical imagery
description: How the cloud-masked Sentinel-2 composite was built, how much of the AOI it covers, and why it is used only for drawing labels.
sidebar:
  order: 3
---

Sentinel-2 (ESA's optical satellites, 10–20 m resolution) is used in this project **only as a visual reference for drawing the training labels**. It is **not** an input to the land-cover model or to the change detection. Everything the model sees comes from NISAR radar, so the map can be applied to cloudy areas where Sentinel-2 sees nothing.

## Sentinel-2 composite used for labelling (Google Earth Engine, 10 m)

- **File:** `data/s2/gee_10m/S2_composite_10m_aoi.tif` (clipped to the AOI; the unclipped export is kept next to it).
- **Built with:** `scripts/gee_s2_composite.js`, run in the Google Earth Engine Code Editor.
- **Collection:** `COPERNICUS/S2_SR_HARMONIZED` (surface reflectance), dates 22 October to 3 November 2026 inclusive.
- **Cloud masking:** Google Cloud Score+ (`GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED`), band `cs_cdf`, pixels kept when cs_cdf ≥ **0.789** (higher = stricter).
- **Compositing:** per-pixel **median** of all clear observations.
- **Bands (6):** B2 (blue), B3 (green), B4 (red), B8 (near infrared), B11 (shortwave infrared 1.6 µm), and `n_clear` (number of clear observations per pixel).
- **Grid:** 10 m, UTM 48N (EPSG:32648), same projection as the NISAR data; 8,002 × 8,346 pixels after clipping; int16; nodata = 0; deflate compression with internal overviews.
- **True-colour display:** red = band 3 (B4), green = band 2 (B3), blue = band 1 (B2).
- **Reflectance scale:** reflectance = DN × 0.0001. Do **not** subtract an extra 0.1 offset: the harmonized collection already has the offset applied. An earlier mistake of subtracting it again produced negative reflectances and a wrong NDVI report.

## Sentinel-2 clear-sky coverage in the study window

- **Only about 32% of the AOI** has at least one clear observation (`n_clear` > 0) between 22 October and 3 November 2026. About 68% of the province has no usable optical view at all in this window.
- **No single clear date:** the best individual date covered only about 24% of the AOI.
- **Older AWS composite (not used):** an earlier composite built from Earth Search (AWS) Sentinel-2 L2A with the Scene Classification Layer (classes 4, 5, 6 = vegetation, bare soil, water) covered 51.7% of the AOI (`data/s2/composite_20m.tif`, 20 m on the SAR grid). However, the extra area it considered clear shows signs of thin cloud: median blue reflectance (B2) of 1129 (×10⁻⁴) there versus 900 where both sources agree the sky is clear. The Earth Engine composite with Cloud Score+ is therefore preferred.
- **Do not use:** `data/s2/composite_20m_uint16_sai.tif` is a known-bad file (wrong data type) and must be ignored.

## Why Sentinel-2 is not a model input

1. **Coverage:** with only ~32% clear coverage, a model needing optical inputs could map at most a third of the province.
2. **Independence:** keeping optical data out of the model makes the result a test of what SAR alone can do, which is the goal of the challenge.
3. **Representativeness checked:** although labels could only be drawn where Sentinel-2 was clear, the [area-of-applicability analysis](/methods/validation/) shows that cloudy and clear parts of the AOI are equally well represented in SAR feature space (8.3% versus 8.4% outside the area of applicability).

## Dynamic World (not used)

Google's Dynamic World land-cover product (derived from Sentinel-2) covers only **6.2% of the AOI** within 22 October–3 November 2026, so it was not used as labels or as a comparison.

## Sentinel-2 related scripts

| Script | Purpose |
|---|---|
| `scripts/gee_s2_composite.js` | Earth Engine script that builds and exports the 10 m composite |
| `scripts/check_gee_s2.py` | Checks the exported file and compares it with the older AWS composite |
| `scripts/clip_gee_s2.py` | Clips the composite to the AOI, builds overviews, writes `aoi_32648.geojson` |
| `scripts/s2_scl_coverage.py`, `scripts/s2_composite.py` | Older AWS (Earth Search) coverage check and 20 m composite (superseded) |

The figure below shows the **older AWS composite** (superseded; white = no clear pixel) and its NDVI. It illustrates how much of the province is hidden by clouds even after combining 12 days of images; the Earth Engine composite actually used for labelling covers less (about 32%) but is cleaner.

![Older AWS Sentinel-2 clear-pixel composite (left) and NDVI (right); white areas have no clear observation](/figures/common/s2_composite.png)
