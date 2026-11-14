---
title: "E6: Hyperparameter tuning with nested CV"
description: Nested spatial cross-validation shows that tuning Random Forest, SVM and LightGBM changes balanced accuracy by at most half a point.
sidebar:
  order: 6
---

**Question.** Would tuning hyperparameters make the SAR land-cover classifiers meaningfully better?

**Short answer.** No. The largest gain is +0.5 points (SVM 93.6% → 94.1% balanced accuracy); Random Forest does not improve (92.9% → 92.8%).

## E6 setup

- **Nested cross-validation**, so that the tuning never sees the test blocks:
  - **Outer loop:** 5 km spatial-block CV (first repeat of the [E1](/experiments/e1-models/) folds).
  - **Inner loop:** 3-fold `GroupKFold` by 5 km block inside each outer training set; parameters are selected by balanced accuracy (BA).
- The "default" column is the model with its default settings on the same outer folds, so the two columns are directly comparable.

## E6 results

![E6: balanced accuracy with default versus tuned hyperparameters](/figures/en/E6_nested_tuning.png)

| Model | Default BA (%) | Tuned BA (%) | Search grid |
|---|---|---|---|
| Random Forest | 92.9 | 92.8 | `max_features` ∈ {√p, 0.5, 1}, `min_samples_leaf` ∈ {1, 2, 5} |
| SVM (RBF) | 93.6 | 94.1 | C ∈ {1, 10, 100}, γ ∈ {scale, 0.03, 0.3} |
| LightGBM | 92.9 | 93.1 | `num_leaves` ∈ {15, 31, 63}, `learning_rate` ∈ {0.03, 0.1} |

The Random Forest default here (92.9%) differs from the 93.1% in E1 because E6 uses only the first CV repeat, while E1 averages 5 repeats.

## E6: parameters chosen in each outer fold

| Model | Fold 1 | Fold 2 | Fold 3 | Fold 4 | Fold 5 |
|---|---|---|---|---|---|
| Random Forest | √p, leaf 5 | √p, leaf 1 | 0.5, leaf 5 | √p, leaf 2 | √p, leaf 5 |
| SVM (RBF) | C 1, γ scale | C 1, γ 0.03 | C 1, γ 0.3 | C 1, γ scale | C 1, γ 0.3 |
| LightGBM | lr 0.1, 31 leaves | lr 0.1, 31 leaves | lr 0.03, 15 leaves | lr 0.1, 15 leaves | lr 0.1, 63 leaves |

## E6: interpretation

- **Tuning barely helps** (at most 0.5 points), well inside the uncertainty of the E1 comparison.
- **SVM picks C = 1 in all 5 folds,** i.e. a smoother, less complex decision boundary than the default (C = 10) generalises slightly better across space.
- **Random Forest and LightGBM choose different parameters in different folds** with no gain, a sign that the accuracy surface is flat.
- The production map therefore keeps the default Random Forest (300 trees, `min_samples_leaf=2`, balanced class weights).
