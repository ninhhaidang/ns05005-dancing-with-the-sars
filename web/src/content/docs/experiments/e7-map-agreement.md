---
title: "E7: Do models produce the same map?"
description: Ten models trained on all samples and applied to the whole province agree on 65.9% of the area; their area shares are similar but not validated.
sidebar:
  order: 7
---

**Question.** Models that score the same on test samples ([E1](/experiments/e1-models/)) may still draw different maps. How much do the land-cover maps of different models agree, and how stable are the area shares?

**Short answer.** All 10 models predict the same class on **65.9%** of the AOI; only 3.0% of cells have 5 or fewer models agreeing with the majority. Area shares are fairly stable (Built-up 22–26%, Bare land 39–47%, excluding LDA), but **stable does not mean correct**: all models learn from the same labels.

## E7 setup

- **Models (10):** Random Forest, Extra Trees, HistGradientBoosting, XGBoost, LightGBM, CatBoost, MLP (64-32), logistic regression, LDA, Maximum Likelihood (QDA).
- **Training:** each model is trained on all 3,918 samples and predicts all 6.43 million 20 m cells of the AOI (2,571.7 km²).
- **Outputs:** per-model area shares, a pairwise agreement matrix, the **consensus map** (majority class over the 10 models) and the **agreement count** (how many models vote for the majority class, 3–10).

## E7: area shares by model

![E7: predicted area share of each class by model](/figures/en/E7_area_by_model.png)

| Model | Water | Vegetation | Bare land | Built-up |
|---|---|---|---|---|
| Random Forest | 5.1 | 25.1 | 45.7 | 24.1 |
| Extra Trees | 5.0 | 27.8 | 44.8 | 22.4 |
| HistGradientBoosting | 5.9 | 26.0 | 42.4 | 25.7 |
| XGBoost | 5.5 | 26.3 | 43.2 | 25.0 |
| LightGBM | 5.8 | 25.9 | 43.3 | 25.0 |
| CatBoost | 5.2 | 25.1 | 44.4 | 25.3 |
| MLP (64-32) | 6.2 | 22.6 | 46.5 | 24.8 |
| Logistic regression | 5.1 | 27.5 | 44.4 | 23.0 |
| LDA | 6.3 | 33.2 | 44.8 | 15.7 |
| Maximum Likelihood (QDA) | 6.2 | 29.1 | 38.7 | 25.9 |
| **Consensus (majority class)** | **5.6** | **26.8** | **43.6** | **24.0** |

Values are % of AOI area as predicted (pixel counting), **not bias-corrected and not validated**. Range across all 10 models: Water 5.0–6.3%, Vegetation 22.6–33.2%, Bare land 38.7–46.5%, Built-up 15.7–25.9%.

## E7: agreement between models

![E7: map of the number of models agreeing with the majority class](/figures/en/E7_agreement_map.png)

| Models agreeing with the majority class | 10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 |
|---|---|---|---|---|---|---|---|---|
| Share of AOI | 65.86% | 15.45% | 6.63% | 4.73% | 4.36% | 2.71% | 0.26% | < 0.01% |

![E7: pairwise agreement between models](/figures/en/E7_pairwise_agreement.png)

- **Tree-based and boosting models agree with each other on 88.7–96.8% of cells** (highest: XGBoost–LightGBM 96.8%, Random Forest–Extra Trees 95.3%).
- **LDA and QDA are the outliers:** they agree with the other models on only 78.8–85.6% (LDA) and 83.5–85.0% (QDA) of cells, and with each other on 75.5%.

## E7: interpretation

- **The map is robust where the models agree.** Two thirds of the province gets the same class from every model.
- **Area shares are stable but unvalidated.** A Built-up share of about 24% looks high for an agricultural delta province. One possible explanation is a class-definition mismatch: Built-up labels were dense building blocks, while the map's Built-up class may also capture villages with trees. This has not been checked against independent data.
- **Agreement measures model consensus, not correctness:** all models share the same label bias.

## E7 outputs used on the web map

- `landcover_model_mode.tif`: consensus land-cover map (majority of 10 models).
- `landcover_model_agreement.tif`: number of agreeing models, shown as a **confidence layer** on the [interactive map](/?view=confidence).

The production land-cover layer itself is the Random Forest map (see [Land-cover results](/results/landcover/)).
