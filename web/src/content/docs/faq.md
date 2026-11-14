---
title: Frequently asked questions
description: Short answers to the questions visitors and judges most often ask about the data, methods, accuracy and findings of the project NISAR L-band Change Detection and Land Cover Mapping.
sidebar:
  order: 4
---

## What is this project about?

**NISAR L-band Change Detection and Land Cover Mapping** is the entry of team 2936-ThanhNoi (NS05005) to the NASA Space Apps Challenge 2026, challenge *Dancing with the SARs*. It uses the first **VALIDATED NISAR** radar data to look at **Hưng Yên province, Vietnam** (the post-2025 province, formed by merging the former Hưng Yên and Thái Bình). It does two things: (1) detects changes linked to **water management** (fields, ponds, dykes) between 22 Oct and 3 Nov 2026, and (2) maps **four land-cover classes from SAR alone**. See the [Overview](/overview/).

## Who made this project?

Team **2936-ThanhNoi** (team ID **NS05005**) for NASA Space Apps Challenge 2026: **Ninh Hải Đăng** (team lead), **Phạm Minh Quang** and **Lê Toàn Thắng**. See [Team](/team/).

## Why use radar (SAR) instead of optical satellite images?

Because of clouds. Between 22 Oct and 3 Nov 2026 only about **32% of the province** had even one clear Sentinel-2 observation. SAR sends its own microwave pulses and sees through clouds day and night, so NISAR covers 100% of the province on every acquisition. NISAR's **L-band** (≈24 cm wavelength) also penetrates vegetation and is very sensitive to water surfaces.

## What is NISAR?

NISAR is the NASA–ISRO Synthetic Aperture Radar mission. This project uses its **GCOV** product (geocoded, terrain-corrected backscatter covariance) at frequency A with HH and HV polarisations. See [NISAR data](/data/nisar/).

## What does VALIDATED mean, and why only VALIDATED data?

NISAR products carry a maturity label. The project uses only products labelled **VALIDATED** (composite release ID **P05036**), available from 21 Oct 2026, and does not use earlier PROVISIONAL products. VALIDATED products still carry known issues listed by the provider. See [NISAR data](/data/nisar/).

## Why only three dates?

By design the project uses only VALIDATED GCOV data between **22 Oct and 3 Nov 2026**. Four acquisitions exist in that window: 22 Oct and 3 Nov (track 148, descending, 20 m), 27 Oct (track 054, ascending, 10 m), and 29 Oct (track 076), which covers only **4%** of the province and was dropped.

## Why 20 m pixels?

The two descending acquisitions are delivered at 20 m. The ascending 27 Oct acquisition is at 10 m and was averaged to 20 m so that all dates share one grid (UTM 48N, EPSG:32648; 6.43 million cells). See [Preprocessing](/methods/preprocessing/).

## What is the "new water" found near the river?

A cluster of about **1.6 km²** near **106.484°E, 20.463°N**, next to a river bend, where HH fell from about −10 to −16 dB and HV from about −17 to −23 dB between 22 Oct and 3 Nov, already partly on 27 Oct. A drop in both polarisations to these levels is typical of a rough surface turning into smooth water. Likely candidates are flooded fields, ponds being filled or an embanked area, but **the cause is not verified**. See [Change results](/results/change/) and the [map](/map/?view=change).

## Did anything else change?

Very little: **99.89%** of the province shows no significant change. 19 patches passed the test in total (1.58 km² new water, 0.38 km² other decreases, 0.58 km² increases, 0.16 km² HV-only increases). See [Change results](/results/change/).

## How accurate is the land-cover map?

We do not know the accuracy of the whole map. What we measured is **balanced accuracy ≈93%** (overall ≈95%) on **pure 20 m cells** under **5 km spatial-block cross-validation**. Accuracy is lower far from the labels (≈90% at 2–5 km) and on mixed cells, which were not tested. See [E1](/experiments/e1-models/) and [E4](/experiments/e4-validation/).

