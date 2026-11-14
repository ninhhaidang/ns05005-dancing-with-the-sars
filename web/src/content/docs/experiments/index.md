---
title: Experiments overview
description: The E0–E8 experiment programme that tests how well a SAR-only land-cover classifier works, how it should be validated, and how reliable the final map is.
sidebar:
  order: 0
---

The land-cover map of this project is produced **from NISAR SAR alone**. Before trusting it, we ran a programme of nine experiments (E0–E8) on the same labels and features. They answer four questions:

1. Does the choice of machine-learning model matter? (E1, E6)
2. Which SAR features carry the information? (E2, E3)
3. How optimistic is a given validation design, and how far from the labels can the model be trusted? (E0, E4, E5)
4. How reliable is the *map*, not just the samples? (E7, E8)

All numbers come from `scripts/experiments.py` (results computed on 14 Nov 2026). Figures are drawn by `scripts/plot_experiments.py`. The method itself is described in [Classification](/methods/classification/) and [Validation](/methods/validation/).

:::caution[How to read every number on these pages]
All accuracy figures are **cross-validation on pure 20 m cells** (cells lying ≥80% inside one label polygon). There is **no independent test set**: a blind set of 250 random cells was prepared but has not been labelled. The headline "≈93%" is **balanced accuracy on pure cells under 5 km spatial-block cross-validation, not the accuracy of the whole map.**
:::

## Experimental setup shared by E0–E8

**Task.** Classify every 20 m cell of Hưng Yên province (6.43 million cells, 2,571.7 km²) into 4 classes: Water, Vegetation, Bare land, Built-up (urban/village).

**Input data.** NISAR L2 GCOV, VALIDATED (CRID P05036), frequency A, HH and HV, three dates: 22 Oct 2026 (track 148 descending, 20 m), 27 Oct 2026 (track 054 ascending, 10 m averaged to 20 m), 3 Nov 2026 (track 148 descending, 20 m). See [NISAR data](/data/nisar/).

**Labels.** 1,347 rectangular polygons drawn on a cloud-masked Sentinel-2 composite: Water 190, Vegetation 485, Bare land 444, Built-up 228. See [Labels](/data/labels/).

**Samples.** A 20 m cell becomes a sample if ≥80% of its area is one class (8×8 supersampling), with at most 20 cells per polygon. Result: **3,918 samples from 864 polygons** (Water 2,011, Vegetation 622, Bare land 660, Built-up 625). 483 polygons (36%) give no sample because they are smaller than one full 20 m cell.

**Features (12 per cell).** HH and HV in dB for each of the 3 dates (smoothed 3×3), mean HH, mean HV, HV − HH, standard deviation of HH and of HV across the 3 dates, and a 7×7 texture (local standard deviation of mean HH).

**Primary metric.** Balanced accuracy (BA, the mean of per-class recall), fixed before running. Water is 51% of the samples, so overall accuracy would be inflated.

**Primary validation.** 5-fold cross-validation by **5×5 km spatial blocks** (`StratifiedGroupKFold`), repeated 5 times with different block-to-fold assignments; 95% confidence intervals by block bootstrap (2,000 resamples). All models share the same folds.

## E0: checking the spatial distribution of labels

E0 is a data check, run before the model experiments, that explains why spatial-block validation is necessary.

- **Labels are clustered by class.** The median distance from a polygon to the nearest *same-class* polygon is **102 m**; to the nearest *other-class* polygon it is **509 m**. Only 1.8% of polygons have an other-class neighbour within 100 m. No polygons touch.
- **Samples are concentrated.** Samples fall in **88 blocks** of 5×5 km (median 21 samples per block, largest 348), but the **10 densest blocks hold 48%** of all samples.
- **Each class is present in only 33–45 blocks:** Water 33, Vegetation 38, Bare land 34, Built-up 45.
- **Folds are balanced:** in the 5 km block CV each test fold holds about 400 Water, 99–182 Vegetation, 130–133 Bare land and 124–126 Built-up samples.

Consequence: a random per-cell or per-polygon split would put test cells right next to same-class training cells, and the effective diversity of the label set is much lower than "3,918 samples" suggests. This is measured directly in [E4](/experiments/e4-validation/).

## Summary of findings

| Experiment | Question | Key result |
|---|---|---|
| [E1 Models](/experiments/e1-models/) | Which of 14 models is best? | 11 of 14 models reach BA 93.0–93.6%; differences are within the uncertainty. SVM 93.6%, Random Forest 93.1%, majority baseline 25%. |
| [E2 Features](/experiments/e2-features/) | Which feature groups matter? | 3 dates 93.1% vs one date 83.4–85.6%. Both HH and HV needed (≈4 points each). Texture adds 0.2 points. |
| [E3 Importance](/experiments/e3-importance/) | Which single features matter? | HV on 27 Oct (the only ascending date) is most important (−6.7 points BA when shuffled), then std of HH (−3.9). |
| [E4 Validation](/experiments/e4-validation/) | How much does the validation design change the score? | Random per-cell split inflates BA by ≈3 points (95.9%). Province halves give 83–87%. 44% of the AOI is >2 km from any label, where BA on pure cells is ≈90%. |
| [E5 Learning curve](/experiments/e5-learning-curve/) | Would more labels help? | BA nearly saturates after ≈300 polygons (92.2% at 40% of polygons, 93.2% at 100%). |
| [E6 Tuning](/experiments/e6-tuning/) | Does hyperparameter tuning help? | At most +0.5 points (SVM 93.6 → 94.1%); RF unchanged. |
| [E7 Map agreement](/experiments/e7-map-agreement/) | Do models produce the same map? | All 10 models agree on 65.9% of the AOI. Area shares stable across models but unvalidated: Built-up ≈24%, Bare land ≈44%. |
| [E8 Applicability](/experiments/e8-applicability/) | Where is the model extrapolating? | 8.3% of the AOI is outside the area of applicability, equally in clear and cloudy areas. 23.5% of Built-up predictions are outside it. |

## Overall conclusions from the experiments

- **SAR-only four-class mapping is feasible** with multi-temporal NISAR L-band: BA ≈93% on pure cells under spatial-block validation, robust to model choice, tuning and buffering.
- **Data, not model complexity, is what matters:** three dates and both polarisations bring 7–10 points; changing the model brings less than 1 point.
- **Reliability is uneven across the map:** accuracy decreases with distance from labelled areas, and the Built-up class is the least reliable. The web map therefore shows confidence layers ([open the confidence view](/map/?view=confidence)).

## Reproducing the experiments

```bash
python -I scripts/experiments.py            # all experiments E0–E8, about 35 minutes on an 8-core machine
python -I scripts/experiments.py --only E1,E4   # a subset
python -I scripts/plot_experiments.py en    # figures and English tables
```

Random seeds are fixed (0); repeated runs can differ very slightly because Random Forest runs in parallel. Full instructions: [Reproduce](/reproduce/).
