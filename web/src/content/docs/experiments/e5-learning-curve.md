---
title: "E5: Learning curve"
description: Training on growing fractions of the label polygons shows that balanced accuracy nearly saturates after about 300 polygons.
sidebar:
  order: 5
---

**Question.** Would drawing more label polygons improve the SAR land-cover classifier?

**Short answer.** Not much, if they are of the same kind. Balanced accuracy (BA) rises quickly up to about 300 polygons and then flattens: 92.2% with 40% of the polygons, 93.2% with all of them.

## E5 setup

- **Model:** Random Forest, 5 km spatial-block CV, 3 repeats × 5 folds.
- **Method:** in each fold, keep a random fraction (5% to 100%) of the *training polygons* (all cells of a kept polygon are kept), train, and score on the full test fold. Fractions that would leave a class with no sample are skipped.
- **± values** are the standard deviation across the 15 fold runs.

## E5 results

![E5: learning curve, balanced accuracy versus number of training polygons](/figures/en/E5_learning_curve.png)

| Share of training polygons | 5% | 10% | 20% | 40% | 60% | 80% | 100% |
|---|---|---|---|---|---|---|---|
| Polygons (mean per fold) | 35 | 69 | 139 | 277 | 416 | 555 | 694 |
| BA (%) | 86.4 ± 5.7 | 87.7 ± 5.1 | 91.0 ± 3.0 | 92.2 ± 1.6 | 92.5 ± 1.9 | 92.8 ± 1.6 | 93.2 ± 1.5 |

At 100%, a training fold contains about 694 of the 864 sample-producing polygons (the rest are in the test fold).

## E5: interpretation

- **The curve nearly saturates after about 300 polygons.** Going from 40% to 100% of the polygons adds only 1 BA point.
- **Variance falls with more polygons** (±5.7 at 5%, ±1.5 at 100%): small label sets give unstable results depending on which polygons are drawn.
- **What could still help is diversity, not volume:** labels in under-sampled regions (Built-up in the south has only 7 samples, see [E4](/experiments/e4-validation/)), and labels on hard cells such as mixed village/tree cells and freshly harvested fields.
- Remember that the test cells are pure cells near labelled areas; the curve says nothing about mixed cells.
