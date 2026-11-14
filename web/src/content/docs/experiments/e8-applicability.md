---
title: "E8: Area of applicability"
description: A dissimilarity index in SAR feature space flags the 8.3% of the province where the model extrapolates beyond its training data, including 23.5% of Built-up predictions.
sidebar:
  order: 8
---

**Question.** Where does the land-cover model see SAR signatures unlike anything in its training data, i.e. where is it extrapolating?

**Short answer.** **8.3% of the AOI** is outside the area of applicability (AOA). The share is the same in cloud-free and cloudy areas, so labelling only where Sentinel-2 was clear did not make the samples unrepresentative in SAR feature space. But **23.5% of the cells predicted as Built-up** are outside the AOA, making Built-up the least reliable class.

## E8 method: dissimilarity index (Meyer & Pebesma, 2021)

1. Standardise the 12 SAR features using the training samples, and weight each feature by its permutation importance from [E3](/experiments/e3-importance/) (negative importances set to 0).
2. For each AOI cell, compute the distance in this weighted feature space to the **nearest training sample**, divided by the mean distance between training samples. This is the **dissimilarity index (DI)**.
3. Compute DI for the test samples inside the 5 km spatial-block CV (distance to the training folds only). The **threshold** is the upper whisker of their boxplot (Q3 + 1.5 × IQR) = **0.105**.
4. Cells with DI > 0.105 are **outside the area of applicability**.

## E8 results

![E8: area-of-applicability map and dissimilarity index](/figures/en/E8_area_of_applicability.png)

| Measure | Value |
|---|---|
| DI threshold | 0.105 |
| AOI outside the AOA | **8.3%** |
| … in areas with clear Sentinel-2 (where labels were drawn) | 8.4% |
| … in cloudy areas | 8.3% |
| Median DI, clear vs cloudy areas | 0.048 vs 0.048 |

Share of cells outside the AOA by **predicted class** (Random Forest map):

| Water | Vegetation | Bare land | Built-up |
|---|---|---|---|
| 4.5% | 0.7% | 4.9% | **23.5%** |

## E8: interpretation

- **Cloudy areas are not worse.** About 69% of the province had no clear optical view in the period, and labels could only be drawn in the clear 32%. The AOA analysis shows the SAR signatures of cloudy areas are as well covered by the training data as those of clear areas. This is good news for the core idea of mapping under cloud with SAR.
- **Built-up is the weak class.** Almost a quarter of Built-up predictions have SAR signatures far from any training sample. These cells concentrate in the north of the province. **They have not been checked against a base map**, so the surface type there is unknown.
- **Water and Vegetation are well covered** (4.5% and 0.7% outside).

## E8: limitation of the dissimilarity index

DI measures **similarity to the training data, not correctness.** Within the cross-validation, BA does not decrease steadily with DI:

| DI quartile (test samples) | 0.01–0.03 | 0.03–0.04 | 0.04–0.06 | 0.06–1.01 |
|---|---|---|---|---|
| BA (%) | 86.7 | 94.2 | 91.1 | 83.6 |

The lowest-DI quartile has lower accuracy than the middle ones. One possible reason is that low-DI samples fall in the dense Vegetation/Bare-land overlap zone, where classes are close in feature space; **this has not been checked.** The AOA layer should therefore be read as "the model is extrapolating here", not as a per-pixel error estimate.

## E8 outputs used on the web map

`aoa_dissimilarity.tif` stores DI for every cell (threshold 0.105 in its metadata). On the [interactive map](/?view=confidence), cells outside the AOA are flagged together with the [E7 model agreement](/experiments/e7-map-agreement/) layer.

**Reference.** Meyer, H. & Pebesma, E. (2021). Predicting into unknown space? Estimating the area of applicability of spatial prediction models. *Methods in Ecology and Evolution*, 12, 1620–1633.
