---
title: Change detection method
description: The statistical log-ratio test with speckle-correlation correction used to find significant backscatter changes between 22 October and 3 November 2026.
sidebar:
  order: 2
---

The change detection compares the two NISAR acquisitions taken from the **same orbit track** (track 148, descending): **22 October 2026** and **3 November 2026**, 12 days apart. Same track means same viewing geometry, so a backscatter difference reflects something that changed on the ground. The goal is to find water-management changes (fields, ponds or embanked areas being flooded or drained) while keeping false alarms from radar speckle very rare. Code: `scripts/change_detection.py`.

## Idea: a z-test on the log-ratio of two radar images

Radar intensity is noisy because of **speckle**: even if nothing changes, two images of the same field differ randomly. Averaging *L* independent looks reduces this noise. Under the standard model, multilooked intensity follows a **Gamma distribution with L looks**, and the logarithm of the ratio of two independent images has a known variance:

- log-ratio: **r = ln(Ī₂ / Ī₁)**, where Ī₁ and Ī₂ are the window-averaged intensities on 22 October and 3 November (linear power).
- theoretical standard deviation: **σ = √( ψ₁(L₁) + ψ₁(L₂) )**, where ψ₁ is the trigamma function and L₁, L₂ are the effective numbers of looks of the two windows.
- test statistic: **z = r / (f · σ)**, where f is a correction factor for speckle correlation (below).

A large negative z means backscatter dropped significantly; a large positive z means it rose. The change in dB, used for interpretation, is 10·log10(Ī₂/Ī₁).

## Step by step: windows, effective looks, correction factor

1. **Valid cells:** a 20 m cell is used only if HH is finite on both dates and `numberOfLooks` > 0 on both dates.
2. **Window averaging:** for each cell, intensities are averaged over a **5 × 5 window** (100 m × 100 m), using only valid cells. This is done separately for HH and HV and for each date, in linear power.
3. **Effective looks:** L for each date is the **sum of `numberOfLooks` over the valid cells in the window** (about 25 × 8.95 ≈ 224 looks for a full window). This assumes the looks of neighbouring pixels are independent, which is not exactly true.
4. **Speckle-correlation correction f:** because neighbouring pixels are correlated, the real spread of r is larger than σ predicts. The script measures it robustly over the whole AOI: **f = 1.4826 · MAD(r) / median(σ)**, where MAD is the median absolute deviation (1.4826·MAD estimates a standard deviation when most cells are unchanged). The fitted values are **f ≈ 1.6–1.7** (f = 1 would mean independent pixels). Dividing by f·σ makes z behave like a standard normal variable in unchanged areas.
5. **Threshold:** a polarisation changes significantly when **|z| > 5**. For a standard normal variable, |z| > 5 happens by chance about once in 1.7 million cells, so random speckle almost never passes.

## Change classes and decision rules

Each valid cell gets one class, using z for HH (z_HH) and HV (z_HV):

| Class | Name | Rule |
|---|---|---|
| 1 | No significant change | none of the rules below |
| 2 | **New water / surface became smooth** | z_HH < −5 and z_HV < −5, and HH on 3 November < −15 dB |
| 3 | Decrease in HH and HV (other) | z_HH < −5 and z_HV < −5, and HH on 3 November ≥ −15 dB |
| 4 | Increase in HH and HV | z_HH > 5 and z_HV > 5 |
| 5 | HV decrease only | \|z_HV\| > 5, z_HV < 0, and \|z_HH\| ≤ 5 |
| 6 | HV increase only | \|z_HV\| > 5, z_HV > 0, and \|z_HH\| ≤ 5 |

- **Both polarisations must agree** for classes 2–4, which further suppresses false alarms.
- **The −15 dB rule for class 2:** calm open water reflects radar away from the sensor (specular reflection), so it is dark in HH, typically below −15 dB. A significant drop that ends below −15 dB is therefore labelled "new water / smoothing". This threshold is a heuristic, not calibrated on labelled change data.
- **Minimum patch size:** connected patches of classes 2–6 smaller than **125 cells (0.05 km² = 5 ha)** are reset to class 1. Small single ponds are therefore not reported.

## Outputs of the change detection

- **Raster:** `data/derived/change_class_22oct_3nov.tif` (uint8, 20 m, 0 = outside AOI, 1–6 = classes above).
- **Patch table:** `outputs/change_patches.csv`, one row per patch: class, area (km²), centroid longitude/latitude, mean HH on 22 October and 3 November (dB).
- **Figure:** `outputs/change_detection.png`.

## Change detection results in numbers

| Class | Area | Share of AOI | Patches |
|---|---|---|---|
| 1 No significant change | 2,569.0 km² | 99.89% | — |
| 2 New water / smoothing | 1.58 km² | 0.061% | 5 |
| 3 Decrease HH and HV (other) | 0.38 km² | 0.015% | 5 |
| 4 Increase HH and HV | 0.58 km² | 0.023% | 7 |
| 5 HV decrease only | 0 km² | 0% | 0 |
| 6 HV increase only | 0.16 km² | 0.006% | 2 |

- **Main finding:** all 5 "new water" patches (total 1.58 km²; the largest 0.71 km² and 0.62 km²) lie together in one cluster around **106.47–106.49°E, 20.46–20.48°N**, next to a stretch of river in the south-east of the province. Four of the five class-3 patches are in the same cluster. In this cluster HH fell from about −10 to −16 dB and HV from about −17 to −23 dB, and the decrease had already started on 27 October (seen in the ascending image). The block has a rectangular shape.
- **Interpretation (hypothesis):** a field, pond or embanked area was filled with water between 22 October and 3 November. **This is not verified**: there was no clear optical image to confirm it.
- **Increase patches (class 4)** are small (0.05–0.13 km²) and scattered, mostly in the north-west of the province (around 106.05–106.10°E, 20.73–20.85°N) and near 106.30°E, 20.56°N. Their causes were not investigated.
- **No rice-harvest signal:** no widespread change pattern consistent with harvesting was found in these 12 days; most rice appears to have been harvested before 22 October.

![Significant changes 22 October → 3 November](/figures/common/change_detection.png)

![HH and HV difference 3 November minus 22 October, in dB](/figures/common/change_22oct_3nov.png)

See the [change view of the interactive map](/map/?view=change) and [Change results](/results/change/).

## Limitations of the change detection

- **Only two dates, 12 days apart:** changes before 22 October or after 3 November are invisible.
- **27 October not used in the test:** it is from a different orbit and look direction, so its backscatter is not directly comparable; it is only used as supporting evidence.
- **Strict thresholds:** |z| > 5, agreement of HH and HV, and a 5 ha minimum patch size favour very few false alarms at the cost of missing small or subtle changes.
- **Global correction factor:** f is estimated once for the whole AOI; local differences in speckle correlation are not modelled.
- **Water threshold is a heuristic:** wind-roughened water can be brighter than −15 dB, and very smooth surfaces (for example wet bare soil) can be darker.
- **Physical cause unverified** for every detected patch.