## Why is there no independent accuracy assessment?

A blind test set of 250 random cells was prepared, but it was not labelled within the project, so there is no independent check. All numbers are cross-validation. See [Limitations](/limitations/).

## What are "pure cells"?

20 m cells whose area lies at least 80% inside one label polygon of a single class. They are easier to classify than mixed cells (e.g. houses with gardens), so accuracy on pure cells is an upper bound for real-world accuracy.

## Which model makes the map?

A **Random Forest** (300 trees) on 12 SAR features: HH and HV on each date, their means, HV − HH, temporal standard deviations and texture. Fourteen models were compared and the top 11 were within 1 point of each other, so the model choice matters little ([E1](/experiments/e1-models/)).

## What matters most for accuracy?

Using **several dates** and **both polarisations**. One date gives 83–86% balanced accuracy, three dates 93%. Dropping HH or HV costs about 4 points. Texture adds almost nothing ([E2](/experiments/e2-features/)).

## Why is the Built-up class the least reliable?

Three reasons: 23.5% of Built-up predictions have SAR signatures unlike any training sample ([E8](/experiments/e8-applicability/)); almost all Built-up labels (618 of 625) are in the northern half of the province ([E4](/experiments/e4-validation/)); and models disagree most on its area (15.7–25.9%, [E7](/experiments/e7-map-agreement/)). Its ≈24% area share looks high for a farming province and is not validated.

## Is the area of each class reliable?

No. Area shares (Water ≈5%, Vegetation ≈25%, Bare land ≈44–46%, Built-up ≈24%) are pixel counts from the map, not validated and not bias-corrected. See [Land-cover results](/results/landcover/).

## How were the labels made?

The team drew **1,347 rectangles** in ArcGIS Pro on a cloud-masked Sentinel-2 composite (10 m) of the same period: Water 190, Vegetation 485, Bare land 444, Built-up 228. Sentinel-2 was used **only to draw labels**, never as model input. See [Labels](/data/labels/).

## Is Sentinel-2 used in the classifier?

No. The classifier uses **only NISAR SAR features**, so it works equally under cloud. Sentinel-2 served only as a visual reference for drawing labels. The [E8 analysis](/experiments/e8-applicability/) shows cloudy and clear areas are equally well covered by the training data in SAR feature space (8.3% vs 8.4% outside the area of applicability).

## Why not also use Sentinel-1?

The challenge focuses on NISAR, and the project's question is what NISAR alone can do. Sentinel-1 (C-band) within the same window could be added in future work but was not used here.

## Why was rice harvest not mapped?

No harvest signal appeared in the 12-day window; most fields seem to have been harvested before 22 Oct. Dynamic World covered only 6.2% of the province in the window, so it could not help either. See [Rice harvest](/results/rice-harvest/).

## What do the confidence layers on the map mean?

**Model agreement** is how many of 10 different models predict the same class (all 10 agree on 65.9% of the province). **Area of applicability** flags the 8.3% of cells whose SAR signature is far from every training sample. Both are indicators, not error maps. Open the [confidence view](/map/?view=confidence).

## Is the map on the website the same as the classifier output?

Almost: the web map shows the Random Forest map after a **3×3 majority filter** that removes isolated "salt-and-pepper" pixels. Its effect on accuracy has not been measured. See [Land-cover results](/results/landcover/).

## Can I get the data and reproduce the results?

The NISAR products are public from NASA's ASF DAAC (a free Earthdata login is needed). The project's scripts clip them to the province and rerun every step; see [Reproduce](/reproduce/).

## How long does it take to reproduce?

Training the main model takes minutes; the full experiment programme (E0–E8) takes about 35 minutes on an 8-core machine. Downloading the original NISAR files is the slowest part. See [Reproduce](/reproduce/).

## Can I trust the AI assistant's answers?

The assistant answers from this documentation and the project data and cites its sources, but it can still make mistakes. For important facts, check the linked page. Ask it [here](/chat/).
