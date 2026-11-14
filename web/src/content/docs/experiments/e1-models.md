---
title: "E1: Comparison of 14 models"
description: Fourteen classifiers compared on the same SAR features and the same 5 km spatial-block folds; the top 11 are statistically indistinguishable at about 93% balanced accuracy.
sidebar:
  order: 1
---

**Question.** Does the choice of machine-learning model matter for SAR-only land-cover classification in Hưng Yên?

**Short answer.** No. 11 of 14 models reach balanced accuracy (BA) 93.0–93.6% on pure cells, with overlapping confidence intervals. A plain logistic regression (93.3%) matches tree ensembles. Only LDA and a depth-4 decision tree are clearly worse.

## E1 setup

- **Data:** 3,918 pure 20 m samples, 12 SAR features (see [Experiments overview](/experiments/)).
- **Validation:** 5-fold cross-validation by 5×5 km spatial blocks, repeated 5 times; all models use exactly the same folds.
- **Hyperparameters:** sensible defaults, not tuned on the evaluation folds (tuning is tested separately in [E6](/experiments/e6-tuning/)).
- **Uncertainty:** 95% confidence intervals (CI) by block bootstrap (2,000 resamples of 5 km blocks) on the first repeat. Differences to Random Forest (ΔBA) are computed on the same bootstrap samples.

## E1 results table

![E1: balanced accuracy of 14 models with 95% confidence intervals](/figures/en/E1_models.png)

| Model | BA (95% CI) | OA | Macro F1 | kappa | F1 Water | F1 Vegetation | F1 Bare land | F1 Built-up |
|---|---|---|---|---|---|---|---|---|
| SVM (RBF) | **93.6** (91.4–95.8) | 95.6 | 93.5 | 0.933 | 99.5 | 88.4 | 91.4 | 94.7 |
| Extra Trees | 93.3 (91.1–95.6) | 95.3 | 93.2 | 0.929 | 99.4 | 88.6 | 89.5 | 95.3 |
| CatBoost | 93.3 (91.4–95.6) | 95.3 | 93.1 | 0.929 | 99.5 | 88.1 | 89.6 | 95.3 |
| Logistic regression | 93.3 (91.2–95.4) | 95.3 | 93.2 | 0.929 | 99.3 | 89.1 | 89.8 | 94.8 |
| MLP (64-32) | 93.2 (91.8–95.4) | 95.5 | 93.4 | 0.931 | 99.4 | 89.0 | 90.2 | 94.7 |
| Random Forest | 93.1 (90.5–95.0) | 95.3 | 93.1 | 0.929 | 99.5 | 88.1 | 89.6 | 95.1 |
| Maximum Likelihood (QDA) | 93.1 (91.5–94.4) | 94.6 | 92.7 | 0.918 | 98.4 | 88.9 | 88.1 | 95.3 |
| k-NN (k=15) | 93.1 (91.0–94.8) | 95.3 | 93.3 | 0.929 | 99.2 | 88.8 | 90.1 | 95.1 |
| XGBoost | 93.1 (90.7–95.0) | 95.2 | 93.0 | 0.928 | 99.5 | 87.8 | 89.7 | 94.9 |
| LightGBM | 93.0 (90.5–95.0) | 95.2 | 92.9 | 0.927 | 99.6 | 87.5 | 89.6 | 95.0 |
| HistGradientBoosting | 93.0 (90.9–95.2) | 95.1 | 92.8 | 0.926 | 99.5 | 87.6 | 89.7 | 94.6 |
| LDA | 90.2 (87.4–93.1) | 93.5 | 90.7 | 0.900 | 98.6 | 85.6 | 85.2 | 93.3 |
| Decision tree (depth 4) | 88.9 (84.9–90.8) | 92.0 | 88.7 | 0.879 | 98.4 | 83.3 | 83.3 | 89.9 |
| Baseline: always the majority class | 25.0 | 51.3 | 17.0 | 0.000 | 67.8 | 0 | 0 | 0 |

BA, OA (overall accuracy) and F1 in %; BA, OA, F1 and kappa are means over 5 repeats; CI from the block bootstrap of the first repeat.

## E1: differences relative to Random Forest

| Model | ΔBA vs Random Forest (95% CI) | McNemar p |
|---|---|---|
| SVM (RBF) | +0.7 (−0.1 to +1.7) | 0.080 |
| Extra Trees | +0.5 (+0.0 to +1.1) | 0.155 |
| CatBoost | +0.7 (+0.2 to +1.3) | 0.009 |
| Logistic regression | +0.4 (−0.7 to +1.5) | 0.399 |
| MLP (64-32) | +0.8 (−0.4 to +2.0) | 0.005 |
| Maximum Likelihood (QDA) | +0.1 (−1.3 to +1.7) | 0.144 |
| k-NN (k=15) | +0.1 (−1.0 to +1.2) | 0.589 |
| XGBoost | +0.1 (−0.4 to +0.6) | 1 |
| LightGBM | −0.0 (−0.7 to +0.7) | 1 |
| HistGradientBoosting | +0.3 (−0.3 to +1.0) | 0.556 |
| LDA | −2.6 (−4.2 to −1.0) | 1.6 × 10⁻⁶ |
| Decision tree (depth 4) | −4.8 (−6.6 to −3.1) | 5.7 × 10⁻²³ |

ΔBA is computed on the first repeat, so it can differ slightly from the difference of the 5-repeat means in the table above. McNemar p-values are **optimistic**, because neighbouring cells are spatially correlated and not independent; the block-bootstrap CI is the more honest measure.

## E1: which classes get confused

![E1: confusion matrices of the top four models](/figures/en/E1_confusion_top4.png)

- **Vegetation ↔ Bare land** is the main confusion for every model, about 6–9% in each direction. Both are agricultural surfaces whose L-band backscatter overlaps (harvested fields, sparse crops, wet soil).
- **Built-up predicted as Vegetation** comes next (3–5%), plausibly villages with trees.
- **Water is almost never confused** (≈99% F1): calm water is very dark in both HH and HV.

## E1: training cost

Per fit on about 3,100 training samples: from 0.003 s (LDA) to 6.5 s (HistGradientBoosting); Random Forest 0.4 s, SVM 0.05 s, XGBoost 2.0 s, LightGBM 4.4 s, CatBoost 1.6 s. All models are cheap; cost is not a reason to choose between them.

## E1 conclusions

- **Model choice does not matter much.** The top 11 models are within 1 BA point and their CIs overlap.
- **The data are almost linearly separable** with these 12 features: logistic regression is as good as gradient boosting.
- **Random Forest is kept** for the production map ([Land-cover results](/results/landcover/)); SVM would be an equally valid choice.
- The ten best-behaved models are reused in [E7](/experiments/e7-map-agreement/) to measure how much their *maps* agree.
