---
title: Land-cover map from SAR only
description: A four-class land-cover map of Hưng Yên at 20 m produced from three NISAR dates alone, with its area shares, confidence layers and the caveats needed to read it.
sidebar:
  order: 2
---

This page presents the land-cover map of Hưng Yên province (post-2025 boundary, 2,571.7 km²) produced **only from NISAR SAR**, without any optical input. Because SAR sees through clouds, the map covers the whole province, including the roughly 69% that had no clear Sentinel-2 view between 22 Oct and 3 Nov 2026. Open it on the [interactive map, land-cover view](/map/?view=landcover).

:::caution[Accuracy and areas are not validated]
The often-quoted **≈93% is balanced accuracy on pure 20 m cells under 5 km spatial-block cross-validation, not the accuracy of this map.** There is no independent test set (a 250-cell blind set was prepared but not labelled). **Area shares below are pixel counts, not validated and not bias-corrected.**
:::

## Land-cover classes

| Class | Meaning in this project | Typical L-band signature |
|---|---|---|
| 1 Water | Rivers, ponds, aquaculture, flooded fields | Very dark in HH and HV (smooth surface, specular reflection) |
| 2 Vegetation | Crops, trees, orchards, grass | Relatively bright HV (volume scattering) |
| 3 Bare land | Harvested or ploughed fields, bare soil | Moderate HH, darker HV |
| 4 Built-up | Dense buildings, towns, villages | Very bright HH (double-bounce from walls and ground) |

Labels were drawn as rectangles on a Sentinel-2 composite (see [Labels](/data/labels/)); the "Built-up" labels are dense building blocks.

## How the land-cover map was produced

- **Input:** 12 features per 20 m cell from NISAR GCOV (VALIDATED) on 22 Oct, 27 Oct and 3 Nov 2026: HH and HV per date, means, HV − HH, temporal standard deviations and texture. See [Classification method](/methods/classification/).
- **Model:** Random Forest (300 trees, `min_samples_leaf=2`, balanced class weights) trained on all 3,918 pure-cell samples from 864 label polygons.
- **Why Random Forest:** the [E1 model comparison](/experiments/e1-models/) found 11 models within 1 point of each other; Random Forest is robust, fast and was kept.

## Land-cover area shares (unvalidated)

| Class | Random Forest map, km² | Random Forest map, % of AOI | Consensus of 10 models, % of AOI |
|---|---|---|---|
| Water | 130.5 | 5.1% | 5.6% |
| Vegetation | 646.3 | 25.1% | 26.8% |
| Bare land | 1,174.5 | 45.7% | 43.6% |
| Built-up | 620.4 | 24.1% | 24.0% |

Areas are counts of 20 m cells (400 m² each) on the raw Random Forest map; the consensus column is the majority vote of 10 models from [E7](/experiments/e7-map-agreement/). Across those 10 models the shares range: Water 5.0–6.3%, Vegetation 22.6–33.2%, Bare land 38.7–46.5%, Built-up 15.7–25.9%.

**Reading these numbers.** The shares are stable across models, but all models learn from the same labels. A Built-up share near 24% looks high for an agricultural delta province. A plausible but unchecked explanation is that villages with trees and gardens are mapped as Built-up. A large Bare-land share is consistent with many rice fields having been harvested before 22 Oct (see [Rice harvest](/results/rice-harvest/)), but this has not been verified either.

![SAR-only land-cover map (raw Random Forest output)](/figures/common/landcover_sar.png)

## How accurate is the land-cover classifier?

What *has* been measured, on pure cells only:

- **Balanced accuracy ≈93%** (Random Forest 93.1%), overall accuracy ≈95%, kappa ≈0.93 under 5 km spatial-block CV ([E1](/experiments/e1-models/)).
- **Per-class F1 (Random Forest):** Water 99.5%, Vegetation 88.1%, Bare land 89.6%, Built-up 95.1%. The main confusion is Vegetation ↔ Bare land (6–9% each way).
- **Accuracy drops with distance from labels:** about 90% at 2–5 km, and 44% of the province is more than 2 km from any label ([E4](/experiments/e4-validation/)).
- **Not measured:** mixed cells (villages with trees, small ponds, fields with houses), which make up a large part of the real landscape; accuracy there is certainly lower.

## Confidence layers on the web map

Two layers show where the land-cover map is more or less trustworthy ([open the confidence view](/map/?view=confidence)):

- **Model agreement ([E7](/experiments/e7-map-agreement/)):** the number of 10 different models that predict the majority class. All 10 agree on 65.9% of the AOI; 5 or fewer on 3.0%.
- **Area of applicability ([E8](/experiments/e8-applicability/)):** cells whose SAR signature is far from every training sample (dissimilarity index > 0.105). 8.3% of the AOI is outside, equally in clear and cloudy areas.

## Built-up is the least reliable class

- **23.5% of the cells predicted as Built-up are outside the area of applicability**, versus 0.7% for Vegetation and 4.5–4.9% for Water and Bare land ([E8](/experiments/e8-applicability/)).
- **Built-up labels are almost all in the north:** 618 of 625 Built-up samples are in the northern half, 7 in the southern half ([E4](/experiments/e4-validation/)).
- **Built-up has the widest spread between models** (15.7–25.9% of the AOI).
- These Built-up cells outside the area of applicability concentrate in the north and have **not been checked against a base map.**

## Post-processing on the web map

The web map displays a **3×3 majority-filtered** version of the Random Forest map: each cell takes the most frequent class among itself and its 8 neighbours. This reduces the salt-and-pepper noise typical of per-pixel classification. **Its effect on accuracy has not been measured**, and area shares of the filtered map may differ slightly from the table above, which is computed on the raw map.

## Land-cover limitations in short

No independent validation; pure-cell accuracy only; clustered and regionally uneven labels; area shares not bias-corrected; Built-up definition may differ between labels and map; labels drawn on a 12-day median composite while the ground was changing (harvest). Full list: [Limitations](/limitations/).
