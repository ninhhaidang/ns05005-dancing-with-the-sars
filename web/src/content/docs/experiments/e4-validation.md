---
title: "E4: Validation design and spatial leakage"
description: The same model scored under twelve train/test splits shows how random splits inflate accuracy, how accuracy falls with distance from labels, and why 93% is not map accuracy.
sidebar:
  order: 4
---

**Question.** How much does the way we split training and test data change the reported accuracy, and how far from the labelled areas can the land-cover model be trusted?

**Short answer.** A random per-cell split inflates balanced accuracy (BA) by about 3 points (95.9% vs 93.1% for Random Forest). Larger spatial blocks lower BA slowly (91.4% with 20 km blocks). Splitting the province in halves drops BA to 83–87%, partly because labels are unevenly distributed. 44% of the AOI lies more than 2 km from any label, where BA on pure cells is about 90%.

## E4 setup

- **Data and features:** the same 3,918 pure samples and 12 SAR features as in [E1](/experiments/e1-models/).
- **Models:** Random Forest (production), LightGBM, SVM (RBF), logistic regression.
- **Splits compared:** random by cell, by polygon, spatial blocks of 1, 2, 5, 10 and 20 km, 5 km blocks with a 250 m or 1 km buffer, and three region splits (West/East, North/South, 4 quadrants).
- **Buffer:** training cells closer than the buffer distance to the nearest test cell are removed. This blocks leakage through the 3×3 smoothing (60 m) and 7×7 texture (140 m) windows at block boundaries.
- **Distance:** for each test cell, the distance to the nearest training cell; the table reports its median.

## E4 results by validation scheme

![E4: balanced accuracy for each validation scheme](/figures/en/E4_validation_schemes.png)

| Train/test split | Median test → train distance | Random Forest | LightGBM | SVM | Logistic regression |
|---|---|---|---|---|---|
| Random by cell (leaky) | 20 m | 95.9 | 96.8 | 96.2 | 94.5 |
| By polygon | 300 m | 94.1 | 94.4 | 94.4 | 93.5 |
| 1 km blocks | 501 m | 94.2 | 94.6 | 94.4 | 93.6 |
| 2 km blocks | 800 m | 93.4 | 93.6 | 93.9 | 93.3 |
| **5 km blocks (primary)** | 1,686 m | **93.1** | 92.9 | 93.6 | 93.3 |
| 5 km blocks + 250 m buffer | 1,920 m | 93.1 | 93.2 | 93.6 | 93.4 |
| 5 km blocks + 1 km buffer | 2,500 m | 92.8 | 93.0 | 93.4 | 92.8 |
| 10 km blocks | 2,925 m | 92.3 | 92.4 | 93.4 | 91.5 |
| 20 km blocks | 4,099 m | 91.4 | 92.3 | 93.2 | 91.4 |
| West / East halves | 18.7 km | 87.0 | 86.2 | 83.0 | 86.1 |
| North / South halves | 17.9 km | 83.8 | 82.9 | 85.7 | 86.5 |
| 4 quadrants | 15.0 km | 90.4 | 91.3 | 92.4 | 90.5 |

All values are BA in %.

## E4: spatial leakage

- **Random per-cell splits are optimistic.** Test cells are only 20 m from training cells of the same polygon, so the model is effectively tested on near-copies of its training data. BA is about 3 points higher than with 5 km blocks.
- **Per-polygon splits are still about 1 point optimistic,** because same-class polygons were drawn in clusters (median 102 m to the nearest same-class polygon, see [E0 in the overview](/experiments/#e0-checking-the-spatial-distribution-of-labels)).
- **The smoothed features do not leak across block boundaries in a meaningful way:** adding a 250 m buffer, larger than the 140 m texture window, leaves BA unchanged (93.1%).

## E4: accuracy versus block size and region splits

- **BA decreases slowly with block size**, from 93.1% (5 km) to 91.4% (20 km) for Random Forest. SVM is the most stable (93.2% at 20 km).
- **Region splits drop to 83–87%,** but this is confounded with uneven labels:

| Class | West / East samples | North / South samples |
|---|---|---|
| Water | 1,011 / 1,000 | 655 / 1,356 |
| Vegetation | 209 / 413 | 284 / 338 |
| Bare land | 308 / 352 | 402 / 258 |
| Built-up | 431 / 194 | **618 / 7** |

With only 7 Built-up samples in the south, a model trained on the southern half barely learns Built-up. The region-split result therefore measures "a class missing from a region" as well as true transferability between regions.

## E4: accuracy versus distance from the nearest label

BA of Random Forest by distance from each test cell to its nearest training cell:

| Scheme | < 500 m | 500 m – 2 km | 2 – 5 km | > 5 km |
|---|---|---|---|---|
| 5 km blocks | 98–100% (n = 495) | 93.7% (n = 1,715) | 90.7% (n = 1,629) | 96.7% (n = 79) |
| 20 km blocks | 96.7% (n = 161) | 94.1% (n = 846) | 89.7% (n = 1,222) | 90.9% (n = 1,675) |

The >5 km bin under 5 km blocks has only 79 samples and is not reliable.

![E4: balanced accuracy by distance to the nearest training sample](/figures/en/E4_accuracy_by_distance.png)

**How far is the rest of the province from the labels?** Distance from every AOI cell to the nearest training sample (computed separately from `experiments.py`):

| Distance | < 500 m | 0.5 – 2 km | 2 – 5 km | 5 – 10 km |
|---|---|---|---|---|
| Share of AOI cells | 12% | 44% | 32% | 12% |

So **44% of the AOI is more than 2 km from any label.** At those distances, BA measured on pure cells is about 90% (89.7–90.9%), below the 93% of the full cross-validation.

## E4 conclusions

- **Use spatial-block validation.** Random or per-polygon splits overstate accuracy for clustered labels.
- **93% is not map accuracy.** It is measured on pure cells near labelled areas; nearly half of the province is farther away, and mixed cells (villages with trees, small ponds) are not tested at all.
- **More diverse labels, especially Built-up in the south, would help more than more labels of the same kind** (see [E5](/experiments/e5-learning-curve/)). The web map shows where the model extrapolates through the [E8 area-of-applicability layer](/experiments/e8-applicability/).
