---
title: Land-cover classification method
description: How the SAR-only Random Forest classifier maps Water, Vegetation, Bare land and Built-up at 20 m from 12 NISAR features.
sidebar:
  order: 3
---

The land-cover map assigns every 20 m cell of the Hưng Yên AOI to one of four classes, **Water, Vegetation, Bare land, Built-up**, using **only NISAR radar features** from three dates. Optical data are used only to draw the training labels. The main model is a Random Forest. Code: `scripts/sar_dataset.py` (features and samples), `scripts/train_classifier.py` (main model and map), `scripts/experiments.py` (comparisons).

## Classes of the SAR land-cover map

| Code | Class | Typical radar behaviour (L-band) |
|---|---|---|
| 1 | Water | Very dark in HH and HV: calm water reflects the signal away from the sensor (specular reflection). |
| 2 | Vegetation | Moderate HH, relatively high HV: leaves and stems scatter the signal in many directions (volume scattering), which produces cross-polarised (HV) return. |
| 3 | Bare land | Lower HV than vegetation; HH depends on soil roughness and moisture. |
| 4 | Built-up | Very bright HH: walls and the ground form corner reflectors (double-bounce scattering). Brightness depends on how buildings are oriented relative to the radar look direction. |

Code 0 in the map rasters means outside the AOI.

## The 12 SAR features per 20 m cell

All features are computed on the 20 m grid from HH and HV backscatter in dB, after the 27 October 10 m image has been averaged to 20 m. Each per-date dB layer is smoothed with a 3 × 3 mean filter (60 m) to reduce speckle. See [Preprocessing](/methods/preprocessing/).

| # | Feature | Definition |
|---|---|---|
| 1–3 | HH_1022, HH_1027, HH_1103 | HH (dB, smoothed) on 22 October, 27 October, 3 November |
| 4–6 | HV_1022, HV_1027, HV_1103 | HV (dB, smoothed) on the same three dates |
| 7 | HH mean | Mean of the three HH values (dB) |
| 8 | HV mean | Mean of the three HV values (dB) |
| 9 | HV − HH | Cross-polarisation ratio: HV mean minus HH mean (dB) |
| 10 | std HH | Standard deviation of HH across the three dates (dB) |
| 11 | std HV | Standard deviation of HV across the three dates (dB) |
| 12 | Texture | Local standard deviation of HH mean in a 7 × 7 window (140 m) |

- **Look-direction caveat:** 27 October is an ascending acquisition while the other two are descending. The "standard deviation across dates" features therefore mix real change with look-direction differences (for example, buildings look different from opposite sides).

## Training samples for the classifier

- **Source:** the 1,347 [label polygons](/data/labels/).
- **Pure cells:** a 20 m cell is a sample if ≥ 80% of its area (measured with 8 × 8 supersampling) belongs to one class.
- **Cap:** at most 20 cells per polygon, chosen at random (seed 0).
- **Result:** **3,918 samples** from 864 polygons: Water 2,011, Vegetation 622, Bare land 660, Built-up 625. Samples whose features are not all finite are dropped.

## The Random Forest model

- **Model:** scikit-learn `RandomForestClassifier` with **300 trees**, `min_samples_leaf = 2`, `class_weight = "balanced"` (so the large Water class does not dominate), `random_state = 0`.
- **Why Random Forest:** it is robust and fast (about 0.4 s per fit on ~3,100 samples). In the model comparison, 11 of 14 models reach balanced accuracy 93.0–93.6% under spatial-block cross-validation and none is meaningfully better than Random Forest (93.1%); SVM is highest at 93.6%. Tuning hyperparameters changes results by less than 0.5 points.
- **Final map:** the model is trained on all 3,918 samples and then predicts all 6.43 million AOI cells, in chunks of 1 million cells.
- **Most useful features (permutation importance, experiment E3):** HV on 27 October (balanced accuracy drops 6.7 points when it is shuffled), standard deviation of HH (3.9), HV on 3 November (3.2) and mean HV (2.3); every other feature below 0.5 points.

## What drives accuracy

- **Three dates matter most:** a single date gives balanced accuracy 83–86%; all three dates give 93%. The two descending dates alone give 87.0%, so the different look direction of 27 October adds real information.
- **Both polarisations are needed:** HV only 89.4%, HH only 88.9%, both 93.1%.
- **Texture is almost useless:** removing it costs only 0.2 points.
- **Main confusion:** Vegetation ↔ Bare land (about 6–9% each way), then Built-up predicted as Vegetation (3–5%). Water is almost never confused (about 99% correct).

## Land-cover outputs

| File | Content |
|---|---|
| `data/derived/landcover_sar_20m.tif` | Main Random Forest map (uint8: 0 outside AOI, 1 Water, 2 Vegetation, 3 Bare land, 4 Built-up) |
| `data/derived/landcover_model_mode.tif` | Consensus map: majority class of 10 different models |
| `data/derived/landcover_model_agreement.tif` | How many of the 10 models agree with the majority class (3–10) |
| `data/derived/aoa_dissimilarity.tif` | Dissimilarity index for the area of applicability (threshold 0.105) |
| `data/derived/samples_polygon_20m.csv` | Row, column, class and polygon id of every training sample |
| `outputs/landcover_sar.png` | Quick-look picture of the main map |

## Predicted land-cover areas (not validated)

Shares of the AOI predicted by the main Random Forest map: Water 5.1%, Vegetation 25.1%, Bare land 45.7%, Built-up 24.1%. The 10-model consensus gives Water 5.6%, Vegetation 26.8%, Bare land 43.6%, Built-up 24.0%.

:::caution[These areas are not validated]
The area shares are simple pixel counts, not bias-corrected estimates. A Built-up share of about 24% seems high for an agricultural delta province; one possible explanation is that villages with trees are classified as Built-up while the labels only marked dense buildings. This has not been checked. Built-up is the least reliable class: 23.5% of the cells predicted as Built-up lie outside the model's area of applicability.
:::

![SAR-only land-cover map (Water / Vegetation / Bare land / Built-up)](/figures/common/landcover_sar.png)

See the [land-cover view](/?view=landcover) and the [confidence view](/?view=confidence) of the interactive map, and [Validation](/methods/validation/) for how the 93% was measured.

## Post-processing of the land-cover map

The original Random Forest map is pixel-by-pixel and shows salt-and-pepper noise. The web map uses a version smoothed with a majority (modal) filter to reduce isolated pixels. This smoothing is cosmetic: its effect on accuracy has not been measured.
