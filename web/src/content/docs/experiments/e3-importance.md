---
title: "E3: Permutation importance of features"
description: Shuffling one SAR feature at a time on the test folds shows that HV on 27 October and the temporal standard deviation of HH carry the most information.
sidebar:
  order: 3
---

**Question.** Which individual SAR features does the Random Forest land-cover model rely on?

**Short answer.** HV on 27 Oct (the only ascending acquisition) is the most important feature: shuffling it lowers balanced accuracy (BA) by 6.7 points. Next come the standard deviation of HH across dates (−3.9), HV on 3 Nov (−3.2) and mean HV (−2.3). All other features are below 0.5 points.

## E3 setup

- **Model and validation:** Random Forest, 5 km spatial-block CV (as in [E1](/experiments/e1-models/)).
- **Method:** permutation importance computed **on the test folds** of the first CV repeat: for each of the 5 folds, train Random Forest on the training blocks, shuffle one feature in the test blocks (10 shuffles), re-predict, and measure the drop in BA. Values are the mean ± standard deviation across the 5 folds.

## E3 results

![E3: drop in balanced accuracy when each feature is shuffled](/figures/en/E3_permutation_importance.png)

| Feature | BA drop (points) |
|---|---|
| HV, 27 Oct (ascending) | 6.71 ± 3.32 |
| Standard deviation of HH across 3 dates | 3.89 ± 2.35 |
| HV, 3 Nov | 3.23 ± 1.18 |
| Mean HV | 2.34 ± 1.53 |
| HH, 22 Oct | 0.47 ± 0.52 |
| HV, 22 Oct | 0.41 ± 1.15 |
| Texture (7×7 std of mean HH) | 0.22 ± 0.31 |
| Standard deviation of HV across 3 dates | 0.21 ± 0.34 |
| HV − HH | 0.06 ± 0.20 |
| HH, 27 Oct | −0.04 ± 0.69 |
| Mean HH | −0.06 ± 0.69 |
| HH, 3 Nov | −0.14 ± 0.62 |

## E3: interpretation

- **HV dominates.** Three of the top four features are HV, consistent with [E2](/experiments/e2-features/), where HV alone outperforms HH alone.
- **The ascending acquisition is special.** HV on 27 Oct is the only feature from the ascending orbit (track 054), which looks at the ground from the opposite side. Building backscatter depends strongly on look direction, so the look-direction contrast may carry physical information about built-up areas. **This hypothesis has not been verified.**
- **Standard deviation of HH** ranks second. Because 27 Oct is ascending, this feature mixes look-direction differences with real change on the ground, so it should not be read as "temporal change" only.
- **Correlated features share importance.** HH on each date, mean HH and the HH standard deviation are strongly correlated; shuffling one leaves the others available, so their individual importance is small or slightly negative. This table must be read together with the group ablation in [E2](/experiments/e2-features/), which shows that removing *all* HH features costs about 4 points.

## E3 use elsewhere

The permutation importances are used as **feature weights** in the area-of-applicability analysis ([E8](/experiments/e8-applicability/)).
