---
title: NISAR GCOV data
description: The three NISAR L-band GCOV VALIDATED acquisitions over Hưng Yên used by the project, their layers, grids and quirks.
sidebar:
  order: 1
---

The project's only model input is radar backscatter from **NISAR**, the joint NASA–ISRO Synthetic Aperture Radar mission. We use the Level-2 **GCOV** product (Geocoded polarimetric COVariance) at maturity level **VALIDATED**, processing version (CRID) **P05036**, frequency **A** of the L-band radar. VALIDATED GCOV products became available from 21 October 2026.

## Acquisitions used

| Date (2026) | Orbit track | Direction | Pixel size | AOI coverage | Used? |
|---|---|---|---|---|---|
| 22 October | 148 | Descending | 20 m | 100% | Yes |
| 27 October | 054 | Ascending | 10 m | 100% | Yes |
| 3 November | 148 | Descending | 20 m | 100% | Yes |
| 29 October | 076 | Descending | — | 4% | No (too little coverage) |

- **Same-track pair for change detection:** 22 October and 3 November are on the same track (148, descending), 12 days apart. Same geometry means a backscatter difference reflects a change on the ground, not a change in viewing angle. These two dates are used for [change detection](/methods/change-detection/).
- **Different look direction on 27 October:** the 27 October image comes from an ascending pass (track 054), so the radar looks at the ground from the opposite side. It adds information for [classification](/methods/classification/) (buildings and slopes scatter differently depending on look direction) but it is not used in the 22 October → 3 November change test.
- **Time window rule:** the project only uses data from 22 October to 3 November 2026. No PROVISIONAL products and no older data are used.

Full product identifiers (example for 22 October): `NISAR_L2_PR_GCOV_033_148_D_078_2005_DHDH_A_20261022T112852_20261022T112927_P05036_N_F_J_001`. The 27 October product is `..._034_054_A_012_4005_DHDH_A_20261027T222209_...` and the 3 November product is `..._034_148_D_078_2005_DHDH_A_20261103T112853_...`. The descending passes are around 11:29 UTC (about 18:29 local time) and the ascending pass around 22:22 UTC (about 05:22 local time the next morning). The source URLs and SHA-256 checksums of the original HDF5 files are recorded in `data/manifest.json`.

## Layers in each NISAR GCOV file

For each date, frequency A of the GCOV HDF5 was clipped to the AOI and written as six GeoTIFF layers (see [Preprocessing](/methods/preprocessing/)):

| Layer | Meaning | Data type, nodata |
|---|---|---|
| `HHHH` | HH backscatter power (horizontal transmit, horizontal receive), linear scale | float32, NaN |
| `HVHV` | HV backscatter power (horizontal transmit, vertical receive; cross-polarised), linear scale | float32, NaN |
| `numberOfLooks` | Number of looks averaged into each pixel (controls speckle strength) | float32, NaN |
| `rtcGammaToSigmaFactor` | Factor that converts the terrain-corrected γ⁰ (gamma-naught) values to σ⁰ (sigma-naught) | float32, NaN |
| `mask` | Validity mask; inside the AOI all pixels have value 1, outside 255 | uint8, 255 |
| `inputDataExceptionMask` | Flags for problems in the input data | uint16, 65535 |

- **Units:** values are linear power. Convert to decibels with dB = 10·log10(value). All thresholds in this project (for example −15 dB) are in dB.
- **Which backscatter convention:** the project uses the HHHH and HVHV values exactly as stored in GCOV (terrain-corrected γ⁰). The `rtcGammaToSigmaFactor` layer is kept but not applied; over this flat delta its median is about −1.07 dB on the descending track and −1.17 dB on the ascending track.
- **Typical values over the AOI (5th / 50th / 95th percentile, dB):** HH on 22 October −15.2 / −8.2 / 0.0; HV on 22 October −22.1 / −15.1 / −8.5. The other dates are within about 1 dB of these.
- **Number of looks:** median about 8.95 looks per 20 m pixel on the descending dates and about 4.64 looks per 10 m pixel on 27 October.
- **Frequency B** (coarser, about 80 m over this area) exists in the files but is not used.

## Grid and coverage of the NISAR rasters

- **Coordinate system:** UTM zone 48N (EPSG:32648), the native projection of the GCOV grid over Hưng Yên; no resampling was needed for clipping.
- **20 m dates (22 October, 3 November):** 4,001 × 4,174 pixels, bounds x 592,920–672,940 m, y 2,239,820–2,323,300 m. Inside the AOI: 6,429,330 valid pixels (2,571.7 km²).
- **10 m date (27 October):** 8,002 × 8,346 pixels over the same extent. For classification it is averaged to the 20 m grid (each 20 m cell = mean of 2 × 2 pixels of linear power).
- **Valid-data footprint:** the valid pixels of all three dates coincide exactly with the AOI rasterised in UTM. Pixels outside the province boundary are nodata.

## Data quality notes for NISAR GCOV

- **VALIDATED is not "perfect":** VALIDATED means the product passed the mission's calibration/validation stage, but NISAR documents known issues for early products. We did not apply any extra radiometric correction.
- **Speckle:** each pixel is noisy because of speckle (random interference of echoes). The project reduces it by averaging (3 × 3 smoothing for classification; 5 × 5 windows with a statistical model for change detection).
- **Original HDF5 files were deleted** after clipping to save space. They can be re-downloaded from the URLs in `data/manifest.json` (see [Reproduce](/reproduce/)).

## Viewing the NISAR images

The [SAR view of the interactive map](/?view=sar) shows each date as a false-colour composite. You can switch dates with the slider, e.g. [22 October](/?view=sar&date=2026-10-22), [27 October](/?view=sar&date=2026-10-27), [3 November](/?view=sar&date=2026-11-03).

![Quicklook of HH and HV in dB for the three dates](/figures/common/quicklook.png)
