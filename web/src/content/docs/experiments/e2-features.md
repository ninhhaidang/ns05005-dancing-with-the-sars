---
title: "E2: Which feature groups matter"
description: Feature ablation with Random Forest shows that three dates and both HH and HV polarisations drive accuracy, while texture adds almost nothing.
sidebar:
  order: 2
---

**Question.** Which groups of SAR features does the land-cover classifier actually need?

**Short answer.** Multi-temporal data matter most: three dates give 93.1% balanced accuracy (BA) versus 83.4–85.6% for a single date. Both polarisations are needed (dropping HH or HV costs about 4 points). Texture contributes only 0.2 points.

## E2 setup

- **Model:** Random Forest (300 trees, `min_samples_leaf=2`, balanced class weights), the production model.
- **Validation:** 5 km spatial-block CV, 5 repeats (same folds as [E1](/experiments/e1-models/)).
- **Method:** retrain with a subset of the 12 features and compare BA. The ± values are the standard deviation over the 5 repeats.

## E2 results

![E2: balanced accuracy for each feature subset](/figures/en/E2_ablation.png)

| Feature set | Number of features | BA (%) | F1 Water | F1 Vegetation | F1 Bare land | F1 Built-up |
|---|---|---|---|---|---|---|
| All 12 features | 12 | **93.1 ± 0.1** | 99.5 | 88.1 | 89.6 | 95.1 |
| Without texture | 11 | 92.9 ± 0.1 | 99.3 | 88.3 | 88.7 | 95.1 |
| Without temporal standard deviation | 10 | 92.0 ± 0.2 | 99.4 | 86.1 | 87.3 | 94.8 |
| HV only (3 dates + mean HV + std of HV) | 5 | 89.4 ± 0.1 | 99.4 | 80.9 | 88.3 | 88.6 |
| HH only (3 dates + mean HH + std of HH + texture) | 6 | 88.9 ± 0.1 | 97.8 | 82.9 | 81.0 | 93.0 |
| Two descending dates (22 Oct, 3 Nov) | 4 | 87.0 ± 0.1 | 98.2 | 78.0 | 81.9 | 89.1 |
| Means only (mean HH, mean HV, HV − HH) | 3 | 86.9 ± 0.2 | 97.8 | 77.1 | 78.9 | 91.8 |
| Single date 22 Oct (HH, HV, HV − HH) | 3 | 85.6 ± 0.1 | 97.4 | 76.2 | 78.7 | 88.5 |
| Single date 27 Oct, ascending | 3 | 85.6 ± 0.1 | 97.7 | 75.5 | 78.6 | 88.9 |
| Single date 3 Nov | 3 | 83.4 ± 0.1 | 95.9 | 75.5 | 73.5 | 85.7 |

## E2: interpretation

- **Multi-temporal data matter most.** Three dates beat one date by 7–10 BA points. Part of the gain is simply more observations (speckle averages out); part is the **second look direction**: the two descending dates together reach only 87.0%, while adding the ascending 27 Oct acquisition brings the full 93.1%.
- **Both polarisations are needed.** HV only (89.4%) or HH only (88.9%) each lose about 4 points. HV (cross-polarisation, sensitive to volume scattering from vegetation) separates Vegetation and Bare land better; HH (sensitive to surface and double-bounce scattering) helps most with Built-up.
- **Temporal variability helps a little** (−1.1 points without the standard deviation features), but note that it mixes real change with look-direction differences, because 27 Oct is ascending and the other dates are descending.
- **Texture is almost useless** (−0.2 points) at 20 m with this label set and could be dropped.
- **Water is easy in every configuration** (F1 ≥ 95.9%); the differences between feature sets come from Vegetation, Bare land and Built-up.

## E2 conclusion

What makes SAR-only classification work here is **NISAR's repeat acquisitions from more than one geometry, in both HH and HV**, not a sophisticated model ([E1](/experiments/e1-models/)) or texture. This supports using NISAR's frequent revisits for land-cover mapping under persistent cloud. Single-feature importance is examined in [E3](/experiments/e3-importance/).
