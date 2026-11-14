---
title: Limitations
description: An explicit list of what this project did not or could not verify, covering the data, labels, accuracy figures, change detection and the web map.
sidebar:
  order: 2
---

This project works with brand-new NISAR data over a province that was under persistent cloud. The results are useful, but they must be read with the limitations below. We prefer to state them plainly rather than leave them implicit.

## Limitations of the data

- **Only three dates.** The project deliberately uses only NISAR GCOV products labelled **VALIDATED** (CRID P05036) in the window **22 Oct – 3 Nov 2026**: 22 Oct and 3 Nov (track 148, descending, 20 m) and 27 Oct (track 054, ascending, 10 m). A fourth acquisition (29 Oct, track 076) covered only 4% of the AOI and was dropped. Older PROVISIONAL products were not used.
- **Mixed geometries.** 27 Oct is ascending and the other two dates descending. This helps classification ([E2](/experiments/e2-features/)) but means only one same-geometry pair (22 Oct → 3 Nov) is available for change detection, and "temporal" features mix look-direction differences with real change.
- **20 m cells.** All analysis is on a 20 m grid (the 10 m acquisition was averaged to 20 m). Objects smaller than a few cells, such as narrow dykes, small ponds or single houses, are not resolved.
- **VALIDATED is not perfect.** VALIDATED products still carry known issues listed by the data provider; their possible effect on these results was not assessed.
- **Frequency B (80 m) was not used.**

## Limitations of the labels

- **Labels come from optical imagery of the same period,** drawn on a 12-day Sentinel-2 median composite. Only about 32% of the AOI had at least one clear observation, so labels exist only there.
- **Labels and acquisition dates do not match perfectly:** the ground changed within the 12 days (harvest, flooding), so some labels may not describe the surface on a given SAR date.
- **Clustered labels:** same-class polygons were drawn close together (median 102 m), and the 10 densest 5 km blocks hold 48% of the samples ([E0](/experiments/#e0-checking-the-spatial-distribution-of-labels)).
- **Uneven regional coverage:** 618 of 625 Built-up samples are in the northern half of the province ([E4](/experiments/e4-validation/)).
- **Small polygons discarded:** 483 of 1,347 polygons (36%), mostly vegetation, are too small to contain a pure 20 m cell.
- **Class definitions:** "Built-up" labels are dense building blocks, but the map's Built-up class may also include villages with trees.

## Limitations of the accuracy figures

- **No independent test set.** All accuracy numbers are cross-validation on labels drawn by the same team. A **blind test set of 250 random cells** was prepared in the clear-sky area, but **it was not labelled**, so it gives no result.
- **Pure cells only.** Accuracy is measured on 20 m cells lying ≥80% inside a single-class polygon. Mixed cells, which make up much of the real landscape, are not tested; accuracy there is certainly lower.
- **"≈93%" is not map accuracy.** It is balanced accuracy on pure cells under 5 km spatial-block CV. Accuracy falls to about 90% at 2–5 km from the labels, and 44% of the province is more than 2 km away ([E4](/experiments/e4-validation/)).
- **Area shares are not validated and not bias-corrected.** A design-based area estimate (Olofsson et al., 2014) would require a probability-sampled reference set, i.e. the unlabelled blind set.
- **Built-up is the least reliable class:** 23.5% of Built-up predictions are outside the model's area of applicability ([E8](/experiments/e8-applicability/)).

## Limitations of the change detection

- **One pair, 12 days.** Changes before 22 Oct or after 3 Nov are invisible.
- **Strict threshold:** |z| > 5 in both HH and HV and patches ≥ 0.05 km². Small or gradual changes are not reported.
- **Causes are unverified.** The new-water cluster near 106.484°E, 20.463°N and the other 18 patches have not been confirmed with optical, high-resolution or field data ([Change results](/results/change/)).
- **Rice harvest could not be studied:** most fields appear to have been harvested before the window ([Rice harvest](/results/rice-harvest/)).

## Limitations of the web map and assistant

- **The displayed land-cover layer is post-processed** with a 3×3 majority filter; the effect on accuracy is not measured.
- **Confidence layers are indicators, not error maps:** model agreement measures consensus between models that share the same labels; the dissimilarity index measures similarity to training data, not correctness.
- **The AI assistant** answers from this documentation and the project data. It can still make mistakes; check important claims against the cited pages.
