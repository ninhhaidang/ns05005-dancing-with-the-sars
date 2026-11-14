---
title: Validation design
description: How the accuracy of the SAR-only land-cover classifier was measured, what the 93% balanced accuracy means and what it does not mean.
sidebar:
  order: 4
---

This page explains how the land-cover classifier was evaluated: the metric, the spatial cross-validation, the uncertainty estimates, the area-of-applicability analysis, and the honest limits of all of it. The detailed numbers of every experiment are in the [Experiments section](/experiments/); the code is `scripts/experiments.py`.

:::caution[What "93%" means]
The headline figure, **balanced accuracy ≈ 93%** (Random Forest 93.1%, SVM 93.6%), is measured by **5 km spatial-block cross-validation on pure 20 m cells** inside the hand-drawn label polygons. It is **not** the accuracy of the whole map. Mixed cells and areas far from labels are certainly less accurate, and **map-level accuracy is unknown** because the independent blind test set was never labelled.
:::

## Primary metric: balanced accuracy (BA)

- **Definition:** balanced accuracy is the mean of the recall (producer's accuracy) of the four classes: BA = (recall_Water + recall_Vegetation + recall_BareLand + recall_BuiltUp) / 4.
- **Why BA and not overall accuracy:** Water makes up 51% of the 3,918 training samples, so overall accuracy (OA) is inflated by easy water cells. BA weights each class equally. A model that always predicts the majority class gets OA 51.3% but BA only 25%.
- **Fixed in advance:** BA under 5 km spatial-block CV was chosen as the primary metric before running the experiments, to avoid picking the most flattering number afterwards.
- **Secondary metrics:** overall accuracy, macro F1, Cohen's kappa, per-class F1 and confusion matrices.

## Spatial-block cross-validation (5 km blocks)

- **Problem:** the labels are spatially clustered (the median distance to the nearest same-class polygon is only 102 m) and neighbouring 20 m cells have almost identical features, partly because features are smoothed over 60–140 m. A random split would test the model on cells right next to training cells, which inflates accuracy (**spatial leakage**).
- **Solution:** the AOI grid is divided into **5 km × 5 km blocks** (250 × 250 cells). All samples in one block go to the same fold, so test cells are usually far from training cells (median distance 1,686 m).
- **Folds and repeats:** 5 folds with scikit-learn `StratifiedGroupKFold` (groups = blocks, class proportions balanced between folds), **repeated 5 times** with different random block-to-fold assignments. All models are evaluated on exactly the same folds.
- **Number of blocks:** the 3,918 samples fall into 88 blocks.

## Uncertainty: block bootstrap confidence intervals

- **95% confidence intervals** for BA are computed by a **block bootstrap**: the 5 km blocks are resampled with replacement 2,000 times and BA is recomputed on the out-of-fold predictions each time. Resampling blocks rather than cells respects spatial correlation.
- **Model differences:** the difference in BA between each model and Random Forest is computed on the same bootstrap samples, giving a confidence interval for the difference.
- **McNemar's test** is also reported, but its p-values are optimistic because neighbouring cells are not independent.
- **Example:** Random Forest BA 93.1% (95% CI 90.5–95.0%); SVM 93.6% (91.4–95.8%).

## How the validation design changes the answer

Experiment E4 compared several ways of splitting train and test data (Random Forest BA):

| Split | Median test-to-train distance | BA |
|---|---|---|
| Random by cell (leaky) | 20 m | 95.9% |
| By polygon | 300 m | 94.1% |
| 5 km blocks (primary) | 1,686 m | 93.1% |
| 5 km blocks + 1 km buffer | 2,500 m | 92.8% |
| 20 km blocks | 4,099 m | 91.4% |
| West / East halves | 18.7 km | 87.0% |
| North / South halves | 17.9 km | 83.8% |

- **Leakage is real:** the random per-cell split is about 3 points too optimistic; even a per-polygon split is about 1 point optimistic.
- **Buffers barely matter:** removing training cells within 250 m or 1 km of test cells changes BA by at most 0.3 points, so feature smoothing does not leak across block borders.
- **Region splits drop a lot (83–87%),** partly because classes are unevenly distributed: Built-up has 618 samples in the north and only 7 in the south, so a model trained on the south hardly knows Built-up.

## Accuracy versus distance from labels

- **Measured on CV test cells (Random Forest, 5 km blocks):** BA is 98–100% for test cells less than 500 m from training cells, 93.7% at 500 m–2 km, and 90.7% at 2–5 km.
- **Distance of the whole AOI to the nearest training sample:** 12% of AOI cells are within 500 m, 44% at 0.5–2 km, 32% at 2–5 km and 12% at 5–10 km. So **about 44% of the AOI is more than 2 km from any label**, where the measured accuracy on pure cells is only about 90%.

## Area of applicability (AOA) and dissimilarity index (DI)

The area of applicability (Meyer & Pebesma, 2021) marks where the model is asked to predict for SAR feature values unlike anything in its training data.

1. **Weighted feature space:** each of the 12 features is standardised (mean 0, standard deviation 1 over the training samples) and multiplied by its permutation importance from experiment E3.
2. **Dissimilarity index:** for each AOI cell, DI = (distance to the nearest training sample in this space) / (mean pairwise distance between training samples, estimated on 3,000 random samples).
3. **Threshold:** DI is also computed for CV test samples against their own training folds (5 km blocks). The threshold is the upper whisker of that distribution, Q3 + 1.5 × IQR = **0.105**. Cells with DI > 0.105 are **outside the AOA**.
4. **Output:** `data/derived/aoa_dissimilarity.tif` (float32 DI per cell; the threshold is stored as a tag).

**AOA results:**
- **8.3% of the AOI is outside the AOA.** The share is the same where Sentinel-2 was clear (8.4%) and where it was cloudy (8.3%), and the median DI is equal (0.048). Drawing labels only in cloud-free areas therefore did not make the training data unrepresentative of cloudy areas in SAR feature space.
- **By predicted class:** 23.5% of cells predicted as Built-up are outside the AOA, versus 4.5–4.9% for Water and Bare land and 0.7% for Vegetation. **Built-up is the least reliable class.**
- **Limit:** DI measures similarity to the training data, not correctness. In CV, BA by DI quartile (lowest to highest) is 86.7%, 94.2%, 91.1%, 83.6%, so accuracy does not fall steadily with DI.

## Model agreement as a confidence layer

Ten different models (Random Forest, Extra Trees, gradient boosting variants, MLP, logistic regression, LDA, QDA) were trained on all samples and applied to the whole AOI. All 10 agree on **65.9% of the AOI**; only 3.0% of cells have 5 or fewer models agreeing with the majority. The per-cell agreement count (`data/derived/landcover_model_agreement.tif`, values 3–10) is shown as a confidence layer on the [map](/?view=confidence). High agreement does not prove correctness: all models learn from the same labels and share the same biases.

## Blind test set: prepared but not used

- **250 random 20 m cells** (`labeling/blind_test_cells.gpkg`) were selected by simple random sampling in cloud-free areas, at least 200 m from training polygons and 200 m from each other, without looking at the predictions. See [Labels](/data/labels/).
- **Not labelled:** the team decided not to label them, so `scripts/eval_blind.py` has not been run on real labels.
- **Consequence:** there is **no independent, design-based accuracy estimate** and **no bias-corrected area estimate** (the good-practice method of Olofsson et al., 2014 would need such a probability sample).

## Summary of what is and is not validated

| Claim | Status |
|---|---|
| BA ≈ 93% on pure cells, 5 km block CV | Measured |
| Model choice barely matters; three dates and both polarisations matter | Measured (cross-validation) |
| Accuracy of the full map, including mixed cells | **Unknown** |
| Area shares (Built-up ≈ 24%, Bare land ≈ 44%) | **Not validated, not bias-corrected** |
| Built-up class reliability | Weakest class (23.5% outside AOA) |

**References:** Meyer, H. & Pebesma, E. (2021). Predicting into unknown space? Estimating the area of applicability of spatial prediction models. *Methods in Ecology and Evolution*, 12, 1620–1633. Olofsson, P. et al. (2014). Good practices for estimating area and assessing accuracy of land change. *Remote Sensing of Environment*, 148, 42–57.
